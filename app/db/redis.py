"""
Redis Database Implementation
Enhanced Redis cache operations with comprehensive functionality
"""

import redis
from typing import Optional, Dict, Any, List, Union
import json
import logging
from datetime import datetime, timedelta

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
            # 使用连接URL方式连接（更可靠）
            redis_url = self.config["url"]
            logger.info(f"Connecting to Redis: {redis_url}")
            
            self.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=10,
                socket_timeout=10,
                retry_on_timeout=True,
                health_check_interval=30
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
    
    # ==================== 高级功能 ====================
    
    def set_with_ttl(self, key: str, value: str, ttl_seconds: int) -> bool:
        """设置带过期时间的键值对"""
        try:
            if not self.connected:
                return False
            
            self.client.setex(key, ttl_seconds, value)
            logger.debug(f"Set key {key} with TTL {ttl_seconds}s")
            return True
            
        except Exception as e:
            logger.error(f"Redis SETEX error for key {key}: {str(e)}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """递增计数器"""
        try:
            if not self.connected:
                return None
            
            result = self.client.incrby(key, amount)
            logger.debug(f"Incremented key {key} by {amount}, new value: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Redis INCRBY error for key {key}: {str(e)}")
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """递减计数器"""
        try:
            if not self.connected:
                return None
            
            result = self.client.decrby(key, amount)
            logger.debug(f"Decremented key {key} by {amount}, new value: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Redis DECRBY error for key {key}: {str(e)}")
            return None
    
    def set_hash(self, name: str, mapping: Dict[str, Any]) -> bool:
        """设置哈希表"""
        try:
            if not self.connected:
                return False
            
            # 序列化复杂对象
            processed_mapping = {}
            for key, value in mapping.items():
                if isinstance(value, (dict, list)):
                    processed_mapping[key] = json.dumps(value, ensure_ascii=False)
                else:
                    processed_mapping[key] = str(value)
            
            result = self.client.hset(name, mapping=processed_mapping)
            logger.debug(f"Set hash {name} with {len(mapping)} fields")
            return result >= 0
            
        except Exception as e:
            logger.error(f"Redis HSET error for hash {name}: {str(e)}")
            return False
    
    def get_hash(self, name: str, key: Optional[str] = None) -> Union[Dict[str, Any], Optional[Any]]:
        """获取哈希表数据"""
        try:
            if not self.connected:
                return {} if key is None else None
            
            if key:
                # 获取单个字段
                value = self.client.hget(name, key)
                if value is None:
                    return None
                
                # 尝试反序列化JSON
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            else:
                # 获取所有字段
                result = self.client.hgetall(name)
                processed_result = {}
                for k, v in result.items():
                    try:
                        processed_result[k] = json.loads(v)
                    except (json.JSONDecodeError, TypeError):
                        processed_result[k] = v
                return processed_result
                
        except Exception as e:
            logger.error(f"Redis HGET error for hash {name}: {str(e)}")
            return {} if key is None else None
    
    def push_to_list(self, name: str, *values: Any, left: bool = False) -> Optional[int]:
        """向列表添加元素"""
        try:
            if not self.connected:
                return None
            
            processed_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    processed_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    processed_values.append(str(value))
            
            if left:
                result = self.client.lpush(name, *processed_values)
            else:
                result = self.client.rpush(name, *processed_values)
            
            logger.debug(f"Pushed {len(values)} values to list {name}")
            return result
            
        except Exception as e:
            logger.error(f"Redis LIST push error for {name}: {str(e)}")
            return None
    
    def pop_from_list(self, name: str, left: bool = False, count: int = 1) -> Union[Any, List[Any], None]:
        """从列表弹出元素"""
        try:
            if not self.connected:
                return None
            
            if left:
                if count == 1:
                    result = self.client.lpop(name)
                else:
                    result = self.client.lpop(name, count)
            else:
                if count == 1:
                    result = self.client.rpop(name)
                else:
                    result = self.client.rpop(name, count)
            
            if result is None:
                return None
            
            # 尝试反序列化JSON
            if isinstance(result, list):
                processed_result = []
                for item in result:
                    try:
                        processed_result.append(json.loads(item))
                    except (json.JSONDecodeError, TypeError):
                        processed_result.append(item)
                return processed_result
            else:
                try:
                    return json.loads(result)
                except (json.JSONDecodeError, TypeError):
                    return result
                    
        except Exception as e:
            logger.error(f"Redis LIST pop error for {name}: {str(e)}")
            return None
    
    def add_to_set(self, name: str, *values: Any) -> Optional[int]:
        """向集合添加元素"""
        try:
            if not self.connected:
                return None
            
            processed_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    processed_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    processed_values.append(str(value))
            
            result = self.client.sadd(name, *processed_values)
            logger.debug(f"Added {len(values)} values to set {name}")
            return result
            
        except Exception as e:
            logger.error(f"Redis SADD error for set {name}: {str(e)}")
            return None
    
    def get_set_members(self, name: str) -> set:
        """获取集合成员"""
        try:
            if not self.connected:
                return set()
            
            result = self.client.smembers(name)
            processed_result = set()
            for item in result:
                try:
                    processed_result.add(json.loads(item))
                except (json.JSONDecodeError, TypeError):
                    processed_result.add(item)
            
            return processed_result
            
        except Exception as e:
            logger.error(f"Redis SMEMBERS error for set {name}: {str(e)}")
            return set()
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键列表"""
        try:
            if not self.connected:
                return []
            
            return self.client.keys(pattern)
            
        except Exception as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {str(e)}")
            return []
    
    def get_redis_info(self) -> Dict[str, Any]:
        """获取Redis服务器信息"""
        try:
            if not self.connected:
                return {}
            
            return self.client.info()
            
        except Exception as e:
            logger.error(f"Redis INFO error: {str(e)}")
            return {}
    
    def flush_database(self) -> bool:
        """清空当前数据库"""
        try:
            if not self.connected:
                return False
            
            result = self.client.flushdb()
            logger.warning("Flushed Redis database")
            return result
            
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {str(e)}")
            return False
    
    # ==================== 缓存模式方法 ====================
    
    def cache_with_fallback(self, key: str, fetch_func, ttl_seconds: int = 300, *args, **kwargs) -> Any:
        """
        缓存模式：先查缓存，未命中则调用函数获取数据并缓存
        
        Args:
            key: 缓存键
            fetch_func: 数据获取函数
            ttl_seconds: 缓存过期时间（秒）
            *args, **kwargs: 传递给fetch_func的参数
        
        Returns:
            缓存的数据或函数返回的数据
        """
        try:
            # 尝试从缓存获取
            cached_data = self.get_json(key)
            if cached_data is not None:
                logger.debug(f"Cache hit for key {key}")
                return cached_data
            
            # 缓存未命中，调用函数获取数据
            logger.debug(f"Cache miss for key {key}, calling fetch function")
            data = fetch_func(*args, **kwargs)
            
            # 存入缓存
            if data is not None:
                self.set_json(key, data, ttl_seconds)
                logger.debug(f"Cached data for key {key}")
            
            return data
            
        except Exception as e:
            logger.error(f"Cache with fallback error for key {key}: {str(e)}")
            # 发生错误时，直接调用函数获取数据
            try:
                return fetch_func(*args, **kwargs)
            except Exception as fetch_error:
                logger.error(f"Fetch function error: {str(fetch_error)}")
                return None

# Global Redis cache instance
redis_cache = RedisCache()
