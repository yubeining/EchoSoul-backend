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
from app.db import get_database_session, mysql_db
from app.services.llm_service import LLMService
from app.core.database_context import get_db_session
from app.core.logging_manager import log_operation_start, log_operation_success, log_operation_error, log_info
from app.core.cache_manager import cache_get, cache_set, cached

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
            log_operation_error("处理AI消息", str(e), user_id=user_id)
            return {"success": False, "error": "服务器内部错误"}
    
    @staticmethod
    async def _handle_start_ai_session(user_id: int, message_data: dict) -> dict:
        """处理开始AI会话请求"""
        ai_character_id = message_data.get("ai_character_id")
        conversation_id = message_data.get("conversation_id")
        
        if not ai_character_id:
            return {"success": False, "error": "缺少AI角色ID"}
        
        try:
            with get_db_session() as db:
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
            log_operation_error("开始AI会话", str(e), user_id=user_id)
            return {"success": False, "error": f"开始AI会话失败: {str(e)}"}
    
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
        frontend_message_id = message_data.get("message_id")
        
        log_operation_start("处理聊天消息", user_id=user_id, conversation_id=conversation_id)
        
        # 输入验证
        if not content or not content.strip():
            log_operation_error("处理聊天消息", "消息内容为空", user_id=user_id)
            return {"success": False, "error": "消息内容不能为空"}
        
        if not conversation_id:
            log_operation_error("处理聊天消息", "缺少会话ID", user_id=user_id)
            return {"success": False, "error": "缺少会话ID"}
        
        if len(content) > 10000:
            log_operation_error("处理聊天消息", f"消息内容过长: {len(content)}字符", user_id=user_id)
            return {"success": False, "error": "消息内容过长，请控制在10000字符以内"}
        
        # 检查AI会话状态
        current_ai_session = ai_manager.get_user_ai_session(user_id)
        if not current_ai_session:
            log_operation_error("处理聊天消息", "没有活跃的AI会话", user_id=user_id)
            return {"success": False, "error": "没有活跃的AI会话"}
        
        try:
            with get_db_session() as db:
                # 验证会话和AI角色
                conversation, ai_character = AIMessageHandler._validate_conversation_and_character(
                    db, conversation_id, user_id
                )
                
                if not conversation:
                    return {"success": False, "error": "会话不存在或无权限"}
                
                if not ai_character:
                    return {"success": False, "error": "AI角色不存在"}
                
                # 保存用户消息
                user_message_id = frontend_message_id or str(uuid.uuid4())
                user_message = Message(
                    message_id=user_message_id,
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    receiver_id=0,
                    content=content.strip(),
                    message_type=message_type,
                    is_ai_message=False,
                    ai_character_id=ai_character.character_id
                )
                
                db.add(user_message)
                db.commit()
                
                # 发送用户消息确认
                await ai_manager.send_to_user(user_id, {
                    "type": "user_message_sent",
                    "message_id": user_message_id,
                    "content": content.strip(),
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
                
                # 异步处理AI回复
                ai_message_id = str(uuid.uuid4())
                task = asyncio.create_task(
                    AIMessageHandler._process_ai_reply_async(
                        conversation_id, ai_character.character_id, user_message.content, ai_message_id
                    )
                )
                ai_manager.set_ai_processing_task(user_id, task)
                
                log_operation_success("处理聊天消息", user_id=user_id, message_id=user_message_id)
                return {
                    "success": True,
                    "message_id": user_message_id,
                    "conversation_id": conversation_id,
                    "ai_processing": True
                }
                
        except Exception as e:
            log_operation_error("处理聊天消息", str(e), user_id=user_id)
            return {"success": False, "error": f"处理消息失败: {str(e)}"}
    
    @staticmethod
    def _validate_conversation_and_character(db: Session, conversation_id: str, user_id: int) -> tuple:
        """验证会话和AI角色"""
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
            return None, None
        
        # 尝试从缓存获取AI角色信息
        cache_key = f"ai_character:{conversation.ai_character_id}"
        cached_character = cache_get(cache_key)
        
        if cached_character is not None and hasattr(cached_character, 'character_id'):
            return conversation, cached_character
        
        # 获取AI角色信息
        ai_character = db.query(AICharacter).filter(
            and_(
                AICharacter.character_id == conversation.ai_character_id,
                AICharacter.status == 1
            )
        ).first()
        
        # 缓存AI角色信息（10分钟）
        if ai_character:
            cache_set(cache_key, ai_character, ttl=600)
        
        return conversation, ai_character
    
    @staticmethod
    async def _process_ai_reply_async(
        conversation_id: str,
        ai_character_id: str,
        user_message_content: str,
        ai_message_id: str
    ):
        """异步处理AI回复（独立数据库会话）"""
        user_id = None
        try:
            with get_db_session() as db:
                # 获取会话和AI角色信息
                conversation = db.query(Conversation).filter(
                    and_(
                        Conversation.conversation_id == conversation_id,
                        Conversation.status == 1
                    )
                ).first()
                
                if not conversation:
                    log_operation_error("AI回复处理", f"会话不存在: {conversation_id}")
                    return
                
                ai_character = db.query(AICharacter).filter(
                    and_(
                        AICharacter.character_id == ai_character_id,
                        AICharacter.status == 1
                    )
                ).first()
                
                if not ai_character:
                    log_operation_error("AI回复处理", f"AI角色不存在: {ai_character_id}")
                    return
                
                user_id = conversation.user1_id
                
                # 发送AI回复开始信号
                await ai_manager.send_ai_stream_start(user_id, ai_message_id)
                
                # 获取对话历史
                conversation_history = AIMessageHandler._get_conversation_history_for_llm(
                    db, conversation_id, limit=10
                )
                
                # 调用流式LLM服务进行回复
                ai_reply = await LLMService.stream_chat_with_character(
                    user_message=user_message_content,
                    character_name=ai_character.nickname,
                    character_personality=ai_character.personality,
                    conversation_history=conversation_history,
                    max_tokens=512,
                    temperature=0.8
                )
                
                if not ai_reply:
                    # 使用降级回复
                    ai_reply = AIMessageHandler._generate_fallback_reply(
                        user_message_content, ai_character
                    )
                
                # 模拟流式输出（将回复分成多个片段）
                chunks = AIMessageHandler._split_into_chunks(ai_reply, chunk_size=50)
                
                # 发送流式片段（优化延迟）
                for i, chunk in enumerate(chunks):
                    await ai_manager.send_ai_stream_chunk(user_id, ai_message_id, chunk)
                    # 减少延迟，提高响应速度
                    if i < len(chunks) - 1:  # 最后一个片段不需要延迟
                        await asyncio.sleep(0.1)
                
                # 保存AI回复到数据库
                ai_message = Message(
                    message_id=ai_message_id,
                    conversation_id=conversation_id,
                    sender_id=0,  # AI使用0作为ID
                    receiver_id=user_id,
                    content=ai_reply,
                    message_type='text',
                    is_ai_message=True,
                    ai_character_id=ai_character_id
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
                
                log_operation_success("AI回复处理", user_id=user_id, message_id=ai_message_id)
                
        except Exception as e:
            log_operation_error("AI回复处理", str(e), user_id=user_id)
            if user_id:
                await ai_manager.send_ai_error(user_id, f"AI回复失败: {str(e)}")
        finally:
            ai_manager.clear_ai_processing_task(user_id)
    
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
            with get_db_session() as db:
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
            log_operation_error("获取历史消息", str(e), user_id=user_id)
            return {"success": False, "error": f"获取历史消息失败: {str(e)}"}
    
    @staticmethod
    async def _handle_get_ai_characters(user_id: int, message_data: dict) -> dict:
        """处理获取AI角色列表请求"""
        try:
            # 尝试从缓存获取
            cache_key = "ai_characters:active"
            cached_characters = cache_get(cache_key)
            
            if cached_characters is not None:
                return {
                    "success": True,
                    "ai_characters": cached_characters
                }
            
            with get_db_session() as db:
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
                
                # 缓存结果（5分钟）
                cache_set(cache_key, character_list, ttl=300)
                
                return {
                    "success": True,
                    "ai_characters": character_list
                }
                
        except Exception as e:
            log_operation_error("获取AI角色列表", str(e), user_id=user_id)
            return {"success": False, "error": f"获取AI角色列表失败: {str(e)}"}
    
    @staticmethod
    async def _handle_ping(user_id: int, message_data: dict) -> dict:
        """处理心跳检测"""
        return {
            "success": True,
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
