"""
EchoSoul AI Platform User Search Service
用户搜索业务逻辑服务
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, func
from typing import Tuple, List, Optional
import math

from app.models.user_models import AuthUser as User
from app.schemas.user_search_schemas import (
    UserSearchRequest, UserSearchResponse, UserSearchResult, PaginationInfo
)

class UserSearchService:
    """用户搜索服务类"""
    
    @staticmethod
    def search_users(db: Session, request: UserSearchRequest) -> Tuple[bool, str, Optional[UserSearchResponse]]:
        """搜索用户"""
        try:
            keyword = request.keyword.strip()
            page = request.page
            limit = request.limit
            
            # 计算偏移量
            offset = (page - 1) * limit
            
            # 构建搜索条件
            search_conditions = or_(
                User.username.like(f'%{keyword}%'),
                User.nickname.like(f'%{keyword}%'),
                User.email.like(f'%{keyword}%'),
                User.intro.like(f'%{keyword}%')
            )
            
            # 只搜索正常状态的用户
            status_condition = User.status == 1
            
            # 组合条件
            where_condition = and_(search_conditions, status_condition)
            
            # 构建排序条件
            # 用户名前缀匹配 > 昵称前缀匹配 > 其他匹配，相同优先级按最后活跃时间倒序
            from sqlalchemy import case
            order_conditions = [
                case(
                    (User.username.like(f'{keyword}%'), 1),
                    (User.nickname.like(f'{keyword}%'), 2),
                    else_=3
                ).label('priority'),
                desc(User.last_login_time),
                desc(User.create_time)
            ]
            
            # 查询总数
            total_count = db.query(User).filter(where_condition).count()
            
            # 查询用户列表
            users = db.query(User).filter(where_condition).order_by(*order_conditions).offset(offset).limit(limit).all()
            
            # 转换为搜索结果格式
            user_results = []
            for user in users:
                user_result = UserSearchResult(
                    id=user.id,
                    uid=user.uid,
                    username=user.username,
                    nickname=user.nickname,
                    email=user.email,
                    mobile=user.mobile,
                    avatar=user.avatar,
                    intro=user.intro,
                    lastActive=user.last_login_time.isoformat() + 'Z' if user.last_login_time else None,
                    createdAt=user.create_time.isoformat() + 'Z'
                )
                user_results.append(user_result)
            
            # 计算分页信息
            total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
            
            pagination = PaginationInfo(
                currentPage=page,
                totalPages=total_pages,
                totalCount=total_count,
                hasNext=page < total_pages,
                hasPrev=page > 1
            )
            
            # 构建响应
            response = UserSearchResponse(
                users=user_results,
                pagination=pagination
            )
            
            return True, "搜索成功", response
            
        except Exception as e:
            return False, f"搜索失败: {str(e)}", None
    
    @staticmethod
    def get_user_by_uid(db: Session, uid: str) -> Optional[User]:
        """根据UID获取用户"""
        try:
            return db.query(User).filter(User.uid == uid, User.status == 1).first()
        except Exception:
            return None
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            return db.query(User).filter(User.username == username, User.status == 1).first()
        except Exception:
            return None
