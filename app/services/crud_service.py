"""
EchoSoul AI Platform CRUD Operations
Database operations for all models
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models.sqlalchemy_models import AIRequest, SystemLog
from app.models.user_models import AuthUser
from app.schemas.pydantic_schemas import AIRequestCreate, AIRequestUpdate, SystemLogCreate

# User CRUD operations - 已移除，使用auth_users表中的AuthUser模型
# 用户管理功能通过auth_service.py中的AuthUser模型实现

# AI Request CRUD operations
def get_ai_request(db: Session, request_id: int) -> Optional[AIRequest]:
    return db.query(AIRequest).filter(AIRequest.id == request_id).first()

def get_ai_requests(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[AIRequest]:
    query = db.query(AIRequest)
    if user_id:
        query = query.filter(AIRequest.user_id == user_id)
    return query.order_by(desc(AIRequest.created_at)).offset(skip).limit(limit).all()

def create_ai_request(db: Session, request: AIRequestCreate) -> AIRequest:
    db_request = AIRequest(
        request_type=request.request_type,
        prompt=request.prompt,
        user_id=request.user_id
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def update_ai_request(db: Session, request_id: int, request_update: AIRequestUpdate) -> Optional[AIRequest]:
    db_request = db.query(AIRequest).filter(AIRequest.id == request_id).first()
    if db_request:
        update_data = request_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_request, field, value)
        db.commit()
        db.refresh(db_request)
    return db_request

def delete_ai_request(db: Session, request_id: int) -> bool:
    db_request = db.query(AIRequest).filter(AIRequest.id == request_id).first()
    if db_request:
        db.delete(db_request)
        db.commit()
        return True
    return False

# System Log CRUD operations
def get_system_logs(db: Session, skip: int = 0, limit: int = 100) -> List[SystemLog]:
    return db.query(SystemLog).order_by(desc(SystemLog.created_at)).offset(skip).limit(limit).all()

def create_system_log(db: Session, log: SystemLogCreate) -> SystemLog:
    db_log = SystemLog(
        level=log.level,
        message=log.message,
        module=log.module,
        user_id=log.user_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# Statistics functions
def get_user_count(db: Session) -> int:
    return db.query(AuthUser).count()

def get_ai_request_count(db: Session) -> int:
    return db.query(AIRequest).count()

def get_system_log_count(db: Session) -> int:
    return db.query(SystemLog).count()
