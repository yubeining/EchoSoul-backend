"""
EchoSoul AI Platform Performance Monitor
性能监控和统计模块
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil
import threading

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.request_times = deque(maxlen=1000)  # 保留最近1000个请求的时间
        self.error_counts = defaultdict(int)
        self.active_connections = 0
        self.start_time = datetime.utcnow()
        self.lock = threading.Lock()
        
        # 系统资源监控
        self.cpu_usage_history = deque(maxlen=60)  # 保留最近60个CPU使用率
        self.memory_usage_history = deque(maxlen=60)  # 保留最近60个内存使用率
        
    def record_request_time(self, endpoint: str, duration: float, status_code: int = 200):
        """记录请求时间"""
        with self.lock:
            self.request_times.append({
                "endpoint": endpoint,
                "duration": duration,
                "status_code": status_code,
                "timestamp": datetime.utcnow()
            })
            
            # 记录到指标中
            self.metrics[f"request_time_{endpoint}"].append(duration)
            
            # 记录错误
            if status_code >= 400:
                self.error_counts[f"{endpoint}_{status_code}"] += 1
    
    def record_websocket_connection(self, connection_type: str, action: str):
        """记录WebSocket连接"""
        with self.lock:
            if action == "connect":
                self.active_connections += 1
            elif action == "disconnect":
                self.active_connections = max(0, self.active_connections - 1)
            
            self.metrics[f"websocket_{connection_type}_{action}"].append(datetime.utcnow())
    
    def record_database_operation(self, operation: str, duration: float, success: bool = True):
        """记录数据库操作"""
        with self.lock:
            self.metrics[f"db_{operation}"].append({
                "duration": duration,
                "success": success,
                "timestamp": datetime.utcnow()
            })
            
            if not success:
                self.error_counts[f"db_{operation}_error"] += 1
    
    def record_llm_operation(self, operation: str, duration: float, success: bool = True, tokens: int = 0):
        """记录LLM操作"""
        with self.lock:
            self.metrics[f"llm_{operation}"].append({
                "duration": duration,
                "success": success,
                "tokens": tokens,
                "timestamp": datetime.utcnow()
            })
            
            if not success:
                self.error_counts[f"llm_{operation}_error"] += 1
    
    def get_request_stats(self, endpoint: Optional[str] = None, minutes: int = 60) -> Dict[str, Any]:
        """获取请求统计"""
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            
            if endpoint:
                # 特定端点的统计
                endpoint_requests = [
                    req for req in self.request_times 
                    if req["endpoint"] == endpoint and req["timestamp"] > cutoff_time
                ]
            else:
                # 所有请求的统计
                endpoint_requests = [
                    req for req in self.request_times 
                    if req["timestamp"] > cutoff_time
                ]
            
            if not endpoint_requests:
                return {
                    "total_requests": 0,
                    "avg_duration": 0,
                    "min_duration": 0,
                    "max_duration": 0,
                    "error_rate": 0
                }
            
            durations = [req["duration"] for req in endpoint_requests]
            error_count = sum(1 for req in endpoint_requests if req["status_code"] >= 400)
            
            return {
                "total_requests": len(endpoint_requests),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "error_rate": error_count / len(endpoint_requests) * 100
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage_history.append(cpu_percent)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_usage_history.append(memory_percent)
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # 网络统计
            network = psutil.net_io_counters()
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "memory_available": memory.available,
                "disk_usage": disk_percent,
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "active_connections": self.active_connections,
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
            }
        except Exception as e:
            logger.error(f"获取系统统计失败: {e}")
            return {}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        with self.lock:
            # 请求统计
            request_stats = self.get_request_stats()
            
            # 系统统计
            system_stats = self.get_system_stats()
            
            # 错误统计
            total_errors = sum(self.error_counts.values())
            
            # 数据库操作统计
            db_operations = {}
            for key, values in self.metrics.items():
                if key.startswith("db_"):
                    if values:
                        durations = [v["duration"] if isinstance(v, dict) else v for v in values]
                        db_operations[key] = {
                            "count": len(values),
                            "avg_duration": sum(durations) / len(durations),
                            "success_rate": sum(1 for v in values if isinstance(v, dict) and v.get("success", True)) / len(values) * 100
                        }
            
            # LLM操作统计
            llm_operations = {}
            for key, values in self.metrics.items():
                if key.startswith("llm_"):
                    if values:
                        durations = [v["duration"] if isinstance(v, dict) else v for v in values]
                        total_tokens = sum(v.get("tokens", 0) for v in values if isinstance(v, dict))
                        llm_operations[key] = {
                            "count": len(values),
                            "avg_duration": sum(durations) / len(durations),
                            "total_tokens": total_tokens,
                            "success_rate": sum(1 for v in values if isinstance(v, dict) and v.get("success", True)) / len(values) * 100
                        }
            
            return {
                "request_stats": request_stats,
                "system_stats": system_stats,
                "error_summary": {
                    "total_errors": total_errors,
                    "error_breakdown": dict(self.error_counts)
                },
                "database_operations": db_operations,
                "llm_operations": llm_operations,
                "websocket_connections": self.active_connections,
                "monitoring_duration": (datetime.utcnow() - self.start_time).total_seconds()
            }
    
    def cleanup_old_metrics(self, hours: int = 24):
        """清理旧的指标数据"""
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            for key, values in self.metrics.items():
                if isinstance(values, list):
                    # 清理旧的时间戳数据
                    self.metrics[key] = [
                        v for v in values 
                        if not isinstance(v, dict) or v.get("timestamp", datetime.utcnow()) > cutoff_time
                    ]

# 性能监控装饰器
def monitor_performance(operation_name: str, monitor_type: str = "request"):
    """性能监控装饰器"""
    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    performance_monitor.record_request_time(operation_name, duration, 200)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    performance_monitor.record_request_time(operation_name, duration, 500)
                    raise
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    performance_monitor.record_request_time(operation_name, duration, 200)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    performance_monitor.record_request_time(operation_name, duration, 500)
                    raise
            return sync_wrapper
    return decorator

# 全局性能监控器实例
performance_monitor = PerformanceMonitor()
