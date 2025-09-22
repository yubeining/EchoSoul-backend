"""
AI对话WebSocket连接管理器
专门处理用户与AI角色的实时对话连接
"""

import json
import asyncio
import logging
from typing import Dict, Optional, Set, List
from fastapi import WebSocket
from datetime import datetime
import uuid

from app.core.logging_manager import log_info, log_operation_start, log_operation_success, log_operation_error

logger = logging.getLogger(__name__)

class AIConnectionManager:
    """AI对话连接管理器"""
    
    def __init__(self):
        # 用户ID -> WebSocket连接
        self.connections: Dict[int, WebSocket] = {}
        # 用户ID -> 当前AI角色ID
        self.user_ai_sessions: Dict[int, str] = {}
        # 用户ID -> 最后活跃时间
        self.user_activity: Dict[int, datetime] = {}
        # 正在处理的AI回复任务
        self.ai_processing_tasks: Dict[int, asyncio.Task] = {}
        # 消息统计
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "total_messages": 0,
            "ai_replies": 0
        }
    
    async def connect(self, websocket: WebSocket, user_id: int) -> bool:
        """建立AI对话连接"""
        try:
            await websocket.accept()
            
            # 如果用户已有连接，先关闭旧连接
            if user_id in self.connections:
                await self.disconnect(user_id)
            
            self.connections[user_id] = websocket
            self.user_activity[user_id] = datetime.utcnow()
            self.stats["active_connections"] = len(self.connections)
            self.stats["total_connections"] += 1
            
            log_info(f"用户已连接到AI对话", user_id=user_id)
            
            # 发送连接成功消息
            await self.send_to_user(user_id, {
                "type": "connection_established",
                "message": "AI对话连接已建立",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
            return True
            
        except Exception as e:
            log_operation_error("AI对话连接", str(e), user_id=user_id)
            return False
    
    async def disconnect(self, user_id: int):
        """断开AI对话连接"""
        if user_id in self.connections:
            try:
                # 取消正在处理的AI任务
                if user_id in self.ai_processing_tasks:
                    task = self.ai_processing_tasks[user_id]
                    if not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                    del self.ai_processing_tasks[user_id]
                
                # 尝试关闭WebSocket连接
                websocket = self.connections[user_id]
                if websocket and not websocket.client_state.disconnected:
                    try:
                        await websocket.close()
                    except Exception as e:
                        logger.warning(f"关闭WebSocket连接失败: {e}")
                
                # 清理连接信息
                del self.connections[user_id]
                if user_id in self.user_activity:
                    del self.user_activity[user_id]
                if user_id in self.user_ai_sessions:
                    del self.user_ai_sessions[user_id]
                
                self.stats["active_connections"] = len(self.connections)
                log_info(f"用户已断开AI对话连接", user_id=user_id)
                
            except Exception as e:
                log_operation_error("断开连接", str(e), user_id=user_id)
                # 强制清理
                self.connections.pop(user_id, None)
                self.user_activity.pop(user_id, None)
                self.user_ai_sessions.pop(user_id, None)
                self.ai_processing_tasks.pop(user_id, None)
                self.stats["active_connections"] = len(self.connections)
    
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
            log_operation_error("发送消息", str(e), user_id=user_id)
            await self.disconnect(user_id)
            return False
    
    async def start_ai_session(self, user_id: int, ai_character_id: str) -> bool:
        """开始AI会话"""
        if user_id not in self.connections:
            return False
        
        self.user_ai_sessions[user_id] = ai_character_id
        
        # 发送会话开始消息
        await self.send_to_user(user_id, {
            "type": "ai_session_started",
            "ai_character_id": ai_character_id,
            "message": "AI会话已开始",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        return True
    
    async def end_ai_session(self, user_id: int) -> bool:
        """结束AI会话"""
        if user_id in self.user_ai_sessions:
            ai_character_id = self.user_ai_sessions[user_id]
            del self.user_ai_sessions[user_id]
            
            # 发送会话结束消息
            await self.send_to_user(user_id, {
                "type": "ai_session_ended",
                "ai_character_id": ai_character_id,
                "message": "AI会话已结束",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
            return True
        return False
    
    def get_user_ai_session(self, user_id: int) -> Optional[str]:
        """获取用户的当前AI会话"""
        return self.user_ai_sessions.get(user_id)
    
    def is_user_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.connections
    
    def get_online_users(self) -> List[int]:
        """获取在线用户列表"""
        return list(self.connections.keys())
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            "online_users": self.get_online_users(),
            "online_count": len(self.connections),
            "active_ai_sessions": len(self.user_ai_sessions),
            "processing_tasks": len(self.ai_processing_tasks)
        }
    
    async def send_ai_stream_start(self, user_id: int, message_id: str):
        """发送AI流式回复开始信号"""
        await self.send_to_user(user_id, {
            "type": "ai_stream_start",
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    async def send_ai_stream_chunk(self, user_id: int, message_id: str, chunk: str):
        """发送AI流式回复片段"""
        await self.send_to_user(user_id, {
            "type": "ai_stream_chunk",
            "message_id": message_id,
            "chunk": chunk,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    async def send_ai_stream_end(self, user_id: int, message_id: str, final_content: str):
        """发送AI流式回复结束信号"""
        await self.send_to_user(user_id, {
            "type": "ai_stream_end",
            "message_id": message_id,
            "final_content": final_content,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    async def send_ai_error(self, user_id: int, error_message: str):
        """发送AI错误消息"""
        await self.send_to_user(user_id, {
            "type": "ai_error",
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    
    def set_ai_processing_task(self, user_id: int, task: asyncio.Task):
        """设置AI处理任务"""
        self.ai_processing_tasks[user_id] = task
    
    def clear_ai_processing_task(self, user_id: int):
        """清除AI处理任务"""
        if user_id in self.ai_processing_tasks:
            del self.ai_processing_tasks[user_id]
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """清理非活跃连接"""
        current_time = datetime.utcnow()
        inactive_users = []
        
        for user_id, last_activity in self.user_activity.items():
            if (current_time - last_activity).total_seconds() > timeout_minutes * 60:
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            log_info(f"清理非活跃连接", user_id=user_id)
            await self.disconnect(user_id)
    
    async def health_check_connections(self):
        """检查连接健康状态"""
        dead_connections = []
        
        for user_id, websocket in self.connections.items():
            try:
                # 检查连接状态
                if websocket.client_state.disconnected:
                    dead_connections.append(user_id)
                    continue
                
                # 发送ping消息检查连接
                await websocket.send_text(json.dumps({
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }))
            except Exception as e:
                log_operation_error("连接健康检查", str(e), user_id=user_id)
                dead_connections.append(user_id)
        
        # 清理死连接
        for user_id in dead_connections:
            log_info(f"清理死连接", user_id=user_id)
            await self.disconnect(user_id)
    
    def get_connection_stats(self) -> dict:
        """获取连接统计信息"""
        return {
            "total_connections": self.stats["total_connections"],
            "active_connections": len(self.connections),
            "active_ai_sessions": len(self.user_ai_sessions),
            "processing_tasks": len(self.ai_processing_tasks),
            "online_users": list(self.connections.keys()),
            "ai_sessions": dict(self.user_ai_sessions)
        }

# 全局AI对话管理器实例
ai_manager = AIConnectionManager()


