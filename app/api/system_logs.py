"""
System Logs API Routes
System log management endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db import get_database_session
from app.schemas.pydantic_schemas import SystemLogCreate, SystemLogResponse
from app.services.crud_service import get_system_logs, create_system_log

router = APIRouter()

@router.get("/", response_model=List[SystemLogResponse])
async def list_system_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_database_session)):
    """Get system logs"""
    logs = get_system_logs(db, skip=skip, limit=limit)
    return logs

@router.post("/", response_model=SystemLogResponse)
async def create_system_log_endpoint(log: SystemLogCreate, db: Session = Depends(get_database_session)):
    """Create a system log entry"""
    return create_system_log(db, log)
