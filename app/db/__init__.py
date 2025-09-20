"""
Database Package
Database initialization and management
"""

from app.db.mysql import mysql_db
from app.db.redis import redis_cache
from config.settings import settings

def initialize_databases():
    """Initialize all databases based on configuration"""
    results = {}
    
    # Initialize MySQL (primary database)
    if mysql_db.connect():
        results["mysql"] = {"status": "connected", "message": "MySQL connected successfully"}
    else:
        results["mysql"] = {"status": "failed", "message": "MySQL connection failed"}
    
    # Initialize Redis (if configured)
    if settings.DATABASE_TYPE == "redis" or settings.DEBUG:
        if redis_cache.connect():
            results["redis"] = {"status": "connected", "message": "Redis connected successfully"}
        else:
            results["redis"] = {"status": "failed", "message": "Redis connection failed"}
    
    # MongoDB support removed - using MySQL and Redis only
    
    return results

def get_database_session():
    """Get database session for dependency injection"""
    session = mysql_db.get_session()
    try:
        yield session
    finally:
        session.close()

def get_database_base():
    """Get database base class"""
    return mysql_db.get_base()

# Export main database instances
__all__ = [
    "mysql_db",
    "redis_cache", 
    "initialize_databases",
    "get_database_session",
    "get_database_base"
]
