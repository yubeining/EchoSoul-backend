"""
增强版AI对话WebSocket消息处理器
集成统一流程处理模块，支持六维状态管理和智能决策
"""

import json
import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.flow.flow_processor import flow_processor
from app.core.flow.models import UserInput, MessageType
from app.core.management.logging_manager import log_operation_start, log_operation_success, log_operation_error, log_info
from app.websocket.ai_manager import ai_manager
from app.models.chat_models import Conversation, Message
from app.models.ai_character_models import AICharacter
from app.core.utils.database_context import get_db_session
from app.core.utils.cache_manager import cache_get, cache_set

logger = logging.getLogger(__name__)

class EnhancedAIMessageHandler:
    """增强版AI对话消息处理器"""
    
    def __init__(self):
        self.flow_processor = flow_processor
        self.active_sessions = {}  # 活跃会话管理
        self.processing_tasks = {}  # 处理任务管理
    
    async def handle_message(self, user_id: int, message_data: dict) -> dict:
        """处理AI对话消息"""
        try:
            # 验证消息格式
            if not isinstance(message_data, dict):
                return {"success": False, "error": "消息格式无效"}
            
            message_type_str = message_data.get("type")
            if not message_type_str:
                return {"success": False, "error": "缺少消息类型"}
            
            # 转换为枚举类型
            try:
                message_type = MessageType(message_type_str)
            except ValueError:
                return {"success": False, "error": f"未知消息类型: {message_type_str}"}
            
            log_operation_start("处理增强版AI消息", user_id=user_id, message_type=message_type.value)
            
            # 构建用户输入对象
            user_input = UserInput(
                user_id=user_id,
                message_type=message_type,
                content=message_data.get("content"),
                conversation_id=message_data.get("conversation_id"),
                ai_character_id=message_data.get("ai_character_id"),
                message_id=message_data.get("message_id"),
                metadata=message_data.get("metadata", {}),
                timestamp=datetime.utcnow()
            )
            
            # 根据消息类型选择处理方式
            if message_type == MessageType.CHAT_MESSAGE:
                return await self._handle_chat_message(user_input)
            elif message_type == MessageType.START_AI_SESSION:
                return await self._handle_start_ai_session(user_input)
            elif message_type == MessageType.END_AI_SESSION:
                return await self._handle_end_ai_session(user_input)
            elif message_type == MessageType.GET_CONVERSATION_HISTORY:
                return await self._handle_get_history(user_input)
            elif message_type == MessageType.GET_AI_CHARACTERS:
                return await self._handle_get_ai_characters(user_input)
            elif message_type == MessageType.PING:
                return await self._handle_ping(user_input)
            elif message_type == MessageType.GET_USER_STATE:
                return await self._handle_get_user_state(user_input)
            elif message_type == MessageType.UPDATE_USER_PREFERENCES:
                return await self._handle_update_user_preferences(user_input)
            elif message_type == MessageType.SWITCH_AI_CHARACTER:
                return await self._handle_switch_ai_character(user_input)
            else:
                return {"success": False, "error": f"不支持的消息类型: {message_type.value}"}
                
        except Exception as e:
            log_operation_error("处理增强版AI消息", str(e), user_id=user_id)
            return {"success": False, "error": "服务器内部错误"}
    
    async def _handle_chat_message(self, user_input: UserInput) -> dict:
        """处理聊天消息"""
        log_operation_start("处理聊天消息", user_id=user_input.user_id, 
                          conversation_id=user_input.conversation_id)
        
        try:
            # 验证输入
            if not user_input.content or not user_input.content.strip():
                return {"success": False, "error": "消息内容不能为空"}
            
            if not user_input.conversation_id:
                return {"success": False, "error": "缺少会话ID"}
            
            if len(user_input.content) > 10000:
                return {"success": False, "error": "消息内容过长，请控制在10000字符以内"}
            
            # 验证会话和AI角色
            conversation, ai_character = await self._validate_conversation_and_character(
                user_input.conversation_id, user_input.user_id
            )
            
            if not conversation:
                return {"success": False, "error": "会话不存在或无权限"}
            
            if not ai_character:
                return {"success": False, "error": "AI角色不存在"}
            
            # 设置AI角色ID
            user_input.ai_character_id = ai_character['character_id']
            
            # 检查AI会话状态
            current_ai_session = ai_manager.get_user_ai_session(user_input.user_id)
            if not current_ai_session:
                # 自动建立AI会话
                success = await ai_manager.start_ai_session(user_input.user_id, ai_character['character_id'])
                if not success:
                    return {"success": False, "error": "无法建立AI会话"}
            
            # 保存用户消息
            user_message_id = user_input.message_id or str(uuid.uuid4())
            await self._save_user_message(
                user_message_id, user_input.conversation_id, 
                user_input.user_id, user_input.content, ai_character['character_id']
            )
            
            # 发送用户消息确认
            await ai_manager.send_to_user(user_input.user_id, {
                "type": "user_message_sent",
                "message_id": user_message_id,
                "content": user_input.content.strip(),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
            # 检查是否已有AI处理任务在进行
            existing_task = ai_manager.get_ai_processing_task(user_input.user_id)
            if existing_task and not existing_task.done():
                # 取消之前的任务
                existing_task.cancel()
                try:
                    await existing_task
                except asyncio.CancelledError:
                    pass
            
            # 使用统一流程处理模块处理AI回复
            ai_message_id = str(uuid.uuid4())
            user_input.message_id = ai_message_id
            
            # 异步处理AI回复
            task = asyncio.create_task(
                self._process_ai_reply_with_flow_processor(user_input, ai_message_id)
            )
            ai_manager.set_ai_processing_task(user_input.user_id, task)
            
            log_operation_success("处理聊天消息", user_id=user_input.user_id, message_id=user_message_id)
            return {
                "success": True,
                "message_id": user_message_id,
                "conversation_id": user_input.conversation_id,
                "ai_processing": True
            }
            
        except Exception as e:
            log_operation_error("处理聊天消息", str(e), user_id=user_input.user_id)
            return {"success": False, "error": f"处理消息失败: {str(e)}"}
    
    async def _process_ai_reply_with_flow_processor(self, user_input: UserInput, ai_message_id: str):
        """使用统一流程处理模块处理AI回复"""
        try:
            # 发送AI回复开始信号
            await ai_manager.send_ai_stream_start(user_input.user_id, ai_message_id)
            
            # 使用统一流程处理模块
            ai_response = await self.flow_processor.process_user_input(user_input)
            
            # 处理流式响应
            if ai_response.is_streaming:
                # 将响应分块发送
                chunks = self._split_into_chunks(ai_response.content, chunk_size=50)
                
                for i, chunk in enumerate(chunks):
                    await ai_manager.send_ai_stream_chunk(user_input.user_id, ai_message_id, chunk)
                    if i < len(chunks) - 1:
                        await asyncio.sleep(0.1)
            else:
                # 直接发送完整响应
                await ai_manager.send_ai_stream_chunk(user_input.user_id, ai_message_id, ai_response.content)
            
            # 保存AI回复到数据库
            await self._save_ai_message(
                ai_message_id, user_input.conversation_id, 
                user_input.user_id, ai_response.content, user_input.ai_character_id
            )
            
            # 发送AI回复结束信号
            await ai_manager.send_ai_stream_end(user_input.user_id, ai_message_id, ai_response.content)
            
            # 更新统计
            ai_manager.stats["ai_replies"] += 1
            
            log_operation_success("AI回复处理", user_id=user_input.user_id, message_id=ai_message_id)
            
        except Exception as e:
            log_operation_error("AI回复处理", str(e), user_id=user_input.user_id)
            await ai_manager.send_ai_error(user_input.user_id, f"AI回复失败: {str(e)}")
        finally:
            ai_manager.clear_ai_processing_task(user_input.user_id)
    
    async def _handle_start_ai_session(self, user_input: UserInput) -> dict:
        """处理开始AI会话请求"""
        ai_character_id = user_input.ai_character_id
        
        if not ai_character_id:
            return {"success": False, "error": "缺少AI角色ID"}
        
        try:
            with get_db_session() as db:
                # 验证AI角色
                ai_character = db.query(AICharacter).filter(
                    AICharacter.character_id == ai_character_id,
                    AICharacter.status == 1
                ).first()
                
                if not ai_character:
                    return {"success": False, "error": "AI角色不存在"}
                
                # 获取或创建会话
                conversation_id = user_input.conversation_id
                if not conversation_id:
                    conversation_id = str(uuid.uuid4())
                    conversation_name = f"与{ai_character.nickname}的对话"
                    
                    conversation = Conversation(
                        conversation_id=conversation_id,
                        user1_id=user_input.user_id,
                        user2_id=0,
                        conversation_name=conversation_name,
                        conversation_type='user_ai',
                        ai_character_id=ai_character_id,
                        status=1
                    )
                    
                    db.add(conversation)
                    db.commit()
                    db.refresh(conversation)
                
                # 启动AI会话
                success = await ai_manager.start_ai_session(user_input.user_id, ai_character_id)
                
                if success:
                    # 使用统一流程处理模块初始化会话状态
                    init_user_input = UserInput(
                        user_id=user_input.user_id,
                        message_type=MessageType.START_AI_SESSION,
                        content=f"开始与{ai_character.nickname}的对话",
                        conversation_id=conversation_id,
                        ai_character_id=ai_character_id
                    )
                    
                    # 初始化状态（不生成回复）
                    await self.flow_processor.state_manager.update_state(
                        user_id=user_input.user_id,
                        conversation_id=conversation_id,
                        parsed_input=await self.flow_processor.input_parser.parse(init_user_input)
                    )
                
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
            log_operation_error("开始AI会话", str(e), user_id=user_input.user_id)
            return {"success": False, "error": f"开始AI会话失败: {str(e)}"}
    
    async def _handle_end_ai_session(self, user_input: UserInput) -> dict:
        """处理结束AI会话请求"""
        success = await ai_manager.end_ai_session(user_input.user_id)
        
        # 清理会话状态
        if user_input.conversation_id:
            await self.flow_processor.state_manager.update_conversation_state(
                user_id=user_input.user_id,
                conversation_id=user_input.conversation_id,
                ai_response=None,
                decision=None
            )
        
        return {"success": success}
    
    async def _handle_get_history(self, user_input: UserInput) -> dict:
        """处理获取历史消息请求"""
        conversation_id = user_input.conversation_id
        
        if not conversation_id:
            return {"success": False, "error": "缺少会话ID"}
        
        try:
            with get_db_session() as db:
                # 验证会话权限
                conversation = db.query(Conversation).filter(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user1_id == user_input.user_id,
                    Conversation.status == 1
                ).first()
                
                if not conversation:
                    return {"success": False, "error": "会话不存在或无权限"}
                
                # 获取历史消息
                messages = db.query(Message).filter(
                    Message.conversation_id == conversation_id,
                    Message.is_deleted == 0
                ).order_by(Message.create_time.desc()).limit(20).all()
                
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
                    "messages": message_list
                }
                
        except Exception as e:
            log_operation_error("获取历史消息", str(e), user_id=user_input.user_id)
            return {"success": False, "error": f"获取历史消息失败: {str(e)}"}
    
    async def _handle_get_ai_characters(self, user_input: UserInput) -> dict:
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
            log_operation_error("获取AI角色列表", str(e), user_id=user_input.user_id)
            return {"success": False, "error": f"获取AI角色列表失败: {str(e)}"}
    
    async def _handle_ping(self, user_input: UserInput) -> dict:
        """处理心跳检测"""
        return {
            "success": True,
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    async def _handle_get_user_state(self, user_input: UserInput) -> dict:
        """处理获取用户状态请求"""
        try:
            # 获取用户状态
            state = await self.flow_processor.state_manager.get_conversation_state(
                user_input.user_id, user_input.conversation_id
            )
            
            return {
                "success": True,
                "user_state": {
                    "user_id": user_input.user_id,
                    "conversation_id": user_input.conversation_id,
                    "role_cognition": state.role_cognition,
                    "interaction_dynamics": state.interaction_dynamics,
                    "expression_rules": state.expression_rules,
                    "capability_permissions": state.capability_permissions,
                    "environment_scenario": state.environment_scenario,
                    "dynamic_adjustment": state.dynamic_adjustment,
                    "emotion_chain": state.emotion_chain[-5:],  # 最近5个情绪
                    "interaction_history": state.interaction_history[-10:]  # 最近10个交互
                }
            }
            
        except Exception as e:
            log_operation_error("获取用户状态", str(e), user_id=user_input.user_id)
            return {"success": False, "error": f"获取用户状态失败: {str(e)}"}
    
    async def _handle_update_user_preferences(self, user_input: UserInput) -> dict:
        """处理更新用户偏好请求"""
        try:
            preferences = user_input.metadata.get("preferences", {})
            
            if not preferences:
                return {"success": False, "error": "缺少偏好数据"}
            
            # 更新用户偏好（这里可以扩展为数据库操作）
            # 目前简化为缓存更新
            cache_key = f"user_preferences:{user_input.user_id}"
            cache_set(cache_key, preferences, ttl=3600)  # 缓存1小时
            
            return {
                "success": True,
                "message": "用户偏好已更新",
                "preferences": preferences
            }
            
        except Exception as e:
            log_operation_error("更新用户偏好", str(e), user_id=user_input.user_id)
            return {"success": False, "error": f"更新用户偏好失败: {str(e)}"}
    
    async def _handle_switch_ai_character(self, user_input: UserInput) -> dict:
        """处理切换AI角色请求"""
        new_character_id = user_input.ai_character_id
        
        if not new_character_id:
            return {"success": False, "error": "缺少AI角色ID"}
        
        try:
            with get_db_session() as db:
                # 验证新AI角色
                new_character = db.query(AICharacter).filter(
                    AICharacter.character_id == new_character_id,
                    AICharacter.status == 1
                ).first()
                
                if not new_character:
                    return {"success": False, "error": "AI角色不存在"}
                
                # 切换AI角色
                success = await ai_manager.start_ai_session(user_input.user_id, new_character_id)
                
                if success:
                    # 清理旧状态，初始化新状态
                    if user_input.conversation_id:
                        await self.flow_processor.state_manager.update_conversation_state(
                            user_id=user_input.user_id,
                            conversation_id=user_input.conversation_id,
                            ai_response=None,
                            decision=None
                        )
                    
                    # 初始化新角色状态
                    switch_user_input = UserInput(
                        user_id=user_input.user_id,
                        message_type=MessageType.SWITCH_AI_CHARACTER,
                        content=f"切换到{new_character.nickname}",
                        conversation_id=user_input.conversation_id,
                        ai_character_id=new_character_id
                    )
                    
                    await self.flow_processor.state_manager.update_state(
                        user_id=user_input.user_id,
                        conversation_id=user_input.conversation_id,
                        parsed_input=await self.flow_processor.input_parser.parse(switch_user_input)
                    )
                
                return {
                    "success": success,
                    "new_character": {
                        "character_id": new_character.character_id,
                        "nickname": new_character.nickname,
                        "description": new_character.description,
                        "personality": new_character.personality
                    }
                }
                
        except Exception as e:
            log_operation_error("切换AI角色", str(e), user_id=user_input.user_id)
            return {"success": False, "error": f"切换AI角色失败: {str(e)}"}
    
    async def _validate_conversation_and_character(self, conversation_id: str, user_id: int) -> tuple:
        """验证会话和AI角色"""
        try:
            with get_db_session() as db:
                # 验证会话
                conversation = db.query(Conversation).filter(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user1_id == user_id,
                    Conversation.conversation_type == 'user_ai',
                    Conversation.status == 1
                ).first()
                
                if not conversation:
                    return None, None
                
                # 获取AI角色信息
                ai_character = db.query(AICharacter).filter(
                    AICharacter.character_id == conversation.ai_character_id,
                    AICharacter.status == 1
                ).first()
                
                if not ai_character:
                    return None, None
                
                # 在会话关闭前提取所需的数据，避免会话绑定错误
                conversation_data = {
                    'conversation_id': conversation.conversation_id,
                    'user1_id': conversation.user1_id,
                    'conversation_type': conversation.conversation_type,
                    'ai_character_id': conversation.ai_character_id,
                    'status': conversation.status
                }
                
                ai_character_data = {
                    'character_id': ai_character.character_id,
                    'nickname': ai_character.nickname,
                    'description': ai_character.description,
                    'personality': ai_character.personality,
                    'status': ai_character.status
                }
                
                return conversation_data, ai_character_data
                
        except Exception as e:
            logger.error(f"验证会话和角色失败: {e}")
            return None, None
    
    async def _save_user_message(self, message_id: str, conversation_id: str, 
                                user_id: int, content: str, ai_character_id: str):
        """保存用户消息"""
        try:
            with get_db_session() as db:
                user_message = Message(
                    message_id=message_id,
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    receiver_id=0,
                    content=content.strip(),
                    message_type='text',
                    is_ai_message=False,
                    ai_character_id=ai_character_id
                )
                
                db.add(user_message)
                db.commit()
                
        except Exception as e:
            logger.error(f"保存用户消息失败: {e}")
    
    async def _save_ai_message(self, message_id: str, conversation_id: str, 
                              user_id: int, content: str, ai_character_id: str):
        """保存AI消息"""
        try:
            with get_db_session() as db:
                ai_message = Message(
                    message_id=message_id,
                    conversation_id=conversation_id,
                    sender_id=0,
                    receiver_id=user_id,
                    content=content,
                    message_type='text',
                    is_ai_message=True,
                    ai_character_id=ai_character_id
                )
                
                db.add(ai_message)
                
                # 更新会话的最后消息信息
                conversation = db.query(Conversation).filter(
                    Conversation.conversation_id == conversation_id
                ).first()
                
                if conversation:
                    conversation.last_message_id = ai_message.id
                    conversation.last_message_time = datetime.utcnow()
                
                # 增加AI角色使用次数
                ai_character = db.query(AICharacter).filter(
                    AICharacter.character_id == ai_character_id
                ).first()
                
                if ai_character:
                    ai_character.usage_count += 1
                
                db.commit()
                
        except Exception as e:
            logger.error(f"保存AI消息失败: {e}")
    
    def _split_into_chunks(self, text: str, chunk_size: int = 50) -> list:
        """将文本分割成流式片段"""
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks
    
    async def get_flow_processor_stats(self) -> dict:
        """获取流程处理器统计信息"""
        return self.flow_processor.get_stats()
    
    async def health_check(self) -> dict:
        """健康检查"""
        try:
            # 检查流程处理器健康状态
            flow_health = await self.flow_processor.health_check()
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "flow_processor": flow_health,
                "active_sessions": len(self.active_sessions),
                "processing_tasks": len(self.processing_tasks)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# 全局增强版AI消息处理器实例
enhanced_ai_handler = EnhancedAIMessageHandler()
