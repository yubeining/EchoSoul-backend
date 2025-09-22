"""
AI对话WebSocket消息处理器
处理用户与AI角色的实时对话消息
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid

from app.websocket.ai_manager import ai_manager
from app.models.chat_models import Conversation, Message
from app.models.ai_character_models import AICharacter
from app.db import get_database_session
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class AIMessageHandler:
    """AI对话消息处理器"""
    
    @staticmethod
    async def handle_message(user_id: int, message_data: dict) -> dict:
        """处理AI对话消息"""
        try:
            # 验证消息格式
            if not isinstance(message_data, dict):
                return {"success": False, "error": "消息格式无效"}
            
            message_type = message_data.get("type")
            if not message_type:
                return {"success": False, "error": "缺少消息类型"}
            
            # 消息处理器映射
            handlers = {
                "start_ai_session": AIMessageHandler._handle_start_ai_session,
                "end_ai_session": AIMessageHandler._handle_end_ai_session,
                "chat_message": AIMessageHandler._handle_chat_message,
                "get_conversation_history": AIMessageHandler._handle_get_history,
                "get_ai_characters": AIMessageHandler._handle_get_ai_characters,
                "ping": AIMessageHandler._handle_ping
            }
            
            handler = handlers.get(message_type)
            if handler:
                return await handler(user_id, message_data)
            else:
                return {"success": False, "error": f"未知消息类型: {message_type}"}
                
        except Exception as e:
            logger.error(f"处理AI消息失败 (用户ID: {user_id}): {e}", exc_info=True)
            return {"success": False, "error": "服务器内部错误"}
    
    @staticmethod
    async def _handle_start_ai_session(user_id: int, message_data: dict) -> dict:
        """处理开始AI会话请求"""
        ai_character_id = message_data.get("ai_character_id")
        conversation_id = message_data.get("conversation_id")
        
        if not ai_character_id:
            return {"success": False, "error": "缺少AI角色ID"}
        
        try:
            db = next(get_database_session())
            
            # 验证AI角色是否存在
            ai_character = db.query(AICharacter).filter(
                and_(
                    AICharacter.character_id == ai_character_id,
                    AICharacter.status == 1
                )
            ).first()
            
            if not ai_character:
                return {"success": False, "error": "AI角色不存在"}
            
            # 获取或创建会话
            if conversation_id:
                # 验证现有会话
                conversation = db.query(Conversation).filter(
                    and_(
                        Conversation.conversation_id == conversation_id,
                        Conversation.user1_id == user_id,
                        Conversation.conversation_type == 'user_ai',
                        Conversation.status == 1
                    )
                ).first()
                
                if not conversation:
                    return {"success": False, "error": "会话不存在或无权限"}
            else:
                # 创建新会话
                conversation_id = str(uuid.uuid4())
                conversation_name = f"与{ai_character.nickname}的对话"
                
                conversation = Conversation(
                    conversation_id=conversation_id,
                    user1_id=user_id,
                    user2_id=0,  # AI使用0作为ID
                    conversation_name=conversation_name,
                    conversation_type='user_ai',
                    ai_character_id=ai_character_id,
                    status=1
                )
                
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
            
            # 启动AI会话
            success = await ai_manager.start_ai_session(user_id, ai_character_id)
            
            return {
                "success": success,
                "conversation_id": conversation_id,
                "ai_character": {
                    "character_id": ai_character.character_id,
                    "nickname": ai_character.nickname,
                    "description": ai_character.description,
                    "personality": ai_character.personality
                }
            }
            
        except Exception as e:
            logger.error(f"开始AI会话失败: {e}")
            return {"success": False, "error": f"开始AI会话失败: {str(e)}"}
        finally:
            db.close()
    
    @staticmethod
    async def _handle_end_ai_session(user_id: int, message_data: dict) -> dict:
        """处理结束AI会话请求"""
        success = await ai_manager.end_ai_session(user_id)
        return {"success": success}
    
    @staticmethod
    async def _handle_chat_message(user_id: int, message_data: dict) -> dict:
        """处理聊天消息"""
        content = message_data.get("content")
        conversation_id = message_data.get("conversation_id")
        message_type = message_data.get("message_type", "text")
        
        if not content or not content.strip():
            return {"success": False, "error": "消息内容不能为空"}
        
        if not conversation_id:
            return {"success": False, "error": "缺少会话ID"}
        
        # 检查内容长度
        if len(content) > 10000:
            return {"success": False, "error": "消息内容过长，请控制在10000字符以内"}
        
        # 检查是否有活跃的AI会话
        current_ai_session = ai_manager.get_user_ai_session(user_id)
        if not current_ai_session:
            return {"success": False, "error": "没有活跃的AI会话"}
        
        try:
            db = next(get_database_session())
            
            # 验证会话
            conversation = db.query(Conversation).filter(
                and_(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user1_id == user_id,
                    Conversation.conversation_type == 'user_ai',
                    Conversation.status == 1
                )
            ).first()
            
            if not conversation:
                return {"success": False, "error": "会话不存在或无权限"}
            
            # 获取AI角色信息
            ai_character = db.query(AICharacter).filter(
                and_(
                    AICharacter.character_id == conversation.ai_character_id,
                    AICharacter.status == 1
                )
            ).first()
            
            if not ai_character:
                return {"success": False, "error": "AI角色不存在"}
            
            # 1. 保存用户消息
            user_message_id = str(uuid.uuid4())
            user_message = Message(
                message_id=user_message_id,
                conversation_id=conversation_id,
                sender_id=user_id,
                receiver_id=0,  # AI使用0作为ID
                content=content.strip(),
                message_type=message_type,
                is_ai_message=False,
                ai_character_id=ai_character.character_id
            )
            
            db.add(user_message)
            db.flush()
            
            # 2. 发送用户消息确认
            await ai_manager.send_to_user(user_id, {
                "type": "user_message_sent",
                "message_id": user_message_id,
                "content": content.strip(),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
            # 3. 异步处理AI回复
            ai_message_id = str(uuid.uuid4())
            task = asyncio.create_task(
                AIMessageHandler._process_ai_reply(
                    db, conversation, ai_character, user_message, ai_message_id
                )
            )
            ai_manager.set_ai_processing_task(user_id, task)
            
            return {
                "success": True,
                "message_id": user_message_id,
                "conversation_id": conversation_id,
                "ai_processing": True
            }
            
        except Exception as e:
            logger.error(f"处理聊天消息失败: {e}")
            return {"success": False, "error": f"处理消息失败: {str(e)}"}
        finally:
            db.close()
    
    @staticmethod
    async def _process_ai_reply(
        db: Session,
        conversation: Conversation,
        ai_character: AICharacter,
        user_message: Message,
        ai_message_id: str
    ):
        """异步处理AI回复"""
        user_id = conversation.user1_id
        
        try:
            # 发送AI回复开始信号
            await ai_manager.send_ai_stream_start(user_id, ai_message_id)
            
            # 获取对话历史
            conversation_history = AIMessageHandler._get_conversation_history_for_llm(
                db, conversation.conversation_id, limit=10
            )
            
            # 调用流式LLM服务进行回复
            ai_reply = await LLMService.stream_chat_with_character(
                user_message=user_message.content,
                character_name=ai_character.nickname,
                character_personality=ai_character.personality,
                conversation_history=conversation_history,
                max_tokens=512,
                temperature=0.8
            )
            
            if not ai_reply:
                # 使用降级回复
                ai_reply = AIMessageHandler._generate_fallback_reply(
                    user_message.content, ai_character
                )
            
            # 模拟流式输出（将回复分成多个片段）
            chunks = AIMessageHandler._split_into_chunks(ai_reply, chunk_size=30)
            
            # 发送流式片段
            for chunk in chunks:
                await ai_manager.send_ai_stream_chunk(user_id, ai_message_id, chunk)
                await asyncio.sleep(0.2)  # 流式延迟，让用户看到打字效果
            
            # 保存AI回复到数据库
            ai_message = Message(
                message_id=ai_message_id,
                conversation_id=conversation.conversation_id,
                sender_id=0,  # AI使用0作为ID
                receiver_id=user_id,
                content=ai_reply,
                message_type='text',
                is_ai_message=True,
                ai_character_id=ai_character.character_id
            )
            
            db.add(ai_message)
            
            # 更新会话的最后消息信息
            conversation.last_message_id = ai_message.id
            conversation.last_message_time = datetime.utcnow()
            
            # 增加AI角色使用次数
            ai_character.usage_count += 1
            
            db.commit()
            
            # 发送AI回复结束信号
            await ai_manager.send_ai_stream_end(user_id, ai_message_id, ai_reply)
            
            # 更新统计
            ai_manager.stats["ai_replies"] += 1
            
        except Exception as e:
            logger.error(f"AI回复处理失败: {e}")
            await ai_manager.send_ai_error(user_id, f"AI回复失败: {str(e)}")
        finally:
            ai_manager.clear_ai_processing_task(user_id)
            db.close()
    
    @staticmethod
    def _split_into_chunks(text: str, chunk_size: int = 50) -> list:
        """将文本分割成流式片段"""
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks
    
    @staticmethod
    def _get_conversation_history_for_llm(
        db: Session, 
        conversation_id: str, 
        limit: int = 10
    ) -> list:
        """获取对话历史，格式化为LLM需要的格式"""
        try:
            messages = db.query(Message).filter(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.is_deleted == 0
                )
            ).order_by(desc(Message.create_time)).limit(limit).all()
            
            history = []
            for msg in reversed(messages):  # 按时间正序排列
                role = "assistant" if msg.is_ai_message else "user"
                history.append({
                    "role": role,
                    "content": msg.content
                })
            
            return history
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    @staticmethod
    def _generate_fallback_reply(user_message: str, ai_character: AICharacter) -> str:
        """生成降级回复（当LLM API不可用时）"""
        import random
        
        # 根据角色的人设和说话风格生成回复
        personality = ai_character.personality or "友好"
        speaking_style = ai_character.speaking_style or "自然"
        
        # 简单的回复模板
        replies = [
            f"你好！我是{ai_character.nickname}，很高兴和你聊天！",
            f"作为{ai_character.nickname}，我想说：{user_message} 这个话题很有趣呢！",
            f"嗯，{user_message}... 让我想想，{ai_character.nickname}觉得这很有道理！",
            f"哇，你提到了{user_message}！{ai_character.nickname}对此很感兴趣！",
            f"作为{ai_character.nickname}，我的{personality}性格让我想说：{user_message} 确实值得思考！"
        ]
        
        # 根据消息内容选择回复
        if "你好" in user_message or "hello" in user_message.lower():
            return f"你好！我是{ai_character.nickname}，很高兴认识你！{ai_character.description or ''}"
        elif "再见" in user_message or "bye" in user_message.lower():
            return f"再见！{ai_character.nickname}期待下次和你聊天！"
        else:
            return random.choice(replies)
    
    @staticmethod
    async def _handle_get_history(user_id: int, message_data: dict) -> dict:
        """处理获取历史消息请求"""
        conversation_id = message_data.get("conversation_id")
        page = message_data.get("page", 1)
        limit = message_data.get("limit", 20)
        
        if not conversation_id:
            return {"success": False, "error": "缺少会话ID"}
        
        try:
            db = next(get_database_session())
            
            # 验证会话权限
            conversation = db.query(Conversation).filter(
                and_(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user1_id == user_id,
                    Conversation.status == 1
                )
            ).first()
            
            if not conversation:
                return {"success": False, "error": "会话不存在或无权限"}
            
            # 获取历史消息
            offset = (page - 1) * limit
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
                    "is_ai_message": msg.is_ai_message,
                    "ai_character_id": msg.ai_character_id,
                    "timestamp": msg.create_time.isoformat() + "Z"
                })
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "messages": message_list,
                "page": page,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"获取历史消息失败: {e}")
            return {"success": False, "error": f"获取历史消息失败: {str(e)}"}
        finally:
            db.close()
    
    @staticmethod
    async def _handle_get_ai_characters(user_id: int, message_data: dict) -> dict:
        """处理获取AI角色列表请求"""
        try:
            db = next(get_database_session())
            
            # 获取所有可用的AI角色
            ai_characters = db.query(AICharacter).filter(
                AICharacter.status == 1
            ).all()
            
            # 转换为字典格式
            character_list = []
            for char in ai_characters:
                character_list.append({
                    "character_id": char.character_id,
                    "nickname": char.nickname,
                    "description": char.description,
                    "personality": char.personality,
                    "speaking_style": char.speaking_style,
                    "usage_count": char.usage_count
                })
            
            return {
                "success": True,
                "ai_characters": character_list
            }
            
        except Exception as e:
            logger.error(f"获取AI角色列表失败: {e}")
            return {"success": False, "error": f"获取AI角色列表失败: {str(e)}"}
        finally:
            db.close()
    
    @staticmethod
    async def _handle_ping(user_id: int, message_data: dict) -> dict:
        """处理心跳检测"""
        return {
            "success": True,
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
