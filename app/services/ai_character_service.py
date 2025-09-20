"""
EchoSoul AI Platform AI Character Service
AI角色系统业务逻辑服务
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import Optional, Tuple, List
import uuid
import string
import random
from datetime import datetime

from app.models.ai_character_models import AICharacter, UserAIRelation
from app.models.user_models import AuthUser
from app.schemas.ai_character_schemas import (
    AICharacterCreateRequest, AICharacterUpdateRequest, CreateAIConversationRequest,
    AICharacterInfo, AICharacterListResponse, AICharacterDetailResponse,
    CreateAICharacterResponse, UpdateAICharacterResponse, DeleteAICharacterResponse,
    FavoriteAICharacterResponse, CreateAIConversationResponse
)
from app.schemas.common_schemas import PaginationInfo

class AICharacterService:
    """AI角色服务类"""
    
    @staticmethod
    def generate_character_id() -> str:
        """生成AI角色唯一标识符"""
        return f"char_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
    
    @staticmethod
    def create_character(db: Session, request: AICharacterCreateRequest, creator_id: int) -> Tuple[bool, str, Optional[CreateAICharacterResponse]]:
        """创建AI角色"""
        try:
            # 检查角色名称是否已存在
            existing_character = db.query(AICharacter).filter(
                and_(
                    AICharacter.name == request.name,
                    AICharacter.creator_id == creator_id
                )
            ).first()
            
            if existing_character:
                return False, "角色名称已存在", None
            
            # 生成角色ID
            character_id = AICharacterService.generate_character_id()
            
            # 创建AI角色
            character = AICharacter(
                character_id=character_id,
                name=request.name,
                nickname=request.nickname,
                avatar=request.avatar,
                description=request.description,
                personality=request.personality,
                background_story=request.background_story,
                speaking_style=request.speaking_style,
                creator_id=creator_id,
                is_public=request.is_public,
                status=1
            )
            
            db.add(character)
            db.commit()
            db.refresh(character)
            
            # 创建用户-AI关系记录
            relation = UserAIRelation(
                user_id=creator_id,
                character_id=character_id,
                relation_type='created'
            )
            db.add(relation)
            db.commit()
            
            response = CreateAICharacterResponse(
                character_id=character_id,
                message="AI角色创建成功"
            )
            
            return True, "创建成功", response
            
        except Exception as e:
            db.rollback()
            return False, f"创建失败: {str(e)}", None
    
    @staticmethod
    def get_character_list(db: Session, user_id: int, list_type: str = "public", 
                          page: int = 1, limit: int = 20) -> Tuple[bool, str, Optional[AICharacterListResponse]]:
        """获取AI角色列表"""
        try:
            offset = (page - 1) * limit
            
            # 构建查询条件
            query = db.query(AICharacter).filter(AICharacter.status == 1)
            
            if list_type == "public":
                # 公开角色
                query = query.filter(AICharacter.is_public == True)
            elif list_type == "my":
                # 我创建的角色
                query = query.filter(AICharacter.creator_id == user_id)
            elif list_type == "favorited":
                # 我收藏的角色
                favorited_character_ids = db.query(UserAIRelation.character_id).filter(
                    and_(
                        UserAIRelation.user_id == user_id,
                        UserAIRelation.relation_type == 'favorited'
                    )
                ).subquery()
                query = query.filter(AICharacter.character_id.in_(favorited_character_ids))
            
            # 获取总数
            total_count = query.count()
            
            # 获取分页数据
            characters = query.order_by(desc(AICharacter.create_time)).offset(offset).limit(limit).all()
            
            # 转换为响应格式
            character_list = []
            for char in characters:
                character_info = AICharacterInfo(
                    id=char.id,
                    character_id=char.character_id,
                    name=char.name,
                    nickname=char.nickname,
                    avatar=char.avatar,
                    description=char.description,
                    personality=char.personality,
                    background_story=char.background_story,
                    speaking_style=char.speaking_style,
                    creator_id=char.creator_id,
                    is_public=char.is_public,
                    status=char.status,
                    usage_count=char.usage_count,
                    like_count=char.like_count,
                    create_time=char.create_time.isoformat() if char.create_time else None,
                    update_time=char.update_time.isoformat() if char.update_time else None
                )
                character_list.append(character_info)
            
            # 分页信息
            total_pages = (total_count + limit - 1) // limit
            pagination = PaginationInfo(
                current_page=page,
                total_pages=total_pages,
                total_count=total_count,
                has_next=page < total_pages,
                has_prev=page > 1
            )
            
            response = AICharacterListResponse(
                characters=character_list,
                pagination=pagination
            )
            
            return True, "获取成功", response
            
        except Exception as e:
            return False, f"获取失败: {str(e)}", None
    
    @staticmethod
    def get_character_detail(db: Session, character_id: str) -> Tuple[bool, str, Optional[AICharacterDetailResponse]]:
        """获取AI角色详情"""
        try:
            character = db.query(AICharacter).filter(
                and_(
                    AICharacter.character_id == character_id,
                    AICharacter.status == 1
                )
            ).first()
            
            if not character:
                return False, "AI角色不存在", None
            
            character_info = AICharacterInfo(
                id=character.id,
                character_id=character.character_id,
                name=character.name,
                nickname=character.nickname,
                avatar=character.avatar,
                description=character.description,
                personality=character.personality,
                background_story=character.background_story,
                speaking_style=character.speaking_style,
                creator_id=character.creator_id,
                is_public=character.is_public,
                status=character.status,
                usage_count=character.usage_count,
                like_count=character.like_count,
                create_time=character.create_time.isoformat() if character.create_time else None,
                update_time=character.update_time.isoformat() if character.update_time else None
            )
            
            response = AICharacterDetailResponse(character=character_info)
            return True, "获取成功", response
            
        except Exception as e:
            return False, f"获取失败: {str(e)}", None
    
    @staticmethod
    def update_character(db: Session, character_id: str, request: AICharacterUpdateRequest, user_id: int) -> Tuple[bool, str, Optional[UpdateAICharacterResponse]]:
        """更新AI角色"""
        try:
            character = db.query(AICharacter).filter(
                and_(
                    AICharacter.character_id == character_id,
                    AICharacter.creator_id == user_id,
                    AICharacter.status == 1
                )
            ).first()
            
            if not character:
                return False, "AI角色不存在或无权限修改", None
            
            # 更新字段
            if request.name is not None:
                # 检查新名称是否与其他角色冲突
                existing = db.query(AICharacter).filter(
                    and_(
                        AICharacter.name == request.name,
                        AICharacter.creator_id == user_id,
                        AICharacter.character_id != character_id
                    )
                ).first()
                if existing:
                    return False, "角色名称已存在", None
                character.name = request.name
            
            if request.nickname is not None:
                character.nickname = request.nickname
            if request.avatar is not None:
                character.avatar = request.avatar
            if request.description is not None:
                character.description = request.description
            if request.personality is not None:
                character.personality = request.personality
            if request.background_story is not None:
                character.background_story = request.background_story
            if request.speaking_style is not None:
                character.speaking_style = request.speaking_style
            if request.is_public is not None:
                character.is_public = request.is_public
            
            db.commit()
            db.refresh(character)
            
            response = UpdateAICharacterResponse(message="更新成功")
            return True, "更新成功", response
            
        except Exception as e:
            db.rollback()
            return False, f"更新失败: {str(e)}", None
    
    @staticmethod
    def delete_character(db: Session, character_id: str, user_id: int) -> Tuple[bool, str, Optional[DeleteAICharacterResponse]]:
        """删除AI角色"""
        try:
            character = db.query(AICharacter).filter(
                and_(
                    AICharacter.character_id == character_id,
                    AICharacter.creator_id == user_id,
                    AICharacter.status == 1
                )
            ).first()
            
            if not character:
                return False, "AI角色不存在或无权限删除", None
            
            # 软删除：将状态设为0
            character.status = 0
            db.commit()
            
            response = DeleteAICharacterResponse(message="删除成功")
            return True, "删除成功", response
            
        except Exception as e:
            db.rollback()
            return False, f"删除失败: {str(e)}", None
    
    @staticmethod
    def favorite_character(db: Session, character_id: str, user_id: int, action: str) -> Tuple[bool, str, Optional[FavoriteAICharacterResponse]]:
        """收藏/取消收藏AI角色"""
        try:
            # 检查角色是否存在
            character = db.query(AICharacter).filter(
                and_(
                    AICharacter.character_id == character_id,
                    AICharacter.status == 1
                )
            ).first()
            
            if not character:
                return False, "AI角色不存在", None
            
            # 检查现有关系
            existing_relation = db.query(UserAIRelation).filter(
                and_(
                    UserAIRelation.user_id == user_id,
                    UserAIRelation.character_id == character_id,
                    UserAIRelation.relation_type == 'favorited'
                )
            ).first()
            
            if action == "favorite":
                if existing_relation:
                    return False, "已经收藏过该角色", None
                
                # 创建收藏关系
                relation = UserAIRelation(
                    user_id=user_id,
                    character_id=character_id,
                    relation_type='favorited'
                )
                db.add(relation)
                
                # 增加点赞数
                character.like_count += 1
                
                message = "收藏成功"
            else:  # unfavorite
                if not existing_relation:
                    return False, "未收藏该角色", None
                
                # 删除收藏关系
                db.delete(existing_relation)
                
                # 减少点赞数
                if character.like_count > 0:
                    character.like_count -= 1
                
                message = "取消收藏成功"
            
            db.commit()
            
            response = FavoriteAICharacterResponse(message=message)
            return True, message, response
            
        except Exception as e:
            db.rollback()
            return False, f"操作失败: {str(e)}", None
    
    @staticmethod
    def create_ai_conversation(db: Session, request: CreateAIConversationRequest, user_id: int) -> Tuple[bool, str, Optional[CreateAIConversationResponse]]:
        """创建用户-AI会话"""
        try:
            # 检查AI角色是否存在
            character = db.query(AICharacter).filter(
                and_(
                    AICharacter.character_id == request.character_id,
                    AICharacter.status == 1
                )
            ).first()
            
            if not character:
                return False, "AI角色不存在", None
            
            # 生成会话ID
            conversation_id = str(uuid.uuid4())
            
            # 创建会话（这里需要导入Conversation模型）
            from app.models.chat_models import Conversation
            
            conversation = Conversation(
                conversation_id=conversation_id,
                user1_id=user_id,
                user2_id=0,  # AI角色使用0作为ID
                conversation_name=character.nickname,
                conversation_type='user_ai',
                ai_character_id=request.character_id
            )
            
            db.add(conversation)
            
            # 增加使用次数
            character.usage_count += 1
            
            db.commit()
            db.refresh(conversation)
            
            # 构建角色信息
            character_info = AICharacterInfo(
                id=character.id,
                character_id=character.character_id,
                name=character.name,
                nickname=character.nickname,
                avatar=character.avatar,
                description=character.description,
                personality=character.personality,
                background_story=character.background_story,
                speaking_style=character.speaking_style,
                creator_id=character.creator_id,
                is_public=character.is_public,
                status=character.status,
                usage_count=character.usage_count,
                like_count=character.like_count,
                create_time=character.create_time.isoformat() if character.create_time else None,
                update_time=character.update_time.isoformat() if character.update_time else None
            )
            
            response = CreateAIConversationResponse(
                conversation_id=conversation_id,
                character_info=character_info,
                message="会话创建成功"
            )
            
            return True, "创建成功", response
            
        except Exception as e:
            db.rollback()
            return False, f"创建失败: {str(e)}", None
