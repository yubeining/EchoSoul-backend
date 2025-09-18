"""
AI Request API Routes
AI request management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_database_session
from app.schemas.pydantic_schemas import AIRequestCreate, AIRequestUpdate, AIRequestResponse, MessageResponse
from app.services.crud_service import (
    get_ai_requests, get_ai_request, create_ai_request, update_ai_request, delete_ai_request
)

router = APIRouter()

@router.get("/", response_model=List[AIRequestResponse])
async def list_ai_requests(
    skip: int = 0, 
    limit: int = 100, 
    user_id: Optional[int] = None, 
    db: Session = Depends(get_database_session)
):
    """Get list of AI requests"""
    requests = get_ai_requests(db, skip=skip, limit=limit, user_id=user_id)
    return requests

@router.post("/", response_model=AIRequestResponse)
async def create_ai_request_endpoint(request: AIRequestCreate, db: Session = Depends(get_database_session)):
    """Create a new AI request"""
    return create_ai_request(db, request)

@router.get("/{request_id}", response_model=AIRequestResponse)
async def get_ai_request_endpoint(request_id: int, db: Session = Depends(get_database_session)):
    """Get AI request by ID"""
    request = get_ai_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="AI request not found")
    return request

@router.put("/{request_id}", response_model=AIRequestResponse)
async def update_ai_request_endpoint(
    request_id: int, 
    request_update: AIRequestUpdate, 
    db: Session = Depends(get_database_session)
):
    """Update AI request"""
    request = update_ai_request(db, request_id, request_update)
    if not request:
        raise HTTPException(status_code=404, detail="AI request not found")
    return request

@router.delete("/{request_id}", response_model=MessageResponse)
async def delete_ai_request_endpoint(request_id: int, db: Session = Depends(get_database_session)):
    """Delete AI request"""
    if delete_ai_request(db, request_id):
        return MessageResponse(message="AI request deleted successfully")
    raise HTTPException(status_code=404, detail="AI request not found")
