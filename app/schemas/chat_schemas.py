"""
EchoSoul AI Platform Chat Schemas
聊天系统相关的Pydantic数据验证模型
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    """消息类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    FILE = "file"
    EMOJI = "emoji"

# 会话相关schemas
class GetOrCreateConversationRequest(BaseModel):
    """获取或创建会话请求"""
    target_user_id: int
    
    @validator('target_user_id')
    def validate_target_user_id(cls, v):
        if v <= 0:
            raise ValueError('目标用户ID必须大于0')
        return v

class ConversationResponse(BaseModel):
    """会话响应"""
    id: int
    conversation_id: str
    user1_id: int
    user2_id: int
    conversation_name: Optional[str] = None
    last_message_id: Optional[int] = None
    last_message_time: Optional[datetime] = None
    status: int
    create_time: datetime
    update_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    """会话列表响应"""
    conversations: List[ConversationResponse]
    total: int
    page: int
    limit: int

# 消息相关schemas
class SendMessageRequest(BaseModel):
    """发送消息请求"""
    conversation_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    reply_to_message_id: Optional[str] = None
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('消息内容不能为空')
        if len(v) > 10000:
            raise ValueError('消息内容不能超过10000个字符')
        return v.strip()
    
    @validator('conversation_id')
    def validate_conversation_id(cls, v):
        if not v or not v.strip():
            raise ValueError('会话ID不能为空')
        return v.strip()

class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    message_id: str
    conversation_id: str
    sender_id: int
    receiver_id: int
    content: str
    message_type: MessageType
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    is_deleted: int
    reply_to_message_id: Optional[str] = None
    create_time: datetime
    update_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    """消息列表响应"""
    messages: List[MessageResponse]
    total: int
    page: int
    limit: int

# 通用响应schemas
class ChatBaseResponse(BaseModel):
    """聊天系统基础响应"""
    code: int
    msg: str
    data: Optional[dict] = None

class GetOrCreateConversationResponse(ChatBaseResponse):
    """获取或创建会话响应"""
    data: Optional[ConversationResponse] = None

class SendMessageResponse(ChatBaseResponse):
    """发送消息响应"""
    data: Optional[MessageResponse] = None

class ConversationListBaseResponse(ChatBaseResponse):
    """会话列表基础响应"""
    data: Optional[ConversationListResponse] = None

class ConversationBaseResponse(ChatBaseResponse):
    """会话详情基础响应"""
    data: Optional[ConversationResponse] = None

class MessageListBaseResponse(ChatBaseResponse):
    """消息列表基础响应"""
    data: Optional[MessageListResponse] = None

class MessageBaseResponse(ChatBaseResponse):
    """单条消息基础响应"""
    data: Optional[MessageResponse] = None
