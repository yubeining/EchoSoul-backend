"""
EchoSoul AI Platform Security Middleware
安全中间件 - 综合安全防护
"""

import time
import re
import json
import hashlib
import logging
from typing import Dict, List, Optional, Set
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from urllib.parse import urlparse, parse_qs

from app.core.utils.constants import SecurityPatterns, SecurityConfig

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # SQL注入检测模式
        self.sql_patterns = SecurityPatterns.SQL_INJECTION_PATTERNS
        
        # XSS检测模式
        self.xss_patterns = SecurityPatterns.XSS_PATTERNS
        
        # 危险文件扩展名
        self.dangerous_extensions = SecurityPatterns.DANGEROUS_EXTENSIONS
        
        # 可疑User-Agent模式
        self.suspicious_user_agents = SecurityPatterns.SUSPICIOUS_USER_AGENTS
        
        # 黑名单IP (可以动态更新)
        self.blacklist_ips: Set[str] = set()
        
        # 白名单IP
        self.whitelist_ips: Set[str] = SecurityConfig.WHITELIST_IPS.copy()
        
        # 安全事件统计
        self.security_stats = {
            "sql_injection_attempts": 0,
            "xss_attempts": 0,
            "suspicious_user_agents": 0,
            "blacklisted_ips": 0,
            "total_blocked": 0
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP"""
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # 处理多个IP的情况
            if "," in forwarded_for:
                return forwarded_for.split(",")[0].strip()
            return forwarded_for.strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # 直接连接IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_blacklisted(self, client_ip: str) -> bool:
        """检查IP是否在黑名单中"""
        return client_ip in self.blacklist_ips
    
    def _is_whitelisted(self, client_ip: str) -> bool:
        """检查IP是否在白名单中"""
        return client_ip in self.whitelist_ips
    
    def _detect_sql_injection(self, content: str) -> bool:
        """检测SQL注入攻击"""
        content_lower = content.lower()
        
        for pattern in self.sql_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_xss(self, content: str) -> bool:
        """检测XSS攻击"""
        for pattern in self.xss_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_suspicious_user_agent(self, user_agent: str) -> bool:
        """检测可疑User-Agent"""
        user_agent_lower = user_agent.lower()
        
        for pattern in self.suspicious_user_agents:
            if re.search(pattern, user_agent_lower):
                return True
        
        return False
    
    def _detect_dangerous_file_upload(self, filename: str) -> bool:
        """检测危险文件上传"""
        if not filename:
            return False
        
        filename_lower = filename.lower()
        
        # 检查文件扩展名
        for ext in self.dangerous_extensions:
            if filename_lower.endswith(ext):
                return True
        
        # 检查双扩展名攻击
        if filename_lower.count('.') > 1:
            return True
        
        return False
    
    def _log_security_event(self, event_type: str, client_ip: str, details: Dict):
        """记录安全事件"""
        self.security_stats[event_type] += 1
        self.security_stats["total_blocked"] += 1
        
        log_data = {
            "timestamp": time.time(),
            "event_type": event_type,
            "client_ip": client_ip,
            "details": details
        }
        
        logger.warning(f"Security event: {json.dumps(log_data)}")
    
    def _block_request(self, request: Request, reason: str, event_type: str) -> JSONResponse:
        """阻止请求"""
        client_ip = self._get_client_ip(request)
        
        # 记录安全事件
        self._log_security_event(event_type, client_ip, {
            "reason": reason,
            "path": str(request.url.path),
            "method": request.method,
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", "")
        })
        
        # 返回错误响应
        response_data = {
            "code": 0,
            "msg": "请求被安全系统拦截",
            "data": None,
            "security_info": {
                "reason": reason,
                "timestamp": int(time.time())
            }
        }
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=response_data
        )
    
    async def dispatch(self, request: Request, call_next):
        """中间件处理逻辑"""
        try:
            client_ip = self._get_client_ip(request)
        except Exception as e:
            logger.error(f"Error in security middleware: {e}")
            return await call_next(request)
        
        try:
            # 白名单IP直接通过
            if self._is_whitelisted(client_ip):
                return await call_next(request)
            
            # 检查黑名单IP
            if self._is_blacklisted(client_ip):
                return self._block_request(request, "IP在黑名单中", "blacklisted_ips")
            
            # 检查User-Agent
            user_agent = request.headers.get("user-agent", "")
            if user_agent and self._detect_suspicious_user_agent(user_agent):
                return self._block_request(request, "可疑的User-Agent", "suspicious_user_agents")
            
            # 检查请求参数
            # 检查URL参数
            if request.query_params:
                query_string = str(request.url.query)
                if self._detect_sql_injection(query_string):
                    return self._block_request(request, "检测到SQL注入攻击", "sql_injection_attempts")
                
                if self._detect_xss(query_string):
                    return self._block_request(request, "检测到XSS攻击", "xss_attempts")
            
            # 检查请求体 (仅对POST/PUT请求)
            if request.method in ["POST", "PUT", "PATCH"]:
                # 获取请求体内容
                body = await request.body()
                if body:
                    try:
                        # 尝试解析JSON
                        body_str = body.decode('utf-8')
                        json.loads(body_str)  # 验证JSON格式
                        
                        # 检查SQL注入
                        if self._detect_sql_injection(body_str):
                            return self._block_request(request, "请求体中检测到SQL注入攻击", "sql_injection_attempts")
                        
                        # 检查XSS
                        if self._detect_xss(body_str):
                            return self._block_request(request, "请求体中检测到XSS攻击", "xss_attempts")
                    
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # 非JSON内容，直接检查
                        body_str = body.decode('utf-8', errors='ignore')
                        if self._detect_sql_injection(body_str):
                            return self._block_request(request, "请求体中检测到SQL注入攻击", "sql_injection_attempts")
                        
                        if self._detect_xss(body_str):
                            return self._block_request(request, "请求体中检测到XSS攻击", "xss_attempts")
            
            # 检查文件上传
            if request.method == "POST":
                content_type = request.headers.get("content-type", "")
                if "multipart/form-data" in content_type:
                    # 这里可以添加文件上传安全检查
                    pass
        
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            # 发生错误时记录但不阻止请求
        
        # 继续处理请求
        response = await call_next(request)
        
        # 添加安全响应头
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        return response
    
    def add_to_blacklist(self, ip: str):
        """添加IP到黑名单"""
        self.blacklist_ips.add(ip)
        logger.info(f"Added IP {ip} to blacklist")
    
    def remove_from_blacklist(self, ip: str):
        """从黑名单移除IP"""
        self.blacklist_ips.discard(ip)
        logger.info(f"Removed IP {ip} from blacklist")
    
    def get_security_stats(self) -> Dict:
        """获取安全统计信息"""
        return self.security_stats.copy()
