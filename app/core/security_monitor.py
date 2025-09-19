"""
EchoSoul AI Platform Security Monitor
安全监控和告警系统
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import redis

logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
    """安全事件类型"""
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    SUSPICIOUS_USER_AGENT = "suspicious_user_agent"
    LOGIN_FAILURE = "login_failure"
    ACCOUNT_LOCKED = "account_locked"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    FILE_UPLOAD_ATTACK = "file_upload_attack"
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    DDoS_ATTACK = "ddos_attack"

class SecurityLevel(Enum):
    """安全级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    """安全事件数据类"""
    event_id: str
    event_type: SecurityEventType
    level: SecurityLevel
    timestamp: float
    client_ip: str
    user_agent: str
    request_path: str
    request_method: str
    details: Dict[str, Any]
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['level'] = self.level.value
        return data

class SecurityMonitor:
    """安全监控器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.memory_store: Dict[str, List[SecurityEvent]] = {}
        
        # 告警阈值配置
        self.alert_thresholds = {
            SecurityEventType.RATE_LIMIT_EXCEEDED: {"count": 10, "window": 300},  # 5分钟内10次
            SecurityEventType.SQL_INJECTION_ATTEMPT: {"count": 3, "window": 300},  # 5分钟内3次
            SecurityEventType.XSS_ATTEMPT: {"count": 3, "window": 300},           # 5分钟内3次
            SecurityEventType.LOGIN_FAILURE: {"count": 20, "window": 600},        # 10分钟内20次
            SecurityEventType.BRUTE_FORCE_ATTACK: {"count": 5, "window": 300},    # 5分钟内5次
            SecurityEventType.DDoS_ATTACK: {"count": 100, "window": 60},          # 1分钟内100次
        }
        
        # 统计计数器
        self.stats = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_level": {},
            "events_by_ip": {},
            "last_reset": time.time()
        }
    
    def _generate_event_id(self) -> str:
        """生成事件ID"""
        return f"sec_{int(time.time() * 1000)}"
    
    def _get_redis_key(self, event_type: SecurityEventType, client_ip: str) -> str:
        """获取Redis键名"""
        return f"security_events:{event_type.value}:{client_ip}"
    
    def _store_event_redis(self, event: SecurityEvent) -> bool:
        """使用Redis存储事件"""
        try:
            key = f"security_event:{event.event_id}"
            event_data = json.dumps(event.to_dict())
            
            # 存储事件详情
            self.redis_client.setex(key, 86400, event_data)  # 24小时过期
            
            # 更新统计
            self._update_stats_redis(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis event storage error: {e}")
            return False
    
    def _store_event_memory(self, event: SecurityEvent) -> bool:
        """使用内存存储事件"""
        try:
            # 存储到内存
            if event.client_ip not in self.memory_store:
                self.memory_store[event.client_ip] = []
            
            self.memory_store[event.client_ip].append(event)
            
            # 清理过期事件（保留最近1小时）
            cutoff_time = time.time() - 3600
            self.memory_store[event.client_ip] = [
                e for e in self.memory_store[event.client_ip]
                if e.timestamp > cutoff_time
            ]
            
            # 更新统计
            self._update_stats_memory(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Memory event storage error: {e}")
            return False
    
    def _update_stats_redis(self, event: SecurityEvent):
        """使用Redis更新统计"""
        try:
            pipe = self.redis_client.pipeline()
            
            # 更新总计数
            pipe.hincrby("security_stats", "total_events", 1)
            
            # 更新事件类型统计
            pipe.hincrby("security_stats", f"type_{event.event_type.value}", 1)
            
            # 更新安全级别统计
            pipe.hincrby("security_stats", f"level_{event.level.value}", 1)
            
            # 更新IP统计
            pipe.hincrby("security_stats", f"ip_{event.client_ip}", 1)
            
            pipe.execute()
            
        except Exception as e:
            logger.error(f"Redis stats update error: {e}")
    
    def _update_stats_memory(self, event: SecurityEvent):
        """使用内存更新统计"""
        self.stats["total_events"] += 1
        
        # 事件类型统计
        event_type_key = event.event_type.value
        self.stats["events_by_type"][event_type_key] = self.stats["events_by_type"].get(event_type_key, 0) + 1
        
        # 安全级别统计
        level_key = event.level.value
        self.stats["events_by_level"][level_key] = self.stats["events_by_level"].get(level_key, 0) + 1
        
        # IP统计
        self.stats["events_by_ip"][event.client_ip] = self.stats["events_by_ip"].get(event.client_ip, 0) + 1
    
    def log_security_event(
        self,
        event_type: SecurityEventType,
        level: SecurityLevel,
        client_ip: str,
        user_agent: str,
        request_path: str,
        request_method: str,
        details: Dict[str, Any],
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> SecurityEvent:
        """记录安全事件"""
        
        event = SecurityEvent(
            event_id=self._generate_event_id(),
            event_type=event_type,
            level=level,
            timestamp=time.time(),
            client_ip=client_ip,
            user_agent=user_agent,
            request_path=request_path,
            request_method=request_method,
            details=details,
            user_id=user_id,
            session_id=session_id
        )
        
        # 存储事件
        if self.redis_client:
            success = self._store_event_redis(event)
        else:
            success = self._store_event_memory(event)
        
        if success:
            # 记录日志
            logger.warning(f"Security event: {event_type.value} from {client_ip} - {json.dumps(details)}")
            
            # 检查是否需要告警
            self._check_alert_threshold(event)
        
        return event
    
    def _check_alert_threshold(self, event: SecurityEvent):
        """检查告警阈值"""
        threshold_config = self.alert_thresholds.get(event.event_type)
        if not threshold_config:
            return
        
        # 检查是否超过阈值
        recent_events = self._get_recent_events(
            event.event_type,
            event.client_ip,
            threshold_config["window"]
        )
        
        if len(recent_events) >= threshold_config["count"]:
            self._trigger_alert(event, recent_events)
    
    def _get_recent_events(self, event_type: SecurityEventType, client_ip: str, window_seconds: int) -> List[SecurityEvent]:
        """获取最近的事件"""
        cutoff_time = time.time() - window_seconds
        
        if self.redis_client:
            return self._get_recent_events_redis(event_type, client_ip, cutoff_time)
        else:
            return self._get_recent_events_memory(event_type, client_ip, cutoff_time)
    
    def _get_recent_events_redis(self, event_type: SecurityEventType, client_ip: str, cutoff_time: float) -> List[SecurityEvent]:
        """从Redis获取最近事件"""
        try:
            key = self._get_redis_key(event_type, client_ip)
            event_ids = self.redis_client.zrangebyscore(key, cutoff_time, "+inf")
            
            events = []
            for event_id in event_ids:
                event_data = self.redis_client.get(f"security_event:{event_id}")
                if event_data:
                    event_dict = json.loads(event_data)
                    events.append(SecurityEvent(**event_dict))
            
            return events
            
        except Exception as e:
            logger.error(f"Redis recent events error: {e}")
            return []
    
    def _get_recent_events_memory(self, event_type: SecurityEventType, client_ip: str, cutoff_time: float) -> List[SecurityEvent]:
        """从内存获取最近事件"""
        if client_ip not in self.memory_store:
            return []
        
        return [
            event for event in self.memory_store[client_ip]
            if event.event_type == event_type and event.timestamp > cutoff_time
        ]
    
    def _trigger_alert(self, event: SecurityEvent, recent_events: List[SecurityEvent]):
        """触发告警"""
        alert_data = {
            "alert_type": f"{event.event_type.value}_threshold_exceeded",
            "level": event.level.value,
            "client_ip": event.client_ip,
            "event_count": len(recent_events),
            "time_window": self.alert_thresholds[event.event_type]["window"],
            "first_event": recent_events[0].timestamp if recent_events else None,
            "last_event": event.timestamp,
            "details": event.details
        }
        
        # 记录告警日志
        logger.critical(f"SECURITY ALERT: {json.dumps(alert_data)}")
        
        # 这里可以添加其他告警方式：
        # - 发送邮件
        # - 发送短信
        # - 调用webhook
        # - 写入告警数据库
    
    def get_security_stats(self) -> Dict[str, Any]:
        """获取安全统计信息"""
        if self.redis_client:
            return self._get_stats_redis()
        else:
            return self._get_stats_memory()
    
    def _get_stats_redis(self) -> Dict[str, Any]:
        """从Redis获取统计信息"""
        try:
            stats = self.redis_client.hgetall("security_stats")
            return {k.decode(): int(v.decode()) for k, v in stats.items()}
        except Exception as e:
            logger.error(f"Redis stats retrieval error: {e}")
            return {}
    
    def _get_stats_memory(self) -> Dict[str, Any]:
        """从内存获取统计信息"""
        return self.stats.copy()
    
    def get_top_threat_ips(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取威胁最大的IP列表"""
        stats = self.get_security_stats()
        
        ip_stats = []
        for key, count in stats.items():
            if key.startswith("ip_"):
                ip = key[3:]  # 移除 "ip_" 前缀
                ip_stats.append({"ip": ip, "count": count})
        
        # 按威胁次数排序
        ip_stats.sort(key=lambda x: x["count"], reverse=True)
        
        return ip_stats[:limit]
    
    def get_event_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取事件摘要"""
        cutoff_time = time.time() - (hours * 3600)
        
        summary = {
            "time_range": f"Last {hours} hours",
            "total_events": 0,
            "events_by_type": {},
            "events_by_level": {},
            "top_threat_ips": [],
            "critical_events": 0
        }
        
        # 这里可以实现更详细的事件摘要逻辑
        # 由于时间限制，这里返回基本统计
        
        return summary

# 全局安全监控实例
security_monitor = SecurityMonitor()
