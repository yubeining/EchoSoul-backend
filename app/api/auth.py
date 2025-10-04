"""
EchoSoul AI Platform Authentication API Routes
用户认证相关的API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_database_session
from app.models.user_models import AuthUser as User
from app.schemas.auth_schemas import (
    UserRegisterRequest, UserLoginRequest, OAuthLoginRequest,
    UserProfileUpdateRequest, PasswordChangeRequest,
    BaseResponse, RegisterResponse, LoginResponse, UserInfo, TokenRefreshResponse
)
from app.services.auth_service import AuthService
from app.core.utils.auth import get_current_user, create_access_token

router = APIRouter()

@router.post("/register", response_model=BaseResponse)
async def register(request: UserRegisterRequest, db: Session = Depends(get_database_session)):
    """用户注册"""
    success, message, data = AuthService.register_user(db, request)
    
    if success:
        return BaseResponse(
            code=1,
            msg=message,
            data=data.dict() if data else None
        )
    else:
        raise HTTPException(status_code=400, detail=message)

@router.post("/login", response_model=BaseResponse)
async def login(request: UserLoginRequest, http_request: Request, db: Session = Depends(get_database_session)):
    """用户登录"""
    # 获取客户端IP
    client_ip = http_request.client.host if http_request.client else None
    
    success, message, data = AuthService.login_user(db, request, client_ip)
    
    if success:
        return BaseResponse(
            code=1,
            msg=message,
            data=data.dict() if data else None
        )
    else:
        raise HTTPException(status_code=401, detail=message)

@router.post("/oauth/login", response_model=BaseResponse)
async def oauth_login(request: OAuthLoginRequest, db: Session = Depends(get_database_session)):
    """第三方登录"""
    success, message, data = AuthService.oauth_login(db, request)
    
    if success:
        return BaseResponse(
            code=1,
            msg=message,
            data=data.dict() if data else None
        )
    else:
        raise HTTPException(status_code=401, detail=message)

@router.get("/user/info", response_model=BaseResponse)
async def get_user_info(current_user: User = Depends(get_current_user)):
    """获取用户信息"""
    user_info = AuthService.get_user_info(current_user)
    
    return BaseResponse(
        code=1,
        msg="success",
        data=user_info.dict()
    )

@router.post("/logout", response_model=BaseResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    # 在实际应用中，这里可以将token加入黑名单
    # 或者使用Redis存储token状态
    
    return BaseResponse(
        code=1,
        msg="登出成功",
        data=None
    )

@router.post("/refresh", response_model=BaseResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """刷新Token"""
    # 创建新的访问令牌
    new_token = create_access_token(data={"sub": str(current_user.id)})
    
    return BaseResponse(
        code=1,
        msg="刷新成功",
        data={"token": new_token}
    )

@router.put("/user/profile", response_model=BaseResponse)
async def update_profile(
    request: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """修改用户资料"""
    success, message = AuthService.update_user_profile(
        db, current_user, request.nickname, request.avatar
    )
    
    if success:
        return BaseResponse(
            code=1,
            msg=message,
            data=None
        )
    else:
        raise HTTPException(status_code=400, detail=message)

@router.put("/user/password", response_model=BaseResponse)
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """修改密码"""
    success, message = AuthService.change_password(
        db, current_user, request.oldPassword, request.newPassword
    )
    
    if success:
        return BaseResponse(
            code=1,
            msg=message,
            data=None
        )
    else:
        raise HTTPException(status_code=400, detail=message)
