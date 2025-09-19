"""
EchoSoul AI Platform Database Models
SQLAlchemy models for the application
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.db import get_database_base

Base = get_database_base()

# User模型已移除，使用auth_users表中的AuthUser模型

# AIRequest 和 SystemLog 模型已移除，因为项目中没有实际使用这些表
