"""
EchoSoul AI Platform AI Character Models
AI角色系统相关的数据模型
"""

from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Text, Boolean, Enum
from sqlalchemy.sql import func
from app.db import get_database_base

Base = get_database_base()

class AICharacter(Base):
    """AI角色信息表模型"""
    __tablename__ = "ai_character"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="AI角色ID")
    character_id = Column(String(32), nullable=False, unique=True, comment="AI角色唯一标识")
    name = Column(String(100), nullable=False, comment="角色名称")
    nickname = Column(String(100), nullable=False, comment="角色昵称")
    avatar = Column(String(500), nullable=True, comment="角色头像URL")
    description = Column(Text, nullable=True, comment="角色描述")
    personality = Column(Text, nullable=True, comment="人设描述")
    background_story = Column(Text, nullable=True, comment="背景故事")
    speaking_style = Column(Text, nullable=True, comment="说话风格")
    creator_id = Column(BigInteger, nullable=False, comment="创建者用户ID")
    is_public = Column(Boolean, default=False, comment="是否公开")
    status = Column(Integer, default=1, comment="状态：1-正常，0-禁用")
    usage_count = Column(Integer, default=0, comment="使用次数")
    like_count = Column(Integer, default=0, comment="点赞数")
    create_time = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
    
    def __repr__(self):
        return f"<AICharacter(id={self.id}, character_id='{self.character_id}', name='{self.name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "character_id": self.character_id,
            "name": self.name,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "description": self.description,
            "personality": self.personality,
            "background_story": self.background_story,
            "speaking_style": self.speaking_style,
            "creator_id": self.creator_id,
            "is_public": self.is_public,
            "status": self.status,
            "usage_count": self.usage_count,
            "like_count": self.like_count,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None
        }

class UserAIRelation(Base):
    """用户与AI角色关联关系表模型"""
    __tablename__ = "user_ai_relation"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="关系ID")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    character_id = Column(String(32), nullable=False, comment="AI角色ID")
    relation_type = Column(Enum('created', 'favorited', 'blocked', name='relation_type_enum'), 
                          nullable=False, comment="关系类型")
    create_time = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    
    def __repr__(self):
        return f"<UserAIRelation(id={self.id}, user_id={self.user_id}, character_id='{self.character_id}', relation_type='{self.relation_type}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "relation_type": self.relation_type,
            "create_time": self.create_time.isoformat() if self.create_time else None
        }
