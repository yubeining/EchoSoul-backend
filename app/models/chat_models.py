"""
EchoSoul AI Platform Chat Models
聊天系统相关的数据模型
"""

from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import get_database_base

Base = get_database_base()

class Conversation(Base):
    """会话表模型"""
    __tablename__ = "conversations"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="会话ID")
    conversation_id = Column(String(36), nullable=False, unique=True, comment="会话唯一标识符，UUID格式")
    user1_id = Column(BigInteger, nullable=False, comment="用户1的ID")
    user2_id = Column(BigInteger, nullable=False, comment="用户2的ID")
    conversation_name = Column(String(100), nullable=True, comment="会话名称（可自定义，默认为对方昵称）")
    last_message_id = Column(BigInteger, nullable=True, comment="最后一条消息ID")
    last_message_time = Column(DateTime, nullable=True, comment="最后消息时间")
    status = Column(Integer, default=1, comment="会话状态：1-正常，0-已删除")
    create_time = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
    
    # 关联关系已移除，避免复杂的外键映射问题
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, conversation_id='{self.conversation_id}', user1_id={self.user1_id}, user2_id={self.user2_id})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "user1_id": self.user1_id,
            "user2_id": self.user2_id,
            "conversation_name": self.conversation_name,
            "last_message_id": self.last_message_id,
            "last_message_time": self.last_message_time.isoformat() if self.last_message_time else None,
            "status": self.status,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None
        }

class Message(Base):
    """消息表模型"""
    __tablename__ = "messages"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="消息ID")
    message_id = Column(String(36), nullable=False, unique=True, comment="消息唯一标识符，UUID格式")
    conversation_id = Column(String(36), nullable=False, comment="所属会话ID")
    sender_id = Column(BigInteger, nullable=False, comment="发送者用户ID")
    receiver_id = Column(BigInteger, nullable=False, comment="接收者用户ID")
    content = Column(Text, nullable=False, comment="消息内容")
    message_type = Column(Enum('text', 'image', 'voice', 'video', 'file', 'emoji', name='message_type_enum'), 
                         default='text', comment="消息类型")
    file_url = Column(String(500), nullable=True, comment="文件URL（图片、语音、视频、文件）")
    file_name = Column(String(255), nullable=True, comment="文件名")
    file_size = Column(BigInteger, nullable=True, comment="文件大小（字节）")
    is_deleted = Column(Integer, default=0, comment="是否删除：1-已删除，0-正常")
    reply_to_message_id = Column(String(36), nullable=True, comment="回复的消息ID")
    create_time = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
    
    # 关联关系已移除，避免复杂的外键映射问题
    
    def __repr__(self):
        return f"<Message(id={self.id}, message_id='{self.message_id}', sender_id={self.sender_id}, content='{self.content[:50]}...')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "message_type": self.message_type,
            "file_url": self.file_url,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "is_deleted": self.is_deleted,
            "reply_to_message_id": self.reply_to_message_id,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None
        }
