"""
EchoSoul AI Platform CRUD Operations
Database operations for all models
"""

from sqlalchemy.orm import Session
from app.models.user_models import AuthUser

# User CRUD operations - 已移除，使用auth_users表中的AuthUser模型
# 用户管理功能通过auth_service.py中的AuthUser模型实现

# AI Request 和 System Log CRUD operations 已移除，因为项目中没有实际使用这些表

# Statistics functions
def get_user_count(db: Session) -> int:
    return db.query(AuthUser).count()
