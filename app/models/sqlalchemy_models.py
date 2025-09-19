"""
EchoSoul AI Platform Database Models
SQLAlchemy models for the application
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.db import get_database_base

Base = get_database_base()

# User模型已移除，使用auth_users表中的AuthUser模型

class AIRequest(Base):
    """AI请求记录模型"""
    __tablename__ = "ai_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # 关联用户ID
    request_type = Column(String(50), nullable=False)  # 请求类型：chat, image, etc.
    prompt = Column(Text, nullable=False)  # 用户输入
    response = Column(Text, nullable=True)  # AI响应
    status = Column(String(20), default="pending")  # pending, completed, failed
    tokens_used = Column(Integer, default=0)  # 使用的token数量
    processing_time = Column(Float, default=0.0)  # 处理时间（秒）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SystemLog(Base):
    """系统日志模型"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    module = Column(String(50), nullable=True)  # 模块名称
    user_id = Column(Integer, nullable=True)  # 关联用户ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
