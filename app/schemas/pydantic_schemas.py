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

# AI Request schemas
class AIRequestBase(BaseModel):
    request_type: str
    prompt: str
    user_id: Optional[int] = None

class AIRequestCreate(AIRequestBase):
    pass

class AIRequestUpdate(BaseModel):
    response: Optional[str] = None
    status: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None

class AIRequestResponse(AIRequestBase):
    id: int
    response: Optional[str] = None
    status: str
    tokens_used: int
    processing_time: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# System Log schemas
class SystemLogBase(BaseModel):
    level: str
    message: str
    module: Optional[str] = None
    user_id: Optional[int] = None

class SystemLogCreate(SystemLogBase):
    pass

class SystemLogResponse(SystemLogBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Generic response schemas
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class DatabaseStatusResponse(BaseModel):
    connected: bool
    message: str
    tables_created: bool = False
