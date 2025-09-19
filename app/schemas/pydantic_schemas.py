"""
EchoSoul AI Platform Pydantic Schemas
Request and response models for API endpoints
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# AI Request 和 System Log schemas 已移除，因为项目中没有实际使用这些表

# Generic response schemas
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class DatabaseStatusResponse(BaseModel):
    connected: bool
    message: str
    tables_created: bool = False
