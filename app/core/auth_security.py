"""
EchoSoul AI Platform Authentication Security
认证安全增强模块 - 防暴力破解和账户安全
"""

import time
import hashlib
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
import redis

from config.settings import settings
from app.models.user_models import AuthUser
from app.core.auth import verify_password

logger = logging.getLogger(__name__)

class LoginAttemptTracker:
    """登录尝试跟踪器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.memory_store: Dict[str, Dict] = {}
        
        # 配置参数
        self.max_attempts = settings.MAX_LOGIN_ATTEMPTS
        self.lockout_duration = settings.LOGIN_LOCKOUT_MINUTES * 60  # 转换为秒
        self.window_size = 15 * 60  # 15分钟窗口
    
    def _get_key(self, identifier: str) -> str:
        """获取Redis键名"""
        return f"login_attempts:{hashlib.md5(identifier.encode()).hexdigest()}"
    
    def _get_ip_key(self, ip: str) -> str:
        """获取IP限流键名"""
        return f"ip_rate_limit:{hashlib.md5(ip.encode()).hexdigest()}"
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            if "," in forwarded_for:
                return forwarded_for.split(",")[0].strip()
            return forwarded_for.strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _record_attempt_redis(self, key: str, success: bool) -> Tuple[bool, Dict]:
        """使用Redis记录登录尝试"""
        current_time = int(time.time())
        window_start = current_time - self.window_size
        
        try:
            pipe = self.redis_client.pipeline()
            
            # 清理过期记录
            pipe.zremrangebyscore(key, 0, window_start)
            
            # 获取当前窗口内的尝试次数
            pipe.zcard(key)
            
            # 添加当前尝试
            pipe.zadd(key, {str(current_time): current_time})
            
            # 设置过期时间
            pipe.expire(key, self.window_size + 60)
            
            results = pipe.execute()
            attempts_count = results[1]
            
            # 检查是否超过限制
            if attempts_count >= self.max_attempts:
                # 计算解锁时间
                unlock_time = current_time + self.lockout_duration
                
                return False, {
                    "locked": True,
                    "attempts": attempts_count,
                    "max_attempts": self.max_attempts,
                    "unlock_time": unlock_time,
                    "retry_after": self.lockout_duration
                }
            
            return True, {
                "locked": False,
                "attempts": attempts_count,
                "max_attempts": self.max_attempts,
                "remaining": self.max_attempts - attempts_count - 1
            }
            
        except Exception as e:
            logger.error(f"Redis login tracking error: {e}")
            return self._record_attempt_memory(key, success)
    
    def _record_attempt_memory(self, key: str, success: bool) -> Tuple[bool, Dict]:
        """使用内存记录登录尝试"""
        current_time = int(time.time())
        window_start = current_time - self.window_size
        
        if key not in self.memory_store:
            self.memory_store[key] = {
                "attempts": [],
                "last_cleanup": current_time
            }
        
        client_data = self.memory_store[key]
        
        # 定期清理过期数据
        if current_time - client_data["last_cleanup"] > 60:
            client_data["attempts"] = [
                attempt_time for attempt_time in client_data["attempts"]
                if attempt_time > window_start
            ]
            client_data["last_cleanup"] = current_time
        
        # 清理过期尝试
        client_data["attempts"] = [
            attempt_time for attempt_time in client_data["attempts"]
            if attempt_time > window_start
        ]
        
        # 检查是否超过限制
        if len(client_data["attempts"]) >= self.max_attempts:
            unlock_time = current_time + self.lockout_duration
            
            return False, {
                "locked": True,
                "attempts": len(client_data["attempts"]),
                "max_attempts": self.max_attempts,
                "unlock_time": unlock_time,
                "retry_after": self.lockout_duration
            }
        
        # 添加当前尝试
        client_data["attempts"].append(current_time)
        
        return True, {
            "locked": False,
            "attempts": len(client_data["attempts"]),
            "max_attempts": self.max_attempts,
            "remaining": self.max_attempts - len(client_data["attempts"])
        }
    
    def record_login_attempt(self, identifier: str, success: bool, request: Request) -> Tuple[bool, Dict]:
        """记录登录尝试"""
        key = self._get_key(identifier)
        
        if self.redis_client:
            return self._record_attempt_redis(key, success)
        else:
            return self._record_attempt_memory(key, success)
    
    def clear_attempts(self, identifier: str):
        """清除登录尝试记录"""
        key = self._get_key(identifier)
        
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis clear attempts error: {e}")
        else:
            self.memory_store.pop(key, None)

class AccountSecurityManager:
    """账户安全管理器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.login_tracker = LoginAttemptTracker(redis_client)
        self.redis_client = redis_client
    
    def check_login_security(self, username: str, password: str, request: Request, db: Session) -> Tuple[bool, Dict]:
        """检查登录安全性"""
        client_ip = self.login_tracker._get_client_ip(request)
        
        # 检查账户是否被锁定
        allowed, attempt_info = self.login_tracker.record_login_attempt(username, False, request)
        
        if not allowed:
            logger.warning(f"Account locked for user: {username}, IP: {client_ip}")
            return False, {
                "success": False,
                "message": "账户已被锁定，请稍后再试",
                "locked": True,
                "retry_after": attempt_info["retry_after"]
            }
        
        # 验证用户凭据
        user = db.query(AuthUser).filter(
            (AuthUser.username == username) | 
            (AuthUser.email == username) | 
            (AuthUser.mobile == username)
        ).first()
        
        if not user:
            logger.warning(f"Login attempt with non-existent user: {username}, IP: {client_ip}")
            return False, {
                "success": False,
                "message": "用户名或密码错误",
                "locked": False,
                "remaining_attempts": attempt_info["remaining"]
            }
        
        # 检查账户状态
        if user.status != 1:
            logger.warning(f"Login attempt with disabled account: {username}, IP: {client_ip}")
            return False, {
                "success": False,
                "message": "账户已被禁用",
                "locked": False,
                "remaining_attempts": attempt_info["remaining"]
            }
        
        # 验证密码
        if not verify_password(password, user.password):
            logger.warning(f"Failed login attempt for user: {username}, IP: {client_ip}")
            return False, {
                "success": False,
                "message": "用户名或密码错误",
                "locked": False,
                "remaining_attempts": attempt_info["remaining"]
            }
        
        # 登录成功，清除尝试记录
        self.login_tracker.clear_attempts(username)
        
        # 更新最后登录信息
        self._update_login_info(user, client_ip, db)
        
        logger.info(f"Successful login for user: {username}, IP: {client_ip}")
        
        return True, {
            "success": True,
            "message": "登录成功",
            "user": user,
            "locked": False
        }
    
    def _update_login_info(self, user: AuthUser, client_ip: str, db: Session):
        """更新登录信息"""
        try:
            user.last_login_time = datetime.utcnow()
            user.last_login_ip = client_ip
            db.commit()
        except Exception as e:
            logger.error(f"Failed to update login info: {e}")
            db.rollback()
    
    def check_password_strength(self, password: str) -> Tuple[bool, str]:
        """检查密码强度"""
        if len(password) < 6:
            return False, "密码长度至少6位"
        
        if len(password) > 20:
            return False, "密码长度不能超过20位"
        
        # 检查是否包含字母和数字
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        
        if not has_letter:
            return False, "密码必须包含字母"
        
        if not has_number:
            return False, "密码必须包含数字"
        
        # 检查常见弱密码
        weak_passwords = {
            "123456", "password", "123456789", "12345678", "12345",
            "1234567", "1234567890", "qwerty", "abc123", "111111",
            "123123", "admin", "letmein", "welcome", "monkey"
        }
        
        if password.lower() in weak_passwords:
            return False, "密码过于简单，请使用更复杂的密码"
        
        return True, "密码强度符合要求"
    
    def generate_secure_token(self, user_id: int) -> str:
        """生成安全令牌"""
        timestamp = str(int(time.time()))
        random_data = hashlib.sha256(f"{user_id}{timestamp}{settings.SECRET_KEY}".encode()).hexdigest()
        return f"{user_id}:{timestamp}:{random_data[:16]}"
    
    def validate_secure_token(self, token: str) -> Optional[int]:
        """验证安全令牌"""
        try:
            parts = token.split(":")
            if len(parts) != 3:
                return None
            
            user_id, timestamp, random_data = parts
            
            # 检查时间戳（令牌有效期1小时）
            token_time = int(timestamp)
            current_time = int(time.time())
            
            if current_time - token_time > 3600:  # 1小时过期
                return None
            
            # 验证随机数据
            expected_random = hashlib.sha256(f"{user_id}{timestamp}{settings.SECRET_KEY}".encode()).hexdigest()[:16]
            if random_data != expected_random:
                return None
            
            return int(user_id)
            
        except (ValueError, IndexError):
            return None

# 全局实例
account_security = AccountSecurityManager()
