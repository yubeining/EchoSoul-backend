"""
EchoSoul AI Platform Authentication Schemas
用户认证相关的Pydantic模式
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import re

# 基础响应模式
class BaseResponse(BaseModel):
    """基础响应模式"""
    code: int = 1
    msg: str = "success"
    data: Optional[dict] = None

# 用户注册请求
class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    mobileOrEmail: str
    password: str
    confirmPassword: str
    nickname: Optional[str] = None
    
    @validator('mobileOrEmail')
    def validate_mobile_or_email(cls, v):
        """验证手机号或邮箱格式"""
        if not v:
            raise ValueError('手机号或邮箱不能为空')
        
        # 检查是否为手机号
        if re.match(r'^1[3-9]\d{9}$', v):
            return v
        
        # 检查是否为邮箱
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            return v
        
        raise ValueError('请输入有效的手机号或邮箱')
    
    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if len(v) < 6 or len(v) > 20:
            raise ValueError('密码长度必须在6-20位之间')
        return v
    
    @validator('confirmPassword')
    def validate_confirm_password(cls, v, values):
        """验证确认密码"""
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v

# 用户登录请求
class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名"""
        if not v or len(v.strip()) == 0:
            raise ValueError('用户名不能为空')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        """验证密码"""
        if not v or len(v.strip()) == 0:
            raise ValueError('密码不能为空')
        return v.strip()

# 第三方登录请求
class OAuthLoginRequest(BaseModel):
    """第三方登录请求"""
    oauthType: str
    oauthCode: str
    oauthState: Optional[str] = None
    
    @validator('oauthType')
    def validate_oauth_type(cls, v):
        """验证第三方类型"""
        allowed_types = ['wechat', 'qq', 'weibo']
        if v not in allowed_types:
            raise ValueError(f'不支持的第三方登录类型: {v}')
        return v
    
    @validator('oauthCode')
    def validate_oauth_code(cls, v):
        """验证授权码"""
        if not v or len(v.strip()) == 0:
            raise ValueError('授权码不能为空')
        return v.strip()

# 用户信息响应
class UserInfo(BaseModel):
    """用户信息"""
    id: int
    username: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    status: int
    lastLoginTime: Optional[str] = None
    createTime: Optional[str] = None

# 登录响应
class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    userInfo: UserInfo
    isNewUser: Optional[bool] = False

# 注册响应
class RegisterResponse(BaseModel):
    """注册响应"""
    userId: int
    username: str
    nickname: Optional[str] = None

# 用户资料更新请求
class UserProfileUpdateRequest(BaseModel):
    """用户资料更新请求"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    
    @validator('nickname')
    def validate_nickname(cls, v):
        """验证昵称"""
        if v is not None and len(v.strip()) == 0:
            raise ValueError('昵称不能为空字符串')
        return v.strip() if v else None
    
    @validator('avatar')
    def validate_avatar(cls, v):
        """验证头像URL"""
        if v is not None and len(v.strip()) == 0:
            raise ValueError('头像URL不能为空字符串')
        return v.strip() if v else None

# 密码修改请求
class PasswordChangeRequest(BaseModel):
    """密码修改请求"""
    oldPassword: str
    newPassword: str
    confirmPassword: str
    
    @validator('oldPassword')
    def validate_old_password(cls, v):
        """验证原密码"""
        if not v or len(v.strip()) == 0:
            raise ValueError('原密码不能为空')
        return v.strip()
    
    @validator('newPassword')
    def validate_new_password(cls, v):
        """验证新密码"""
        if len(v) < 6 or len(v) > 20:
            raise ValueError('新密码长度必须在6-20位之间')
        return v
    
    @validator('confirmPassword')
    def validate_confirm_password(cls, v, values):
        """验证确认密码"""
        if 'newPassword' in values and v != values['newPassword']:
            raise ValueError('两次输入的新密码不一致')
        return v

# Token刷新响应
class TokenRefreshResponse(BaseModel):
    """Token刷新响应"""
    token: str
