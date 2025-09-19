"""
EchoSoul AI Platform Chat Service
聊天系统业务逻辑服务
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import Optional, Tuple, List
import uuid
from datetime import datetime

from app.models.chat_models import Conversation, Message
from app.models.user_models import AuthUser
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
        """发送消息"""
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
                reply_to_message_id=request.reply_to_message_id
            )
            
            db.add(new_message)
            
            # 更新会话的最后消息信息
            conversation.last_message_id = new_message.id
            conversation.last_message_time = datetime.utcnow()
            
            db.commit()
            db.refresh(new_message)
            
            return True, "发送消息成功", MessageResponse.from_orm(new_message)
            
        except Exception as e:
            db.rollback()
            return False, f"发送消息失败: {str(e)}", None
    
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
