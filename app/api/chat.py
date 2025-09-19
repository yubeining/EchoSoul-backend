"""
EchoSoul AI Platform Chat API Routes
聊天系统API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_database_session
from app.core.auth import get_current_user
from app.models.user_models import AuthUser
from app.services.chat_service import ChatService
from app.schemas.chat_schemas import (
    GetOrCreateConversationRequest, SendMessageRequest,
    GetOrCreateConversationResponse, SendMessageResponse,
    ConversationListBaseResponse, MessageListBaseResponse,
    ConversationListResponse, MessageListResponse
)

router = APIRouter()

@router.post("/conversations/get-or-create", 
             response_model=GetOrCreateConversationResponse,
             summary="获取或创建会话")
async def get_or_create_conversation(
    request: GetOrCreateConversationRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """获取或创建与指定用户的会话"""
    success, message, data = ChatService.get_or_create_conversation(
        db, current_user.id, request
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return GetOrCreateConversationResponse(
        code=1,
        msg=message,
        data=data
    )

@router.get("/conversations", 
            response_model=ConversationListBaseResponse,
            summary="获取用户会话列表")
async def get_user_conversations(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """获取当前用户的会话列表"""
    success, message, conversations = ChatService.get_user_conversations(
        db, current_user.id, page, limit
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # 获取总数
    total = ChatService.get_conversation_count(db, current_user.id)
    
    response_data = ConversationListResponse(
        conversations=conversations,
        total=total,
        page=page,
        limit=limit
    )
    
    return ConversationListBaseResponse(
        code=1,
        msg=message,
        data=response_data
    )

@router.post("/messages", 
             response_model=SendMessageResponse,
             summary="发送消息")
async def send_message(
    request: SendMessageRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """发送消息到指定会话"""
    success, message, data = ChatService.send_message(
        db, current_user.id, request
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return SendMessageResponse(
        code=1,
        msg=message,
        data=data
    )

@router.get("/conversations/{conversation_id}/messages", 
            response_model=MessageListBaseResponse,
            summary="获取会话消息列表")
async def get_conversation_messages(
    conversation_id: str,
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(50, ge=1, le=100, description="每页数量"),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """获取指定会话的消息列表"""
    success, message, messages = ChatService.get_conversation_messages(
        db, current_user.id, conversation_id, page, limit
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # 获取总数
    total = ChatService.get_message_count(db, conversation_id)
    
    response_data = MessageListResponse(
        messages=messages,
        total=total,
        page=page,
        limit=limit
    )
    
    return MessageListBaseResponse(
        code=1,
        msg=message,
        data=response_data
    )
