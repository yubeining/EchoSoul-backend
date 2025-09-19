"""
EchoSoul AI Platform Constants
统一常量定义，避免重复代码
"""

import re
from typing import List

class SecurityPatterns:
    """安全相关正则表达式模式"""
    
    # SQL注入检测模式
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"][^'\"]*['\"]\s*=\s*['\"][^'\"]*['\"])",
        r"(\bUNION\s+SELECT\b)",
        r"(\bDROP\s+TABLE\b)",
        r"(\bINSERT\s+INTO\b)",
        r"(\bDELETE\s+FROM\b)",
        r"(\bUPDATE\s+SET\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bWAITFOR\s+DELAY\b)",
        r"(\bBENCHMARK\b)",
        r"(\bSLEEP\b)",
    ]
    
    # XSS检测模式
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<link[^>]*>.*?</link>",
        r"<meta[^>]*>.*?</meta>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onfocus\s*=",
        r"onblur\s*=",
        r"onchange\s*=",
        r"onsubmit\s*=",
        r"onreset\s*=",
        r"onselect\s*=",
        r"onkeydown\s*=",
        r"onkeyup\s*=",
        r"onkeypress\s*=",
        r"onmousedown\s*=",
        r"onmouseup\s*=",
        r"onmousemove\s*=",
        r"onmouseout\s*=",
        r"onmouseenter\s*=",
        r"onmouseleave\s*=",
        r"oncontextmenu\s*=",
        r"ondblclick\s*=",
        r"onabort\s*=",
        r"onbeforeunload\s*=",
        r"onerror\s*=",
        r"onhashchange\s*=",
        r"onload\s*=",
        r"onmessage\s*=",
        r"onoffline\s*=",
        r"ononline\s*=",
        r"onpagehide\s*=",
        r"onpageshow\s*=",
        r"onpopstate\s*=",
        r"onresize\s*=",
        r"onstorage\s*=",
        r"onunload\s*=",
    ]
    
    # 路径遍历攻击模式
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
    ]
    
    # 可疑User-Agent模式
    SUSPICIOUS_USER_AGENTS = [
        r"sqlmap",
        r"nikto",
        r"nmap",
        r"masscan",
        r"zap",
        r"burp",
        r"w3af",
        r"havij",
        r"acunetix",
        r"nessus",
        r"openvas",
        r"metasploit",
        r"cobalt",
        r"beef",
        r"xsser",
        r"commix",
        r"wpscan",
        r"joomscan",
        r"drupwn",
        r"droopescan",
        r"wascan",
        r"skipfish",
        r"dirb",
        r"dirbuster",
        r"gobuster",
        r"wfuzz",
        r"ffuf",
        r"feroxbuster",
        r"dirsearch",
        r"webdiscover",
        r"whatweb",
        r"wafw00f",
        r"uniscan",
        r"lbd",
        r"dnsrecon",
        r"fierce",
        r"dnsenum",
        r"dnsmap",
        r"dnswalk",
        r"dnsdict6",
    ]

class ValidationConstants:
    """验证相关常量"""
    
    # 邮箱正则表达式
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # 手机号正则表达式
    PHONE_REGEX = re.compile(r'^1[3-9]\d{9}$')
    
    # 用户名正则表达式
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
    
    # 保留用户名
    RESERVED_USERNAMES = {
        'admin', 'administrator', 'root', 'system', 'api', 'www', 'mail',
        'ftp', 'test', 'guest', 'user', 'support', 'help', 'info'
    }
    
    # 危险文件扩展名
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.php', '.asp', '.aspx', '.jsp', '.py', '.pl', '.sh',
        '.ps1', '.psm1', '.psd1', '.ps1xml', '.psc1', '.psc2'
    }
    
    # 允许的文件扩展名
    ALLOWED_FILE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx',
        '.txt', '.csv', '.xlsx', '.zip', '.rar'
    }
    
    # 允许的MIME类型
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'application/pdf',
        'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/zip', 'application/x-rar-compressed'
    }
    
    # 弱密码列表
    WEAK_PASSWORDS = {
        "123456", "password", "123456789", "12345678", "12345",
        "1234567", "1234567890", "qwerty", "abc123", "111111",
        "123123", "admin", "letmein", "welcome", "monkey"
    }

class RateLimitConfig:
    """限流配置常量"""
    
    # 默认限流配置
    DEFAULT_CONFIG = {
        "requests_per_minute": 60,
        "burst_size": 10,
        "window_size": 60  # 秒
    }
    
    # 认证接口限流配置
    AUTH_CONFIG = {
        "requests_per_minute": 10,
        "burst_size": 3,
        "window_size": 60
    }
    
    # API接口限流配置
    API_CONFIG = {
        "requests_per_minute": 100,
        "burst_size": 20,
        "window_size": 60
    }
    
    # 严格限流配置
    STRICT_CONFIG = {
        "requests_per_minute": 5,
        "burst_size": 2,
        "window_size": 60
    }

class SecurityConfig:
    """安全配置常量"""
    
    # 白名单IP
    WHITELIST_IPS = {
        "127.0.0.1",
        "::1",
        "localhost"
    }
    
    # 需要限流的路径
    LIMITED_PATHS = {
        "/api/",
        "/auth/",
        "/admin/",
        "/system/"
    }
    
    # 安全响应头
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'"
    }

class DatabaseConstants:
    """数据库相关常量"""
    
    # 数据库类型
    DATABASE_TYPES = {
        "mysql": "MySQL",
        "redis": "Redis", 
        "mongodb": "MongoDB"
    }
    
    # 连接池配置
    POOL_CONFIG = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 3600
    }

class APIResponseCodes:
    """API响应码常量"""
    
    SUCCESS = 1
    FAILURE = 0
    
    # HTTP状态码
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
