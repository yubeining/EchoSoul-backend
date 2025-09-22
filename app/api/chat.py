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
    ConversationListBaseResponse, ConversationBaseResponse, MessageListBaseResponse,
    ConversationListResponse, MessageListResponse, MessageBaseResponse
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
    user1_id: int = Query(None, description="用户1 ID"),
    user2_id: int = Query(None, description="用户2 ID"),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """获取当前用户的会话列表，支持按用户ID查询"""
    # 如果提供了user1_id和user2_id，则查找特定会话
    if user1_id and user2_id:
        # 这里可以添加查找特定会话的逻辑
        # 暂时使用默认的会话列表逻辑
        success, message, conversations = ChatService.get_user_conversations(
            db, current_user.id, page, limit
        )
    else:
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

@router.get("/conversations/ai", 
            response_model=ConversationListBaseResponse,
            summary="获取用户AI会话列表")
async def get_ai_conversations(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """获取用户的AI会话列表"""
    success, message, data = ChatService.get_ai_conversations(
        db, current_user.id, page, limit
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # 构建分页信息
    total = len(data) if data else 0
    response_data = ConversationListResponse(
        conversations=data,
        total=total,
        page=page,
        limit=limit
    )
    
    return ConversationListBaseResponse(
        code=1,
        msg=message,
        data=response_data
    )

@router.get("/conversations/{conversation_id}", 
            response_model=ConversationBaseResponse,
            summary="获取会话详情")
async def get_conversation_detail(
    conversation_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """获取特定会话的详细信息"""
    success, message, data = ChatService.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return ConversationBaseResponse(
        code=1,
        msg=message,
        data=data
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

# 注意：AI聊天功能已集成到 /messages 接口中
# 当会话类型为 'user_ai' 时，系统会自动处理AI回复
# 不再需要单独的 /messages/ai 接口

@router.get("/messages/{message_id}", 
            response_model=MessageBaseResponse,
            summary="获取单条消息详情")
async def get_message_detail(
    message_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """根据消息ID获取单条消息详情"""
    success, message, data = ChatService.get_message_by_id(
        db, current_user.id, message_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return MessageBaseResponse(
        code=1,
        msg=message,
        data=data
    )

@router.get("/conversations/{conversation_id}/messages/{message_id}", 
            response_model=MessageBaseResponse,
            summary="获取会话中的特定消息")
async def get_conversation_message_detail(
    conversation_id: str,
    message_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """根据会话ID和消息ID获取特定消息"""
    success, message, data = ChatService.get_message_by_id_in_conversation(
        db, current_user.id, conversation_id, message_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    return MessageBaseResponse(
        code=1,
        msg=message,
        data=data
    )
