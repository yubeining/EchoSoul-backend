"""
EchoSoul AI Platform 通用响应模型
Common response models for all API endpoints
"""

from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """统一的基础响应模型"""
    code: int = 200
    msg: str = "success"
    data: Optional[T] = None

class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str
    success: bool = True

class DatabaseStatusResponse(BaseModel):
    """数据库状态响应模型"""
    connected: bool
    message: str
    tables_created: bool = False

class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = 1
    limit: int = 20
    
    def __init__(self, page: int = 1, limit: int = 20, **data):
        super().__init__(page=page, limit=limit, **data)

class PaginationInfo(BaseModel):
    """分页信息模型"""
    current_page: int
    total_pages: int
    total_count: int
    has_next: bool
    has_prev: bool
    limit: int = 20

class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int
    msg: str
    detail: Optional[str] = None
    timestamp: Optional[str] = None
