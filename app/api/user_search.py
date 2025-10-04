"""
EchoSoul AI Platform User Search API
用户搜索API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_database_session
from app.core.utils.auth import get_current_user
from app.models.user_models import AuthUser as User
from app.services.user_search_service import UserSearchService
from app.schemas.user_search_schemas import (
    UserSearchRequest, BaseResponse, UserDetailBaseResponse, UserDetailResponse, UserSearchResult
)

router = APIRouter()

@router.get("/search", response_model=BaseResponse)
async def search_users(
    keyword: str = Query(..., description="搜索关键词", min_length=2, max_length=50),
    page: int = Query(1, description="页码", ge=1),
    limit: int = Query(20, description="每页数量", ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    用户搜索接口
    
    - **keyword**: 搜索关键词，支持用户名、昵称、邮箱、简介的模糊搜索
    - **page**: 页码，从1开始
    - **limit**: 每页数量，最大100
    - **认证**: 需要Bearer Token认证
    
    搜索规则：
    - 搜索字段：username, nickname, email, intro
    - 匹配方式：模糊匹配 (LIKE '%keyword%')
    - 排序规则：用户名前缀匹配 > 昵称前缀匹配 > 其他匹配，相同优先级按最后活跃时间倒序
    """
    try:
        # 构建搜索请求
        search_request = UserSearchRequest(
            keyword=keyword,
            page=page,
            limit=limit
        )
        
        # 执行搜索
        success, message, response = UserSearchService.search_users(db, search_request)
        
        if success:
            return BaseResponse(
                code=200,
                msg="success",
                data=response
            )
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索服务异常: {str(e)}")

@router.get("/profile/{uid}", response_model=UserDetailBaseResponse)
async def get_user_profile(
    uid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    根据UID获取用户详细信息
    
    - **uid**: 用户唯一标识符
    - **认证**: 需要Bearer Token认证
    """
    try:
        user = UserSearchService.get_user_by_uid(db, uid)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 构建用户信息响应
        user_result = UserSearchResult(
            id=user.id,
            uid=user.uid,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            mobile=user.mobile,
            avatar=user.avatar,
            intro=user.intro,
            lastActive=user.last_login_time.isoformat() + 'Z' if user.last_login_time else None,
            createdAt=user.create_time.isoformat() + 'Z'
        )
        
        user_detail = UserDetailResponse(user=user_result)
        
        return UserDetailBaseResponse(
            code=200,
            msg="success",
            data=user_detail
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

@router.get("/{userId}", response_model=UserDetailBaseResponse)
async def get_user_by_id(
    userId: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    根据用户ID获取用户详细信息
    
    - **userId**: 用户ID
    - **认证**: 需要Bearer Token认证
    """
    try:
        user = db.query(User).filter(User.id == userId).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 构建用户信息响应
        user_result = UserSearchResult(
            id=user.id,
            uid=user.uid,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            mobile=user.mobile,
            avatar_url=user.avatar,
            intro=user.intro,
            last_active_at=user.last_login_time,
            create_time=user.create_time
        )
        
        return UserDetailBaseResponse(
            code=1,
            msg="获取用户详情成功",
            data=user_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户详情失败: {str(e)}")

@router.get("/profile/username/{username}", response_model=UserDetailBaseResponse)
async def get_user_profile_by_username(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    根据用户名获取用户详细信息
    
    - **username**: 用户名
    - **认证**: 需要Bearer Token认证
    """
    try:
        user = UserSearchService.get_user_by_username(db, username)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 构建用户信息响应
        user_result = UserSearchResult(
            id=user.id,
            uid=user.uid,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            mobile=user.mobile,
            avatar=user.avatar,
            intro=user.intro,
            lastActive=user.last_login_time.isoformat() + 'Z' if user.last_login_time else None,
            createdAt=user.create_time.isoformat() + 'Z'
        )
        
        user_detail = UserDetailResponse(user=user_result)
        
        return UserDetailBaseResponse(
            code=200,
            msg="success",
            data=user_detail
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")
