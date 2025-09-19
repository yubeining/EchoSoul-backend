"""
EchoSoul AI Platform Pydantic Schemas
Request and response models for API endpoints
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# User schemas 已移除，项目使用 auth_schemas.py 中的认证相关schemas

# AI Request 和 System Log schemas 已移除，因为项目中没有实际使用这些表

# Generic response schemas
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class DatabaseStatusResponse(BaseModel):
    connected: bool
    message: str
    tables_created: bool = False
