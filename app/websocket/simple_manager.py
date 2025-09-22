"""
简化的双人会话WebSocket连接管理器
专门处理只有两个用户的实时通信场景
"""

import json
import asyncio
import logging
from typing import Dict, Optional
from fastapi import WebSocket
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class SimpleConnectionManager:
    """简化的双人会话连接管理器"""
    
    def __init__(self):
        # 用户ID -> WebSocket连接
        self.connections: Dict[int, WebSocket] = {}
        # 用户ID -> 最后活跃时间
        self.user_activity: Dict[int, datetime] = {}
        # 消息统计
        self.stats = {
            "total_messages": 0,
            "active_connections": 0,
            "total_connections": 0
        }
    
    async def connect(self, websocket: WebSocket, user_id: int) -> bool:
        """建立连接"""
        try:
            await websocket.accept()
            self.connections[user_id] = websocket
            self.user_activity[user_id] = datetime.utcnow()
            self.stats["active_connections"] = len(self.connections)
            self.stats["total_connections"] += 1
            logger.info(f"用户 {user_id} 已连接")
            return True
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    def disconnect(self, user_id: int):
        """断开连接"""
        if user_id in self.connections:
            del self.connections[user_id]
            if user_id in self.user_activity:
                del self.user_activity[user_id]
            self.stats["active_connections"] = len(self.connections)
            logger.info(f"用户 {user_id} 已断开")
    
    async def send_to_user(self, user_id: int, message: dict) -> bool:
        """发送消息给指定用户"""
        if user_id not in self.connections:
            return False
        
        try:
            websocket = self.connections[user_id]
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
            self.user_activity[user_id] = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"发送失败: {e}")
            self.disconnect(user_id)
            return False
    
    async def send_to_other_user(self, sender_id: int, message: dict) -> bool:
        """发送消息给另一个用户"""
        # 找到另一个用户
        other_user_id = None
        for user_id in self.connections:
            if user_id != sender_id:
                other_user_id = user_id
                break
        
        if other_user_id:
            return await self.send_to_user(other_user_id, message)
        return False
    
    def is_user_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.connections
    
    def get_online_users(self) -> list:
        """获取在线用户列表"""
        return list(self.connections.keys())
    
    def get_other_user_id(self, current_user_id: int) -> Optional[int]:
        """获取另一个用户的ID"""
        for user_id in self.connections:
            if user_id != current_user_id:
                return user_id
        return None
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            "online_users": self.get_online_users(),
            "online_count": len(self.connections)
        }
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """清理非活跃连接"""
        current_time = datetime.utcnow()
        inactive_users = []
        
        for user_id, last_activity in self.user_activity.items():
            if (current_time - last_activity).total_seconds() > timeout_minutes * 60:
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            logger.info(f"清理简单WebSocket非活跃连接: 用户 {user_id}")
            self.disconnect(user_id)
    
    async def health_check_connections(self):
        """检查连接健康状态"""
        dead_connections = []
        
        for user_id, websocket in self.connections.items():
            try:
                # 发送ping消息检查连接
                await websocket.send_text(json.dumps({
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }))
            except Exception as e:
                logger.warning(f"简单WebSocket连接健康检查失败 (用户ID: {user_id}): {e}")
                dead_connections.append(user_id)
        
        # 清理死连接
        for user_id in dead_connections:
            logger.info(f"清理简单WebSocket死连接: 用户 {user_id}")
            self.disconnect(user_id)

# 全局实例
simple_manager = SimpleConnectionManager()
