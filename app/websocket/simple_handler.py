"""
简化的双人会话消息处理器
处理WebSocket消息的接收、验证、存储和转发
"""

import json
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.websocket.simple_manager import simple_manager
from app.models.chat_models import Message
from app.db import get_database_session
import uuid

logger = logging.getLogger(__name__)

class SimpleMessageHandler:
    """简化的消息处理器"""
    
    @staticmethod
    async def handle_message(sender_id: int, message_data: dict) -> dict:
        """处理消息"""
        try:
            message_type = message_data.get("type")
            
            if message_type == "chat_message":
                return await SimpleMessageHandler._handle_chat_message(sender_id, message_data)
            elif message_type == "typing":
                return await SimpleMessageHandler._handle_typing(sender_id, message_data)
            elif message_type == "ping":
                return await SimpleMessageHandler._handle_ping(sender_id, message_data)
            elif message_type == "get_online_status":
                return await SimpleMessageHandler._handle_get_online_status(sender_id, message_data)
            elif message_type == "get_history":
                return await SimpleMessageHandler._handle_get_history(sender_id, message_data)
            else:
                return {"success": False, "error": f"未知消息类型: {message_type}"}
                
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def _handle_chat_message(sender_id: int, message_data: dict) -> dict:
        """处理聊天消息"""
        content = message_data.get("content")
        message_type = message_data.get("message_type", "text")
        conversation_id = message_data.get("conversation_id")
        
        if not content or not content.strip():
            return {"success": False, "error": "消息内容不能为空"}
        
        if not conversation_id:
            return {"success": False, "error": "缺少会话ID"}
        
        # 检查内容长度
        if len(content) > 10000:
            return {"success": False, "error": "消息内容过长，请控制在10000字符以内"}
        
        # 创建消息对象
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        message_obj = {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "sender_id": sender_id,
            "content": content.strip(),
            "message_type": message_type,
            "timestamp": timestamp.isoformat() + "Z"  # 添加Z后缀表示UTC时间
        }
        
        # 异步保存到数据库
        asyncio.create_task(
            SimpleMessageHandler._save_message_to_db(message_obj)
        )
        
        # 发送给另一个用户
        success = await simple_manager.send_to_other_user(sender_id, {
            "type": "new_message",
            "data": message_obj
        })
        
        if success:
            simple_manager.stats["total_messages"] += 1
        
        return {
            "success": True,
            "message_id": message_id,
            "conversation_id": conversation_id,
            "timestamp": message_obj["timestamp"],
            "sent": success,
            "other_user_online": success
        }
    
    @staticmethod
    async def _handle_typing(sender_id: int, message_data: dict) -> dict:
        """处理正在输入状态"""
        is_typing = message_data.get("is_typing", True)
        
        # 发送给另一个用户
        await simple_manager.send_to_other_user(sender_id, {
            "type": "typing_status",
            "data": {
                "user_id": sender_id,
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        })
        
        return {"success": True}
    
    @staticmethod
    async def _handle_ping(sender_id: int, message_data: dict) -> dict:
        """处理心跳检测"""
        return {
            "success": True,
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    @staticmethod
    async def _handle_get_online_status(sender_id: int, message_data: dict) -> dict:
        """处理获取在线状态请求"""
        other_user_id = simple_manager.get_other_user_id(sender_id)
        online_users = simple_manager.get_online_users()
        
        return {
            "success": True,
            "online_users": online_users,
            "other_user_id": other_user_id,
            "other_user_online": other_user_id is not None,
            "online_count": len(online_users)
        }
    
    @staticmethod
    async def _handle_get_history(sender_id: int, message_data: dict) -> dict:
        """处理获取历史消息请求"""
        conversation_id = message_data.get("conversation_id")
        page = message_data.get("page", 1)
        limit = message_data.get("limit", 20)
        
        if not conversation_id:
            return {"success": False, "error": "缺少会话ID"}
        
        # 获取历史消息
        messages = await SimpleMessageHandler._get_history_messages(
            conversation_id, page, limit
        )
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "messages": messages,
            "page": page,
            "limit": limit
        }
    
    @staticmethod
    async def _get_history_messages(conversation_id: str, page: int, limit: int):
        """获取历史消息"""
        try:
            db = next(get_database_session())
            
            # 计算偏移量
            offset = (page - 1) * limit
            
            # 查询消息
            from sqlalchemy import and_, desc
            messages = db.query(Message).filter(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.is_deleted == 0
                )
            ).order_by(desc(Message.create_time)).offset(offset).limit(limit).all()
            
            # 转换为字典格式
            message_list = []
            for msg in messages:
                message_list.append({
                    "message_id": msg.message_id,
                    "sender_id": msg.sender_id,
                    "content": msg.content,
                    "message_type": msg.message_type,
                    "timestamp": msg.create_time.isoformat() + "Z"  # 添加Z后缀表示UTC时间
                })
            
            return message_list
            
        except Exception as e:
            logger.error(f"获取历史消息失败: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    async def _save_message_to_db(message_obj: dict):
        """异步保存消息到数据库"""
        try:
            db = next(get_database_session())
            message = Message(
                message_id=message_obj["message_id"],
                conversation_id=message_obj["conversation_id"],  # 使用正确的conversation_id
                sender_id=message_obj["sender_id"],
                receiver_id=0,  # 双人会话
                content=message_obj["content"],
                message_type=message_obj["message_type"]
            )
            db.add(message)
            db.commit()
            logger.info(f"消息 {message_obj['message_id']} 已保存到数据库")
        except Exception as e:
            logger.error(f"保存消息失败: {e}")
        finally:
            db.close()
