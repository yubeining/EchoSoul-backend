"""
Statistics API Routes
System statistics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.db import get_database_session
from app.services.crud_service import get_user_count

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_statistics(db: Session = Depends(get_database_session)):
    """Get system statistics"""
    try:
        total_users = get_user_count(db)
        return {
            "status": "success",
            "data": {
                "total_users": total_users,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统统计失败")

@router.get("/users")
async def get_user_statistics(db: Session = Depends(get_database_session)):
    """Get user statistics"""
    try:
        total_users = get_user_count(db)
        return {
            "status": "success",
            "data": {
                "total_users": total_users,
                "active_users": total_users,  # 暂时使用总用户数，后续可添加活跃用户逻辑
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    except Exception as e:
        logger.error(f"获取用户统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户统计失败")
