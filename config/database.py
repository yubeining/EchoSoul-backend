"""
Database Configuration
Centralized database configuration for different database types
"""

import os
from typing import Dict, Any

class DatabaseConfig:
    """Database configuration class"""
    
    # MySQL Configuration
    MYSQL_HOST = "echosoul-mysql-mysql.ns-7rdhhsv1.svc"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "kzmtbc6b"
    MYSQL_DATABASE = "EchoSoul"
    
    # Redis Configuration (for future use)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    # MongoDB Configuration (for future use)
    MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))
    MONGODB_USER = os.getenv("MONGODB_USER", None)
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", None)
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "echosoul")
    
    @classmethod
    def get_mysql_url(cls) -> str:
        """Get MySQL connection URL"""
        return f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}"
    
    @classmethod
    def get_mysql_database_url(cls) -> str:
        """Get MySQL database connection URL"""
        return f"{cls.get_mysql_url()}/{cls.MYSQL_DATABASE}"
    
    @classmethod
    def get_redis_url(cls) -> str:
        """Get Redis connection URL"""
        auth = f":{cls.REDIS_PASSWORD}@" if cls.REDIS_PASSWORD else ""
        return f"redis://{auth}{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
    
    @classmethod
    def get_mongodb_url(cls) -> str:
        """Get MongoDB connection URL"""
        auth = f"{cls.MONGODB_USER}:{cls.MONGODB_PASSWORD}@" if cls.MONGODB_USER else ""
        return f"mongodb://{auth}{cls.MONGODB_HOST}:{cls.MONGODB_PORT}/{cls.MONGODB_DATABASE}"
    
    @classmethod
    def get_database_config(cls, db_type: str = "mysql") -> Dict[str, Any]:
        """Get database configuration by type"""
        configs = {
            "mysql": {
                "url": cls.get_mysql_database_url(),
                "server_url": cls.get_mysql_url(),
                "host": cls.MYSQL_HOST,
                "port": cls.MYSQL_PORT,
                "user": cls.MYSQL_USER,
                "password": cls.MYSQL_PASSWORD,
                "database": cls.MYSQL_DATABASE
            },
            "redis": {
                "url": cls.get_redis_url(),
                "host": cls.REDIS_HOST,
                "port": cls.REDIS_PORT,
                "password": cls.REDIS_PASSWORD,
                "db": cls.REDIS_DB
            },
            "mongodb": {
                "url": cls.get_mongodb_url(),
                "host": cls.MONGODB_HOST,
                "port": cls.MONGODB_PORT,
                "user": cls.MONGODB_USER,
                "password": cls.MONGODB_PASSWORD,
                "database": cls.MONGODB_DATABASE
            }
        }
        return configs.get(db_type, configs["mysql"])
