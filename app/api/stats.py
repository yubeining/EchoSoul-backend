"""
Statistics API Routes
System statistics endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_database_session
from app.services.crud_service import get_user_count

router = APIRouter()

@router.get("/")
async def get_statistics(db: Session = Depends(get_database_session)):
    """Get system statistics"""
    return {
        "users": get_user_count(db)
    }

@router.get("/users")
async def get_user_statistics(db: Session = Depends(get_database_session)):
    """Get user statistics"""
    return {
        "total_users": get_user_count(db),
        "active_users": get_user_count(db)  # TODO: Add active user filtering
    }
