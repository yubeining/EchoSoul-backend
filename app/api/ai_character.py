"""
EchoSoul AI Platform AI Character API Routes
AI角色系统API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_database_session
from app.core.auth import get_current_user
from app.models.user_models import AuthUser
from app.services.ai_character_service import AICharacterService
from app.schemas.ai_character_schemas import (
    AICharacterCreateRequest, AICharacterUpdateRequest, CreateAIConversationRequest,
    AICharacterListBaseResponse, AICharacterDetailBaseResponse,
    CreateAICharacterBaseResponse, UpdateAICharacterBaseResponse,
    DeleteAICharacterBaseResponse, FavoriteAICharacterBaseResponse,
    CreateAIConversationBaseResponse
)

router = APIRouter()

@router.post("/characters", 
             response_model=CreateAICharacterBaseResponse,
             summary="创建AI角色")
async def create_character(
    request: AICharacterCreateRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """创建AI角色"""
    success, message, data = AICharacterService.create_character(db, request, current_user.id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return CreateAICharacterBaseResponse(
        code=1,
        msg=message,
        data=data
    )

@router.get("/characters", 
            response_model=AICharacterListBaseResponse,
            summary="获取AI角色列表")
async def get_character_list(
    list_type: str = Query("public", description="列表类型: public-公开, my-我创建的, favorited-我收藏的"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """获取AI角色列表"""
    success, message, data = AICharacterService.get_character_list(
        db, current_user.id, list_type, page, limit
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return AICharacterListBaseResponse(
        code=1,
        msg=message,
        data=data
    )

@router.get("/characters/{character_id}", 
            response_model=AICharacterDetailBaseResponse,
            summary="获取AI角色详情")
async def get_character_detail(
    character_id: str,
    db: Session = Depends(get_database_session)
):
    """获取AI角色详情"""
    success, message, data = AICharacterService.get_character_detail(db, character_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return AICharacterDetailBaseResponse(
        code=1,
        msg=message,
        data=data
    )

@router.put("/characters/{character_id}", 
            response_model=UpdateAICharacterBaseResponse,
            summary="更新AI角色")
async def update_character(
    character_id: str,
    request: AICharacterUpdateRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """更新AI角色"""
    success, message, data = AICharacterService.update_character(
        db, character_id, request, current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return UpdateAICharacterBaseResponse(
        code=1,
        msg=message,
        data=data
    )

@router.delete("/characters/{character_id}", 
               response_model=DeleteAICharacterBaseResponse,
               summary="删除AI角色")
async def delete_character(
    character_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """删除AI角色"""
    success, message, data = AICharacterService.delete_character(
        db, character_id, current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return DeleteAICharacterBaseResponse(
        code=1,
        msg=message,
        data=data
    )

@router.post("/characters/{character_id}/favorite", 
             response_model=FavoriteAICharacterBaseResponse,
             summary="收藏AI角色")
async def favorite_character(
    character_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """收藏AI角色"""
    success, message, data = AICharacterService.favorite_character(
        db, character_id, current_user.id, "favorite"
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return FavoriteAICharacterBaseResponse(
        code=1,
        msg=message,
        data=data
    )

@router.delete("/characters/{character_id}/favorite", 
               response_model=FavoriteAICharacterBaseResponse,
               summary="取消收藏AI角色")
async def unfavorite_character(
    character_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """取消收藏AI角色"""
    success, message, data = AICharacterService.favorite_character(
        db, character_id, current_user.id, "unfavorite"
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return FavoriteAICharacterBaseResponse(
        code=1,
        msg=message,
        data=data
    )

@router.post("/conversations/ai",
             response_model=CreateAIConversationBaseResponse,
             summary="获取或创建用户-AI会话")
async def create_ai_conversation(
    request: CreateAIConversationRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """获取或创建用户-AI会话"""
    success, message, data = AICharacterService.create_ai_conversation(
        db, request, current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return CreateAIConversationBaseResponse(
        code=1,
        msg=message,
        data=data
    )
