"""
EchoSoul AI Platform User Models
用户认证相关的数据模型
"""

from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Text
from sqlalchemy.sql import func
from app.db import get_database_base

Base = get_database_base()

class AuthUser(Base):
    """用户认证表模型"""
    __tablename__ = "auth_users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    uid = Column(String(8), nullable=False, unique=True, comment="用户唯一标识符")
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=True, comment="邮箱")
    mobile = Column(String(20), unique=True, nullable=True, comment="手机号")
    password = Column(String(255), nullable=False, comment="密码(加密后)")
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    intro = Column(Text, nullable=True, comment="个人简介")
    status = Column(Integer, default=1, comment="状态: 1-正常, 0-禁用")
    last_login_time = Column(DateTime, nullable=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")
    create_time = Column(DateTime, default=func.current_timestamp(), comment="创建时间")
    update_time = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', nickname='{self.nickname}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "uid": self.uid,
            "username": self.username,
            "email": self.email,
            "mobile": self.mobile,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "intro": self.intro,
            "status": self.status,
            "lastLoginTime": self.last_login_time.isoformat() + "Z" if self.last_login_time else None,
            "createTime": self.create_time.isoformat() + "Z" if self.create_time else None
        }
