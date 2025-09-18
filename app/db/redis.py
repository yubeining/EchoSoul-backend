"""
Redis Database Implementation
Redis-specific cache operations (for future use)
"""

import redis
from typing import Optional, Dict, Any
import json
import logging

from app.db.base import CacheInterface
from config.database import DatabaseConfig

logger = logging.getLogger(__name__)

class RedisCache(CacheInterface):
    """Redis cache implementation"""
    
    def __init__(self):
        self.config = DatabaseConfig.get_database_config("redis")
        self.client = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to Redis"""
        try:
            self.client = redis.Redis(
                host=self.config["host"],
                port=self.config["port"],
                password=self.config["password"],
                db=self.config["db"],
                decode_responses=True
            )
            
            # Test connection
            self.client.ping()
            self.connected = True
            logger.info("Redis connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("Redis connection closed")
    
    def test_connection(self) -> tuple[bool, str]:
        """Test Redis connection"""
        try:
            if not self.client:
                return False, "Redis client not initialized"
            
            self.client.ping()
            return True, "Redis connection successful"
            
        except Exception as e:
            return False, f"Redis connection failed: {str(e)}"
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        try:
            if not self.connected:
                return None
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set key-value pair"""
        try:
            if not self.connected:
                return False
            
            if expire:
                self.client.setex(key, expire, value)
            else:
                self.client.set(key, value)
            return True
            
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key"""
        try:
            if not self.connected:
                return False
            
            result = self.client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            if not self.connected:
                return False
            
            return self.client.exists(key) > 0
            
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {str(e)}")
            return False
    
    def set_json(self, key: str, data: Dict[str, Any], expire: Optional[int] = None) -> bool:
        """Set JSON data"""
        try:
            json_data = json.dumps(data, ensure_ascii=False)
            return self.set(key, json_data, expire)
        except Exception as e:
            logger.error(f"Redis SET JSON error for key {key}: {str(e)}")
            return False
    
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON data"""
        try:
            data = self.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis GET JSON error for key {key}: {str(e)}")
            return None

# Global Redis cache instance
redis_cache = RedisCache()
