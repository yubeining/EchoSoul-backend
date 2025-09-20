"""
EchoSoul AI Platform Authentication Service
用户认证业务逻辑服务
"""

from sqlalchemy.orm import Session
from typing import Optional, Tuple
from datetime import datetime
import re

from app.models.user_models import AuthUser as User
from app.schemas.auth_schemas import (
    UserRegisterRequest, UserLoginRequest, OAuthLoginRequest,
    RegisterResponse, LoginResponse, UserInfo
)
from app.core.auth import (
    get_password_hash, authenticate_user, create_access_token,
    generate_username_from_mobile_or_email, update_user_login_info, generate_uid
)

class AuthService:
    """认证服务类"""
    
    @staticmethod
    def register_user(db: Session, request: UserRegisterRequest) -> Tuple[bool, str, Optional[RegisterResponse]]:
        """用户注册"""
        try:
            # 检查用户名是否已存在
            existing_user = db.query(User).filter(User.username == request.mobileOrEmail).first()
            if existing_user:
                return False, "用户名已存在", None
            
            # 检查邮箱是否已存在
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', request.mobileOrEmail):
                existing_email = db.query(User).filter(User.email == request.mobileOrEmail).first()
                if existing_email:
                    return False, "邮箱已存在", None
            
            # 检查手机号是否已存在
            if re.match(r'^1[3-9]\d{9}$', request.mobileOrEmail):
                existing_mobile = db.query(User).filter(User.mobile == request.mobileOrEmail).first()
                if existing_mobile:
                    return False, "手机号已存在", None
            
            # 生成用户名
            username = generate_username_from_mobile_or_email(request.mobileOrEmail)
            
            # 确保用户名唯一
            counter = 1
            original_username = username
            while db.query(User).filter(User.username == username).first():
                username = f"{original_username}_{counter}"
                counter += 1
            
            # 创建新用户
            user = User(
                uid=generate_uid(db),
                username=username,
                email=request.mobileOrEmail if '@' in request.mobileOrEmail else None,
                mobile=request.mobileOrEmail if re.match(r'^1[3-9]\d{9}$', request.mobileOrEmail) else None,
                password=get_password_hash(request.password),
                nickname=request.nickname or username,
                status=1
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            response = RegisterResponse(
                userId=user.id,
                uid=user.uid,
                username=user.username,
                nickname=user.nickname
            )
            
            return True, "注册成功", response
            
        except Exception as e:
            db.rollback()
            return False, f"注册失败: {str(e)}", None
    
    @staticmethod
    def login_user(db: Session, request: UserLoginRequest, login_ip: str = None) -> Tuple[bool, str, Optional[LoginResponse]]:
        """用户登录"""
        try:
            # 认证用户
            user = authenticate_user(db, request.username, request.password)
            if not user:
                return False, "用户名或密码错误", None
            
            # 更新登录信息
            update_user_login_info(db, user, login_ip)
            
            # 创建访问令牌
            access_token = create_access_token(data={"sub": str(user.id)})
            
            # 构建用户信息
            user_info = UserInfo(
                id=user.id,
                uid=user.uid,
                username=user.username,
                email=user.email,
                mobile=user.mobile,
                nickname=user.nickname,
                avatar=user.avatar,
                status=user.status,
                lastLoginTime=user.last_login_time.isoformat() + "Z" if user.last_login_time else None,
                createTime=user.create_time.isoformat() + "Z" if user.create_time else None
            )
            
            response = LoginResponse(
                token=access_token,
                userInfo=user_info,
                isNewUser=False
            )
            
            return True, "登录成功", response
            
        except Exception as e:
            return False, f"登录失败: {str(e)}", None
    
    @staticmethod
    def oauth_login(db: Session, request: OAuthLoginRequest) -> Tuple[bool, str, Optional[LoginResponse]]:
        """第三方登录"""
        try:
            # 根据第三方类型生成用户名
            username = f"{request.oauthType}_{request.oauthCode[:8]}"
            
            # 检查用户是否已存在
            user = db.query(User).filter(User.username == username).first()
            is_new_user = False
            
            if not user:
                # 创建新用户
                user = User(
                    uid=generate_uid(db),
                    username=username,
                    nickname=f"{request.oauthType.title()}用户",
                    status=1,
                    password=get_password_hash("oauth_default_password")
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                is_new_user = True
            
            # 创建访问令牌
            access_token = create_access_token(data={"sub": str(user.id)})
            
            # 构建用户信息
            user_info = UserInfo(
                id=user.id,
                uid=user.uid,
                username=user.username,
                email=user.email,
                mobile=user.mobile,
                nickname=user.nickname,
                avatar=user.avatar,
                status=user.status,
                lastLoginTime=user.last_login_time.isoformat() + "Z" if user.last_login_time else None,
                createTime=user.create_time.isoformat() + "Z" if user.create_time else None
            )
            
            response = LoginResponse(
                token=access_token,
                userInfo=user_info,
                isNewUser=is_new_user
            )
            
            return True, "登录成功", response
            
        except Exception as e:
            db.rollback()
            return False, f"第三方登录失败: {str(e)}", None
    
    @staticmethod
    def get_user_info(user: User) -> UserInfo:
        """获取用户信息"""
        return UserInfo(
            id=user.id,
            uid=user.uid,
            username=user.username,
            email=user.email,
            mobile=user.mobile,
            nickname=user.nickname,
            avatar=user.avatar,
            status=user.status,
            lastLoginTime=user.last_login_time.isoformat() if user.last_login_time else None,
            createTime=user.create_time.isoformat() if user.create_time else None
        )
    
    @staticmethod
    def update_user_profile(db: Session, user: User, nickname: str = None, avatar: str = None) -> Tuple[bool, str]:
        """更新用户资料"""
        try:
            if nickname is not None:
                user.nickname = nickname
            if avatar is not None:
                user.avatar = avatar
            
            db.commit()
            db.refresh(user)
            return True, "修改成功"
            
        except Exception as e:
            db.rollback()
            return False, f"修改失败: {str(e)}"
    
    @staticmethod
    def change_password(db: Session, user: User, old_password: str, new_password: str) -> Tuple[bool, str]:
        """修改密码"""
        try:
            from app.core.auth import verify_password
            
            # 验证原密码
            if not verify_password(old_password, user.password):
                return False, "原密码错误"
            
            # 检查新密码是否与原密码相同
            if verify_password(new_password, user.password):
                return False, "新密码不能与原密码相同"
            
            # 更新密码
            from app.core.auth import get_password_hash
            user.password = get_password_hash(new_password)
            
            db.commit()
            db.refresh(user)
            return True, "密码修改成功"
            
        except Exception as e:
            db.rollback()
            return False, f"密码修改失败: {str(e)}"
