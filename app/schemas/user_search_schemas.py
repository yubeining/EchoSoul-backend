"""
EchoSoul AI Platform User Search Schemas
用户搜索相关的Pydantic模式
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from .common_schemas import BaseResponse, PaginationInfo

# 用户搜索请求
class UserSearchRequest(BaseModel):
    """用户搜索请求"""
    keyword: str
    page: Optional[int] = 1
    limit: Optional[int] = 20
    
    @validator('keyword')
    def validate_keyword(cls, v):
        """验证搜索关键词"""
        if not v or len(v.strip()) == 0:
            raise ValueError('搜索关键词不能为空')
        
        v = v.strip()
        if len(v) < 2:
            raise ValueError('搜索关键词至少需要2个字符')
        
        if len(v) > 50:
            raise ValueError('搜索关键词不能超过50个字符')
        
        return v
    
    @validator('page')
    def validate_page(cls, v):
        """验证页码"""
        if v is not None and v < 1:
            raise ValueError('页码必须大于0')
        return v or 1
    
    @validator('limit')
    def validate_limit(cls, v):
        """验证每页数量"""
        if v is not None:
            if v < 1:
                raise ValueError('每页数量必须大于0')
            if v > 100:
                raise ValueError('每页数量不能超过100')
        return v or 20

# 用户搜索结果
class UserSearchResult(BaseModel):
    """用户搜索结果"""
    id: int
    uid: str
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    avatar: Optional[str] = None
    intro: Optional[str] = None
    lastActive: Optional[str] = None
    createdAt: str
    
    @validator('lastActive', pre=True)
    def format_last_active(cls, v):
        """格式化最后活跃时间"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat() + 'Z'
        return v
    
    @validator('createdAt', pre=True)
    def format_created_at(cls, v):
        """格式化创建时间"""
        if isinstance(v, datetime):
            return v.isoformat() + 'Z'
        return v

# 分页信息
# PaginationInfo 已移至 common_schemas.py

# 用户搜索响应
class UserSearchResponse(BaseModel):
    """用户搜索响应"""
    users: List[UserSearchResult]
    pagination: PaginationInfo

# 用户详情响应
class UserDetailResponse(BaseModel):
    """用户详情响应"""
    user: UserSearchResult

# 基础响应
# BaseResponse 已移至 common_schemas.py

# 用户搜索基础响应
class UserSearchBaseResponse(BaseModel):
    """用户搜索基础响应"""
    code: int
    msg: str
    data: Optional[UserSearchResponse] = None

# 用户详情基础响应
class UserDetailBaseResponse(BaseModel):
    """用户详情基础响应"""
    code: int
    msg: str
    data: Optional[UserDetailResponse] = None
