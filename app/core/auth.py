"""
EchoSoul AI Platform Authentication Core
JWT认证和密码加密核心功能
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import random
import string

from config.settings import settings
from app.db import get_database_session
from app.models.user_models import AuthUser as User

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# HTTP Bearer认证
security = HTTPBearer()

def generate_uid(db: Session) -> str:
    """生成8位唯一用户标识符（纯数字递增）"""
    # 查询当前最大的数字UID
    max_uid_user = db.query(User).filter(User.uid.regexp_match(r'^\d{8}$')).order_by(User.uid.desc()).first()
    
    if max_uid_user and max_uid_user.uid.isdigit():
        # 如果存在数字UID，则递增
        next_uid = int(max_uid_user.uid) + 1
    else:
        # 如果没有数字UID，从10000000开始
        next_uid = 10000000
    
    # 确保UID是8位数字
    return str(next_uid).zfill(8)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_user_by_username_or_email_or_mobile(db: Session, username: str) -> Optional[User]:
    """根据用户名、邮箱或手机号获取用户"""
    # 先尝试用户名
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    
    # 尝试邮箱
    user = db.query(User).filter(User.email == username).first()
    if user:
        return user
    
    # 尝试手机号
    user = db.query(User).filter(User.mobile == username).first()
    if user:
        return user
    
    return None

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """认证用户"""
    user = get_user_by_username_or_email_or_mobile(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    if user.status != 1:
        return None
    return user

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database_session)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    return user

def generate_username_from_mobile_or_email(mobile_or_email: str) -> str:
    """根据手机号或邮箱生成用户名"""
    import re
    
    # 如果是手机号
    if re.match(r'^1[3-9]\d{9}$', mobile_or_email):
        return mobile_or_email
    
    # 如果是邮箱
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', mobile_or_email):
        local_part = mobile_or_email.split('@')[0]
        return local_part
    
    # 其他情况直接使用输入值
    return mobile_or_email

def update_user_login_info(db: Session, user: User, login_ip: str = None):
    """更新用户登录信息"""
    user.last_login_time = datetime.utcnow()
    if login_ip:
        user.last_login_ip = login_ip
    db.commit()
    db.refresh(user)
