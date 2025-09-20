"""
EchoSoul AI Platform AI Character Schemas
AI角色系统相关的Pydantic数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.common_schemas import BaseResponse, PaginationInfo

# 请求模型
class AICharacterCreateRequest(BaseModel):
    """创建AI角色请求"""
    name: str = Field(..., min_length=1, max_length=100, description="角色名称")
    nickname: str = Field(..., min_length=1, max_length=100, description="角色昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="角色头像URL")
    description: Optional[str] = Field(None, description="角色描述")
    personality: Optional[str] = Field(None, description="人设描述")
    background_story: Optional[str] = Field(None, description="背景故事")
    speaking_style: Optional[str] = Field(None, description="说话风格")
    is_public: bool = Field(False, description="是否公开")

class AICharacterUpdateRequest(BaseModel):
    """更新AI角色请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="角色名称")
    nickname: Optional[str] = Field(None, min_length=1, max_length=100, description="角色昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="角色头像URL")
    description: Optional[str] = Field(None, description="角色描述")
    personality: Optional[str] = Field(None, description="人设描述")
    background_story: Optional[str] = Field(None, description="背景故事")
    speaking_style: Optional[str] = Field(None, description="说话风格")
    is_public: Optional[bool] = Field(None, description="是否公开")

class CreateAIConversationRequest(BaseModel):
    """创建用户-AI会话请求"""
    character_id: str = Field(..., min_length=1, max_length=32, description="AI角色ID")

# 响应模型
class AICharacterInfo(BaseModel):
    """AI角色信息"""
    id: int
    character_id: str
    name: str
    nickname: str
    avatar: Optional[str]
    description: Optional[str]
    personality: Optional[str]
    background_story: Optional[str]
    speaking_style: Optional[str]
    creator_id: int
    is_public: bool
    status: int
    usage_count: int
    like_count: int
    create_time: str
    update_time: str

class AICharacterListResponse(BaseModel):
    """AI角色列表响应"""
    characters: List[AICharacterInfo]
    pagination: PaginationInfo

class AICharacterDetailResponse(BaseModel):
    """AI角色详情响应"""
    character: AICharacterInfo

class CreateAICharacterResponse(BaseModel):
    """创建AI角色响应"""
    character_id: str
    message: str

class UpdateAICharacterResponse(BaseModel):
    """更新AI角色响应"""
    message: str

class DeleteAICharacterResponse(BaseModel):
    """删除AI角色响应"""
    message: str

class FavoriteAICharacterResponse(BaseModel):
    """收藏AI角色响应"""
    message: str

class CreateAIConversationResponse(BaseModel):
    """创建用户-AI会话响应"""
    conversation_id: str
    character_info: AICharacterInfo
    message: str

# 基础响应模型
class AICharacterListBaseResponse(BaseResponse):
    """AI角色列表基础响应"""
    data: AICharacterListResponse

class AICharacterDetailBaseResponse(BaseResponse):
    """AI角色详情基础响应"""
    data: AICharacterDetailResponse

class CreateAICharacterBaseResponse(BaseResponse):
    """创建AI角色基础响应"""
    data: CreateAICharacterResponse

class UpdateAICharacterBaseResponse(BaseResponse):
    """更新AI角色基础响应"""
    data: UpdateAICharacterResponse

class DeleteAICharacterBaseResponse(BaseResponse):
    """删除AI角色基础响应"""
    data: DeleteAICharacterResponse

class FavoriteAICharacterBaseResponse(BaseResponse):
    """收藏AI角色基础响应"""
    data: FavoriteAICharacterResponse

class CreateAIConversationBaseResponse(BaseResponse):
    """创建用户-AI会话基础响应"""
    data: CreateAIConversationResponse
