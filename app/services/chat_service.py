"""
EchoSoul AI Platform Chat Service
聊天系统业务逻辑服务
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import Optional, Tuple, List, Dict
import uuid
from datetime import datetime

from app.models.chat_models import Conversation, Message
from app.models.user_models import AuthUser
from app.models.ai_character_models import AICharacter
from app.schemas.chat_schemas import (
    GetOrCreateConversationRequest, SendMessageRequest,
    ConversationResponse, MessageResponse, MessageType
)

class ChatService:
    """聊天服务类"""
    
    @staticmethod
    def get_or_create_conversation(
        db: Session, 
        current_user_id: int, 
        request: GetOrCreateConversationRequest
    ) -> Tuple[bool, str, Optional[ConversationResponse]]:
        """获取或创建会话"""
        try:
            # 检查目标用户是否存在
            target_user = db.query(AuthUser).filter(
                AuthUser.id == request.target_user_id,
                AuthUser.status == 1
            ).first()
            
            if not target_user:
                return False, "目标用户不存在", None
            
            if current_user_id == request.target_user_id:
                return False, "不能与自己创建会话", None
            
            # 确定user1_id和user2_id（保证一致性）
            user1_id = min(current_user_id, request.target_user_id)
            user2_id = max(current_user_id, request.target_user_id)
            
            # 查找现有会话
            conversation = db.query(Conversation).filter(
                and_(
                    Conversation.user1_id == user1_id,
                    Conversation.user2_id == user2_id,
                    Conversation.status == 1
                )
            ).first()
            
            if conversation:
                # 返回现有会话
                return True, "获取会话成功", ConversationResponse.from_orm(conversation)
            
            # 创建新会话
            conversation_id = str(uuid.uuid4())
            conversation_name = target_user.nickname or target_user.username
            
            new_conversation = Conversation(
                conversation_id=conversation_id,
                user1_id=user1_id,
                user2_id=user2_id,
                conversation_name=conversation_name,
                status=1
            )
            
            db.add(new_conversation)
            db.commit()
            db.refresh(new_conversation)
            
            return True, "创建会话成功", ConversationResponse.from_orm(new_conversation)
            
        except Exception as e:
            db.rollback()
            return False, f"操作失败: {str(e)}", None
    
    @staticmethod
    def get_user_conversations(
        db: Session, 
        current_user_id: int, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[bool, str, Optional[List[ConversationResponse]]]:
        """获取用户会话列表"""
        try:
            # 计算偏移量
            offset = (page - 1) * limit
            
            # 查询用户的会话
            conversations = db.query(Conversation).filter(
                and_(
                    or_(
                        Conversation.user1_id == current_user_id,
                        Conversation.user2_id == current_user_id
                    ),
                    Conversation.status == 1
                )
            ).order_by(desc(Conversation.last_message_time)).offset(offset).limit(limit).all()
            
            # 转换为响应格式
            conversation_responses = [
                ConversationResponse.from_orm(conv) for conv in conversations
            ]
            
            return True, "获取会话列表成功", conversation_responses
            
        except Exception as e:
            return False, f"获取会话列表失败: {str(e)}", None
    
    @staticmethod
    def send_message(
        db: Session, 
        current_user_id: int, 
        request: SendMessageRequest
    ) -> Tuple[bool, str, Optional[MessageResponse]]:
        """发送消息（支持用户间聊天和AI聊天）"""
        try:
            # 检查会话是否存在
            conversation = db.query(Conversation).filter(
                and_(
                    Conversation.conversation_id == request.conversation_id,
                    Conversation.status == 1
                )
            ).first()
            
            if not conversation:
                return False, "会话不存在", None
            
            # 检查用户是否参与此会话
            if current_user_id not in [conversation.user1_id, conversation.user2_id]:
                return False, "无权限在此会话中发送消息", None
            
            # 判断是否为AI会话
            if conversation.conversation_type == 'user_ai':
                # 处理AI会话
                return ChatService._handle_ai_conversation(db, conversation, current_user_id, request)
            else:
                # 处理普通用户间会话
                return ChatService._handle_user_conversation(db, conversation, current_user_id, request)
            
        except Exception as e:
            db.rollback()
            return False, f"发送消息失败: {str(e)}", None
    
    @staticmethod
    def _handle_user_conversation(
        db: Session,
        conversation: Conversation,
        current_user_id: int,
        request: SendMessageRequest
    ) -> Tuple[bool, str, Optional[MessageResponse]]:
        """处理用户间会话"""
        try:
            # 确定接收者ID
            receiver_id = conversation.user2_id if current_user_id == conversation.user1_id else conversation.user1_id
            
            # 创建消息
            message_id = str(uuid.uuid4())
            new_message = Message(
                message_id=message_id,
                conversation_id=request.conversation_id,
                sender_id=current_user_id,
                receiver_id=receiver_id,
                content=request.content,
                message_type=request.message_type.value,
                file_url=request.file_url,
                file_name=request.file_name,
                file_size=request.file_size,
                reply_to_message_id=request.reply_to_message_id,
                is_ai_message=False,
                ai_character_id=None
            )
            
            db.add(new_message)
            db.flush()
            
            # 更新会话的最后消息信息
            conversation.last_message_id = new_message.id
            conversation.last_message_time = datetime.utcnow()
            
            db.commit()
            db.refresh(new_message)
            
            return True, "发送消息成功", MessageResponse.from_orm(new_message)
            
        except Exception as e:
            db.rollback()
            return False, f"发送用户消息失败: {str(e)}", None
    
    @staticmethod
    def _handle_ai_conversation(
        db: Session,
        conversation: Conversation,
        current_user_id: int,
        request: SendMessageRequest
    ) -> Tuple[bool, str, Optional[MessageResponse]]:
        """处理AI会话"""
        try:
            # 获取AI角色信息
            ai_character = db.query(AICharacter).filter(
                and_(
                    AICharacter.character_id == conversation.ai_character_id,
                    AICharacter.status == 1
                )
            ).first()
            
            if not ai_character:
                return False, "AI角色不存在", None
            
            # 1. 保存用户消息
            user_message_id = str(uuid.uuid4())
            user_message = Message(
                message_id=user_message_id,
                conversation_id=request.conversation_id,
                sender_id=current_user_id,
                receiver_id=0,  # AI使用0作为receiver_id
                content=request.content,
                message_type=request.message_type.value,
                file_url=request.file_url,
                file_name=request.file_name,
                file_size=request.file_size,
                reply_to_message_id=request.reply_to_message_id,
                is_ai_message=False,  # 用户消息
                ai_character_id=ai_character.character_id  # 标明是发给哪个AI的消息
            )
            
            db.add(user_message)
            db.flush()
            
            # 2. 生成AI回复（集成真实LLM API）
            ai_reply = ChatService._generate_ai_reply_with_llm(request.content, ai_character, conversation.conversation_id, db)
            
            # 3. 保存AI回复
            ai_message_id = str(uuid.uuid4())
            ai_message = Message(
                message_id=ai_message_id,
                conversation_id=request.conversation_id,
                sender_id=0,  # AI使用0作为ID
                receiver_id=current_user_id,
                content=ai_reply,
                message_type='text',
                is_ai_message=True,
                ai_character_id=ai_character.character_id
            )
            
            db.add(ai_message)
            db.flush()
            
            # 4. 更新会话的最后消息信息
            conversation.last_message_id = ai_message.id
            conversation.last_message_time = datetime.utcnow()
            
            # 5. 增加AI角色使用次数
            ai_character.usage_count += 1
            
            db.commit()
            db.refresh(ai_message)
            
            return True, "AI回复成功", MessageResponse.from_orm(ai_message)
            
        except Exception as e:
            db.rollback()
            return False, f"AI会话处理失败: {str(e)}", None
    
    @staticmethod
    def get_conversation_messages(
        db: Session, 
        current_user_id: int, 
        conversation_id: str, 
        page: int = 1, 
        limit: int = 50
    ) -> Tuple[bool, str, Optional[List[MessageResponse]]]:
        """获取会话消息列表"""
        try:
            # 检查会话是否存在且用户有权限访问
            conversation = db.query(Conversation).filter(
                and_(
                    Conversation.conversation_id == conversation_id,
                    Conversation.status == 1
                )
            ).first()
            
            if not conversation:
                return False, "会话不存在", None
            
            if current_user_id not in [conversation.user1_id, conversation.user2_id]:
                return False, "无权限访问此会话", None
            
            # 计算偏移量
            offset = (page - 1) * limit
            
            # 查询消息
            messages = db.query(Message).filter(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.is_deleted == 0
                )
            ).order_by(desc(Message.create_time)).offset(offset).limit(limit).all()
            
            # 转换为响应格式
            message_responses = [
                MessageResponse.from_orm(msg) for msg in messages
            ]
            
            return True, "获取消息列表成功", message_responses
            
        except Exception as e:
            return False, f"获取消息列表失败: {str(e)}", None
    
    @staticmethod
    def get_conversation_count(db: Session, current_user_id: int) -> int:
        """获取用户会话总数"""
        return db.query(Conversation).filter(
            and_(
                or_(
                    Conversation.user1_id == current_user_id,
                    Conversation.user2_id == current_user_id
                ),
                Conversation.status == 1
            )
        ).count()
    
    @staticmethod
    def get_message_count(db: Session, conversation_id: str) -> int:
        """获取会话消息总数"""
        return db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.is_deleted == 0
            )
        ).count()
    
    @staticmethod
    def send_ai_message(db: Session, conversation_id: str, user_message: str, user_id: int) -> Tuple[bool, str, Optional[MessageResponse]]:
        """发送消息到AI角色并获取AI回复"""
        try:
            # 获取会话信息
            conversation = db.query(Conversation).filter(
                and_(
                    Conversation.conversation_id == conversation_id,
                    Conversation.status == 1,
                    Conversation.conversation_type == 'user_ai'
                )
            ).first()
            
            if not conversation:
                return False, "会话不存在", None
            
            # 检查用户是否有权限发送消息
            if conversation.user1_id != user_id:
                return False, "无权限发送消息", None
            
            # 获取AI角色信息
            ai_character = db.query(AICharacter).filter(
                and_(
                    AICharacter.character_id == conversation.ai_character_id,
                    AICharacter.status == 1
                )
            ).first()
            
            if not ai_character:
                return False, "AI角色不存在", None
            
            # 1. 保存用户消息
            user_message_id = str(uuid.uuid4())
            user_message_obj = Message(
                message_id=user_message_id,
                conversation_id=conversation_id,
                sender_id=user_id,
                receiver_id=0,  # AI使用0作为ID
                content=user_message,
                message_type='text',
                is_ai_message=False,
                ai_character_id=None
            )
            
            db.add(user_message_obj)
            db.flush()  # 刷新以获取用户消息ID
            
            # 2. 生成AI回复（这里可以集成真实的AI服务）
            ai_reply = ChatService._generate_ai_reply(user_message, ai_character)
            
            # 3. 保存AI回复
            ai_message_id = str(uuid.uuid4())
            ai_message_obj = Message(
                message_id=ai_message_id,
                conversation_id=conversation_id,
                sender_id=0,  # AI使用0作为ID
                receiver_id=user_id,
                content=ai_reply,
                message_type='text',
                is_ai_message=True,
                ai_character_id=ai_character.character_id
            )
            
            db.add(ai_message_obj)
            db.flush()  # 刷新以获取AI消息ID
            
            # 4. 更新会话的最后消息信息
            conversation.last_message_id = ai_message_obj.id
            conversation.last_message_time = datetime.utcnow()
            
            # 5. 增加AI角色使用次数
            ai_character.usage_count += 1
            
            db.commit()
            db.refresh(ai_message_obj)
            
            return True, "消息发送成功", MessageResponse.from_orm(ai_message_obj)
            
        except Exception as e:
            db.rollback()
            return False, f"发送消息失败: {str(e)}", None
    
    @staticmethod
    def _generate_ai_reply_with_llm(
        user_message: str, 
        ai_character: AICharacter, 
        conversation_id: str,
        db: Session
    ) -> str:
        """生成AI回复（集成真实LLM API）"""
        try:
            # 导入LLM服务
            from app.services.llm_service import LLMService
            
            # 获取对话历史（最近10条消息）
            conversation_history = ChatService._get_conversation_history_for_llm(
                db, conversation_id, limit=10
            )
            
            # 调用LLM服务（使用同步方式）
            try:
                import asyncio
                # 创建新的事件循环来运行异步函数
                ai_reply = asyncio.run(
                    LLMService.chat_with_character(
                        user_message=request.content,
                        character_name=ai_character.nickname,
                        character_personality=ai_character.personality,
                        conversation_history=conversation_history,
                        max_tokens=512,
                        temperature=0.8
                    )
                )
            except Exception as e:
                # 如果异步调用失败，使用降级回复
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"LLM API调用失败: {str(e)}")
                ai_reply = None
            
            if ai_reply:
                return ai_reply
            else:
                # 如果LLM调用失败，使用降级回复
                return ChatService._generate_fallback_reply(user_message, ai_character)
                
        except Exception as e:
            # 记录错误日志
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"LLM API调用失败: {str(e)}")
            
            # 使用降级回复
            return ChatService._generate_fallback_reply(user_message, ai_character)
    
    @staticmethod
    def _get_conversation_history_for_llm(
        db: Session, 
        conversation_id: str, 
        limit: int = 10
    ) -> List[Dict[str, str]]:
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
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取对话历史失败: {str(e)}")
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
    def get_ai_conversations(db: Session, current_user_id: int, page: int = 1, limit: int = 20) -> Tuple[bool, str, Optional[List[ConversationResponse]]]:
        """获取用户的AI会话列表"""
        try:
            offset = (page - 1) * limit
            
            # 查询用户的AI会话
            conversations = db.query(Conversation).filter(
                and_(
                    Conversation.user1_id == current_user_id,
                    Conversation.conversation_type == 'user_ai',
                    Conversation.status == 1
                )
            ).order_by(desc(Conversation.last_message_time)).offset(offset).limit(limit).all()
            
            # 转换为响应格式
            conversation_responses = [
                ConversationResponse.from_orm(conv) for conv in conversations
            ]
            
            return True, "获取AI会话列表成功", conversation_responses
            
        except Exception as e:
            return False, f"获取AI会话列表失败: {str(e)}", None
    
    @staticmethod
    def get_message_by_id(
        db: Session, 
        current_user_id: int, 
        message_id: str
    ) -> Tuple[bool, str, Optional[MessageResponse]]:
        """根据消息ID获取单条消息"""
        try:
            # 查询消息
            message = db.query(Message).filter(
                and_(
                    Message.message_id == message_id,
                    Message.is_deleted == 0
                )
            ).first()
            
            if not message:
                return False, "消息不存在", None
            
            # 检查用户是否有权限访问此消息
            # 通过会话验证用户权限
            conversation = db.query(Conversation).filter(
                and_(
                    Conversation.conversation_id == message.conversation_id,
                    Conversation.status == 1
                )
            ).first()
            
            if not conversation:
                return False, "会话不存在", None
            
            # 检查用户是否参与此会话
            if current_user_id not in [conversation.user1_id, conversation.user2_id]:
                return False, "无权限访问此消息", None
            
            return True, "获取消息成功", MessageResponse.from_orm(message)
            
        except Exception as e:
            return False, f"获取消息失败: {str(e)}", None
    
    @staticmethod
    def get_message_by_id_in_conversation(
        db: Session, 
        current_user_id: int, 
        conversation_id: str,
        message_id: str
    ) -> Tuple[bool, str, Optional[MessageResponse]]:
        """根据会话ID和消息ID获取特定消息"""
        try:
            # 首先验证会话是否存在且用户有权限访问
            conversation = db.query(Conversation).filter(
                and_(
                    Conversation.conversation_id == conversation_id,
                    Conversation.status == 1
                )
            ).first()
            
            if not conversation:
                return False, "会话不存在", None
            
            # 检查用户是否参与此会话
            if current_user_id not in [conversation.user1_id, conversation.user2_id]:
                return False, "无权限访问此会话", None
            
            # 查询消息
            message = db.query(Message).filter(
                and_(
                    Message.message_id == message_id,
                    Message.conversation_id == conversation_id,
                    Message.is_deleted == 0
                )
            ).first()
            
            if not message:
                return False, "消息不存在", None
            
            return True, "获取消息成功", MessageResponse.from_orm(message)
            
        except Exception as e:
            return False, f"获取消息失败: {str(e)}", None