"""
缓存管理器
提供统一的缓存管理，提高性能
"""

import json
import time
import hashlib
from typing import Any, Optional, Dict, Union
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, default_ttl: int = 300):  # 默认5分钟过期
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": sorted(kwargs.items()) if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """检查缓存是否过期"""
        if "expires_at" not in cache_entry:
            return True
        return datetime.utcnow() > cache_entry["expires_at"]
    
    def _cleanup_expired(self):
        """清理过期的缓存项"""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if "expires_at" in entry and current_time > entry["expires_at"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            self.stats["deletes"] += 1
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        cache_entry = self.cache[key]
        
        if self._is_expired(cache_entry):
            del self.cache[key]
            self.stats["misses"] += 1
            self.stats["deletes"] += 1
            return None
        
        self.stats["hits"] += 1
        return cache_entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        
        self.stats["sets"] += 1
        return True
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        if key in self.cache:
            del self.cache[key]
            self.stats["deletes"] += 1
            return True
        return False
    
    def clear(self):
        """清空所有缓存"""
        self.cache.clear()
        self.stats["deletes"] += len(self.cache)
    
    def get_or_set(self, key: str, func, ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """获取缓存值，如果不存在则设置"""
        value = self.get(key)
        if value is not None:
            return value
        
        # 缓存未命中，执行函数获取值
        value = func(*args, **kwargs)
        self.set(key, value, ttl)
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            "hit_rate": round(hit_rate, 2),
            "cache_size": len(self.cache),
            "total_requests": total_requests
        }
    
    def cleanup(self):
        """清理过期缓存"""
        self._cleanup_expired()

# 全局缓存管理器实例
cache_manager = CacheManager()

# 缓存装饰器
def cached(ttl: int = 300, key_prefix: str = "default"):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cache_manager._generate_key(
                f"{key_prefix}:{func.__name__}", 
                *args, 
                **kwargs
            )
            
            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 缓存未命中，执行函数
            result = func(*args, **kwargs)
            
            # 将结果存入缓存
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# 便捷函数
def cache_get(key: str) -> Optional[Any]:
    """获取缓存值"""
    return cache_manager.get(key)

def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """设置缓存值"""
    return cache_manager.set(key, value, ttl)

def cache_delete(key: str) -> bool:
    """删除缓存项"""
    return cache_manager.delete(key)

def cache_clear():
    """清空缓存"""
    cache_manager.clear()

def cache_stats() -> Dict[str, Any]:
    """获取缓存统计"""
    return cache_manager.get_stats()
