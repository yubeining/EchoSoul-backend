"""
EchoSoul AI Platform Models Package
统一导入所有数据模型
"""

# 导入所有模型以确保它们被注册到SQLAlchemy
from .user_models import AuthUser
from .chat_models import Conversation, Message
from .ai_character_models import AICharacter, UserAIRelation
from .sqlalchemy_models import Base

__all__ = [
    "AuthUser",
    "Conversation", 
    "Message",
    "AICharacter",
    "UserAIRelation",
    "Base"
]
