"""
EchoSoul AI Platform Rate Limiter Middleware
API限流中间件 - 防止恶意流量攻击
"""

import time
import json
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis
import hashlib
import logging

from config.settings import settings
from app.core.constants import RateLimitConfig, SecurityConfig

logger = logging.getLogger(__name__)

class RateLimiter:
    """限流器类"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.memory_store: Dict[str, Dict] = {}
        
        # 限流配置
        self.configs = {
            "default": RateLimitConfig.DEFAULT_CONFIG,
            "auth": RateLimitConfig.AUTH_CONFIG,
            "api": RateLimitConfig.API_CONFIG,
            "strict": RateLimitConfig.STRICT_CONFIG
        }
    
    def _get_client_key(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用真实IP
        client_ip = request.headers.get("x-forwarded-for")
        if not client_ip:
            client_ip = request.headers.get("x-real-ip")
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"
        
        # 处理多个IP的情况
        if "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        
        return f"rate_limit:{client_ip}"
    
    def _get_route_config(self, path: str) -> Dict:
        """根据路径获取限流配置"""
        if "/auth/login" in path or "/auth/register" in path:
            return self.configs["auth"]
        elif "/api/" in path:
            return self.configs["api"]
        elif "/admin/" in path or "/system/" in path:
            return self.configs["strict"]
        else:
            return self.configs["default"]
    
    def _sliding_window_check(self, key: str, config: Dict) -> Tuple[bool, Dict]:
        """滑动窗口限流检查"""
        current_time = int(time.time())
        window_size = config["window_size"]
        max_requests = config["requests_per_minute"]
        burst_size = config["burst_size"]
        
        # 清理过期数据
        cutoff_time = current_time - window_size
        
        if self.redis_client:
            # 使用Redis实现分布式限流
            try:
                # 使用Redis的sorted set实现滑动窗口
                pipe = self.redis_client.pipeline()
                
                # 清理过期记录
                pipe.zremrangebyscore(key, 0, cutoff_time)
                
                # 获取当前窗口内的请求数
                pipe.zcard(key)
                
                # 添加当前请求
                pipe.zadd(key, {str(current_time): current_time})
                
                # 设置过期时间
                pipe.expire(key, window_size + 10)
                
                results = pipe.execute()
                current_requests = results[1]
                
                # 检查是否超过限制
                if current_requests >= max_requests:
                    return False, {
                        "limit": max_requests,
                        "remaining": 0,
                        "reset_time": current_time + window_size,
                        "retry_after": window_size
                    }
                
                return True, {
                    "limit": max_requests,
                    "remaining": max_requests - current_requests - 1,
                    "reset_time": current_time + window_size,
                    "retry_after": 0
                }
                
            except Exception as e:
                logger.error(f"Redis rate limiting error: {e}")
                # Redis失败时降级到内存限流
                return self._memory_rate_limit(key, config)
        else:
            # 内存限流
            return self._memory_rate_limit(key, config)
    
    def _memory_rate_limit(self, key: str, config: Dict) -> Tuple[bool, Dict]:
        """内存限流实现"""
        current_time = int(time.time())
        window_size = config["window_size"]
        max_requests = config["requests_per_minute"]
        
        if key not in self.memory_store:
            self.memory_store[key] = {
                "requests": [],
                "last_cleanup": current_time
            }
        
        client_data = self.memory_store[key]
        
        # 定期清理过期数据
        if current_time - client_data["last_cleanup"] > 60:
            client_data["requests"] = [
                req_time for req_time in client_data["requests"]
                if current_time - req_time < window_size
            ]
            client_data["last_cleanup"] = current_time
        
        # 清理过期请求
        cutoff_time = current_time - window_size
        client_data["requests"] = [
            req_time for req_time in client_data["requests"]
            if req_time > cutoff_time
        ]
        
        # 检查是否超过限制
        if len(client_data["requests"]) >= max_requests:
            return False, {
                "limit": max_requests,
                "remaining": 0,
                "reset_time": current_time + window_size,
                "retry_after": window_size
            }
        
        # 添加当前请求
        client_data["requests"].append(current_time)
        
        return True, {
            "limit": max_requests,
            "remaining": max_requests - len(client_data["requests"]),
            "reset_time": current_time + window_size,
            "retry_after": 0
        }
    
    def check_rate_limit(self, request: Request) -> Tuple[bool, Dict]:
        """检查限流"""
        client_key = self._get_client_key(request)
        route_config = self._get_route_config(str(request.url.path))
        
        return self._sliding_window_check(client_key, route_config)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.rate_limiter = RateLimiter(redis_client)
        
        # 白名单IP (管理后台等)
        self.whitelist_ips = SecurityConfig.WHITELIST_IPS.copy()
        
        # 需要限流的路径
        self.limited_paths = SecurityConfig.LIMITED_PATHS.copy()
    
    def _is_whitelisted(self, request: Request) -> bool:
        """检查是否在白名单中"""
        client_ip = request.headers.get("x-forwarded-for")
        if not client_ip:
            client_ip = request.headers.get("x-real-ip")
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"
        
        if "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        
        return client_ip in self.whitelist_ips
    
    def _should_limit(self, request: Request) -> bool:
        """判断是否需要限流"""
        path = str(request.url.path)
        
        # 白名单IP不限流
        if self._is_whitelisted(request):
            return False
        
        # 只对特定路径限流
        return any(path.startswith(limited_path) for limited_path in self.limited_paths)
    
    async def dispatch(self, request: Request, call_next):
        """中间件处理逻辑"""
        
        # 检查是否需要限流
        if not self._should_limit(request):
            return await call_next(request)
        
        # 执行限流检查
        allowed, rate_info = self.rate_limiter.check_rate_limit(request)
        
        if not allowed:
            # 记录限流事件
            client_ip = request.headers.get("x-forwarded-for", 
                                          request.headers.get("x-real-ip", 
                                          request.client.host if request.client else "unknown"))
            
            logger.warning(f"Rate limit exceeded for IP: {client_ip}, Path: {request.url.path}")
            
            # 返回限流响应
            response_data = {
                "code": 0,
                "msg": "请求过于频繁，请稍后再试",
                "data": None,
                "rate_limit_info": {
                    "limit": rate_info["limit"],
                    "remaining": rate_info["remaining"],
                    "reset_time": rate_info["reset_time"],
                    "retry_after": rate_info["retry_after"]
                }
            }
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=response_data
            )
            
            # 添加限流响应头
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset_time"])
            response.headers["Retry-After"] = str(rate_info["retry_after"])
            
            return response
        
        # 添加限流信息到响应头
        response = await call_next(request)
        
        if hasattr(response, 'headers'):
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset_time"])
        
        return response


def create_rate_limit_middleware(redis_client: Optional[redis.Redis] = None):
    """创建限流中间件"""
    return lambda app: RateLimitMiddleware(app, redis_client)
