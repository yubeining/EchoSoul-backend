"""
User API Routes
User management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import get_database_session
from app.schemas.pydantic_schemas import UserCreate, UserUpdate, UserResponse, MessageResponse
from app.services.crud_service import (
    get_users, get_user, create_user, update_user, delete_user,
    get_user_by_username, get_user_by_email
)

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_database_session)):
    """Get list of users"""
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserResponse)
async def create_user_endpoint(user: UserCreate, db: Session = Depends(get_database_session)):
    """Create a new user"""
    # Check if username or email already exists
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return create_user(db, user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: int, db: Session = Depends(get_database_session)):
    """Get user by ID"""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: int, user_update: UserUpdate, db: Session = Depends(get_database_session)):
    """Update user"""
    user = update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user_endpoint(user_id: int, db: Session = Depends(get_database_session)):
    """Delete user"""
    if delete_user(db, user_id):
        return MessageResponse(message="User deleted successfully")
    raise HTTPException(status_code=404, detail="User not found")
