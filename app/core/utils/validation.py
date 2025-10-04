"""
EchoSoul AI Platform Input Validation
输入验证和安全检查模块
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, Field
import bleach

from app.core.utils.constants import SecurityPatterns, ValidationConstants

logger = logging.getLogger(__name__)

class SecureString(str):
    """安全字符串类型"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError('string required')
        
        # HTML转义
        v = html.escape(v, quote=True)
        
        # 移除危险字符
        v = cls._sanitize_string(v)
        
        return cls(v)
    
    @staticmethod
    def _sanitize_string(s: str) -> str:
        """清理字符串中的危险内容"""
        # 移除控制字符
        s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)
        
        # 移除SQL注入相关字符
        dangerous_patterns = SecurityPatterns.SQL_INJECTION_PATTERNS
        
        for pattern in dangerous_patterns:
            s = re.sub(pattern, '', s, flags=re.IGNORECASE)
        
        return s.strip()

class EmailValidator(str):
    """邮箱验证器"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError('string required')
        
        v = v.strip().lower()
        
        if not ValidationConstants.EMAIL_REGEX.match(v):
            raise ValueError('Invalid email format')
        
        # 检查邮箱长度
        if len(v) > 100:
            raise ValueError('Email too long')
        
        return cls(v)

class PhoneValidator(str):
    """手机号验证器"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError('string required')
        
        # 移除所有非数字字符
        v = re.sub(r'\D', '', v)
        
        if not ValidationConstants.PHONE_REGEX.match(v):
            raise ValueError('Invalid phone number format')
        
        return cls(v)

class PasswordValidator(str):
    """密码验证器"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError('string required')
        
        # 密码长度检查
        if len(v) < 6:
            raise ValueError('Password too short (minimum 6 characters)')
        
        if len(v) > 20:
            raise ValueError('Password too long (maximum 20 characters)')
        
        # 密码强度检查
        if not cls._check_password_strength(v):
            raise ValueError('Password must contain at least one letter and one number')
        
        return cls(v)
    
    @staticmethod
    def _check_password_strength(password: str) -> bool:
        """检查密码强度"""
        has_letter = bool(re.search(r'[a-zA-Z]', password))
        has_number = bool(re.search(r'\d', password))
        
        return has_letter and has_number

class UsernameValidator(str):
    """用户名验证器"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError('string required')
        
        v = v.strip()
        
        if not ValidationConstants.USERNAME_REGEX.match(v):
            raise ValueError('Username must be 3-20 characters long and contain only letters, numbers, and underscores')
        
        # 检查保留用户名
        if v.lower() in ValidationConstants.RESERVED_USERNAMES:
            raise ValueError('Username is reserved')
        
        return cls(v)

class HTMLSanitizer:
    """HTML内容清理器"""
    
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'b', 'i', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre'
    ]
    
    ALLOWED_ATTRIBUTES = {}
    
    @classmethod
    def sanitize(cls, content: str) -> str:
        """清理HTML内容"""
        if not content:
            return ""
        
        # 使用bleach清理HTML
        cleaned = bleach.clean(
            content,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        return cleaned

class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_json_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证JSON输入"""
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")
        
        # 检查数据大小
        json_str = str(data)
        if len(json_str) > 10000:  # 10KB限制
            raise ValueError("Input data too large")
        
        # 递归清理数据
        return InputValidator._clean_dict(data)
    
    @staticmethod
    def _clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """递归清理字典数据"""
        cleaned = {}
        
        for key, value in data.items():
            # 清理键名
            clean_key = SecureString.validate(key)
            
            # 清理值
            if isinstance(value, str):
                clean_value = SecureString.validate(value)
            elif isinstance(value, dict):
                clean_value = InputValidator._clean_dict(value)
            elif isinstance(value, list):
                clean_value = InputValidator._clean_list(value)
            else:
                clean_value = value
            
            cleaned[clean_key] = clean_value
        
        return cleaned
    
    @staticmethod
    def _clean_list(data: List[Any]) -> List[Any]:
        """递归清理列表数据"""
        cleaned = []
        
        for item in data:
            if isinstance(item, str):
                clean_item = SecureString.validate(item)
            elif isinstance(item, dict):
                clean_item = InputValidator._clean_dict(item)
            elif isinstance(item, list):
                clean_item = InputValidator._clean_list(item)
            else:
                clean_item = item
            
            cleaned.append(clean_item)
        
        return cleaned
    
    @staticmethod
    def validate_file_upload(filename: str, content_type: str, size: int) -> bool:
        """验证文件上传"""
        # 检查文件名
        if not filename or len(filename) > 255:
            return False
        
        # 检查文件大小 (10MB限制)
        if size > 10 * 1024 * 1024:
            return False
        
        # 检查文件扩展名
        filename_lower = filename.lower()
        if not any(filename_lower.endswith(ext) for ext in ValidationConstants.ALLOWED_FILE_EXTENSIONS):
            return False
        
        # 检查MIME类型
        if content_type not in ValidationConstants.ALLOWED_MIME_TYPES:
            return False
        
        return True

def detect_attack_patterns(content: str) -> List[str]:
    """检测攻击模式"""
    detected = []
    
    for pattern in SecurityPatterns.SQL_INJECTION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            detected.append("sql_injection")
            break
    
    for pattern in SecurityPatterns.XSS_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            detected.append("xss")
            break
    
    for pattern in SecurityPatterns.PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            detected.append("path_traversal")
            break
    
    return detected

# 便捷验证函数
def validate_email(email: str) -> str:
    """验证邮箱格式"""
    validator = EmailValidator()
    return validator.validate(email)

def validate_password(password: str) -> str:
    """验证密码强度"""
    validator = PasswordValidator()
    return validator.validate(password)

def validate_username(username: str) -> str:
    """验证用户名格式"""
    validator = UsernameValidator()
    return validator.validate(username)
