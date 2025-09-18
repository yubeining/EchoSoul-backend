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
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]
    
    # Database
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "mysql")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
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
