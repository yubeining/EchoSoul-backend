"""
EchoSoul AI Platform Schemas Package
统一导入所有Pydantic数据验证模型
"""

# 认证相关schemas
from .auth_schemas import (
    UserRegisterRequest, UserLoginRequest, OAuthLoginRequest,
    UserProfileUpdateRequest, PasswordChangeRequest,
    BaseResponse, RegisterResponse, LoginResponse, UserInfo, TokenRefreshResponse
)

# 聊天相关schemas
from .chat_schemas import (
    GetOrCreateConversationRequest, SendMessageRequest,
    GetOrCreateConversationResponse, SendMessageResponse,
    ConversationListBaseResponse, ConversationBaseResponse, MessageListBaseResponse,
    ConversationListResponse, MessageListResponse, MessageBaseResponse,
    MessageType, ConversationResponse, MessageResponse
)

# AI角色相关schemas
from .ai_character_schemas import (
    AICharacterCreateRequest, AICharacterUpdateRequest, CreateAIConversationRequest,
    AICharacterListBaseResponse, AICharacterDetailBaseResponse,
    CreateAICharacterBaseResponse, UpdateAICharacterBaseResponse,
    DeleteAICharacterBaseResponse, FavoriteAICharacterBaseResponse,
    CreateAIConversationBaseResponse
)

# 用户搜索相关schemas
from .user_search_schemas import (
    UserSearchRequest, UserSearchResponse, UserSearchBaseResponse
)

# 存储相关schemas
from .storage_schemas import (
    FileUploadResponse, FileInfoResponse, FileListResponse,
    StorageStatusResponse
)

# 通用schemas
from .common_schemas import (
    DatabaseStatusResponse, PaginationParams, BaseResponse
)

__all__ = [
    # 认证
    "UserRegisterRequest", "UserLoginRequest", "OAuthLoginRequest",
    "UserProfileUpdateRequest", "PasswordChangeRequest",
    "BaseResponse", "RegisterResponse", "LoginResponse", "UserInfo", "TokenRefreshResponse",
    
    # 聊天
    "GetOrCreateConversationRequest", "SendMessageRequest",
    "GetOrCreateConversationResponse", "SendMessageResponse",
    "ConversationListBaseResponse", "ConversationBaseResponse", "MessageListBaseResponse",
    "ConversationListResponse", "MessageListResponse", "MessageBaseResponse",
    "MessageType", "ConversationResponse", "MessageResponse",
    
    # AI角色
    "AICharacterCreateRequest", "AICharacterUpdateRequest", "CreateAIConversationRequest",
    "AICharacterListBaseResponse", "AICharacterDetailBaseResponse",
    "CreateAICharacterBaseResponse", "UpdateAICharacterBaseResponse",
    "DeleteAICharacterBaseResponse", "FavoriteAICharacterBaseResponse",
    "CreateAIConversationBaseResponse",
    
    # 用户搜索
    "UserSearchRequest", "UserSearchResponse", "UserSearchBaseResponse",
    
    # 存储
    "FileUploadResponse", "FileInfoResponse", "FileListResponse",
    "StorageStatusResponse",
    
    # 通用
    "DatabaseStatusResponse", "PaginationParams"
]
