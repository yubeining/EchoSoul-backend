"""
Application Settings
Centralized application configuration
"""

import os
from typing import List

class Settings:
    """Application settings"""
    
    # Application
    APP_NAME = "EchoSoul AI Platform Backend Service"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8080))
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://echosoul.com,https://cedezmdpgixn.sealosbja.site,https://ohciuodbxwdp.sealosbja.site").split(",")
    
    # Database
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "mysql")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    # JWT Security
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REDIS_URL = os.getenv("RATE_LIMIT_REDIS_URL", None)
    
    # Security Settings
    SECURITY_ENABLED = os.getenv("SECURITY_ENABLED", "true").lower() == "true"
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
    LOGIN_LOCKOUT_MINUTES = int(os.getenv("LOGIN_LOCKOUT_MINUTES", 15))
    
    # CORS Security
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = [
        "Content-Type",
        "Authorization", 
        "X-Requested-With",
        "Accept",
        "Origin"
    ]
    CORS_MAX_AGE = 86400
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # API Documentation
    DOCS_URL = "/docs"
    REDOC_URL = "/redoc"
    
    # Pagination
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Get CORS origins list"""
        if cls.CORS_ORIGINS == ["*"]:
            return ["*"]
        return [origin.strip() for origin in cls.CORS_ORIGINS if origin.strip()]

# Global settings instance
settings = Settings()
