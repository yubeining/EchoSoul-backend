"""
六维状态管理器 (StateManager)
管理六维状态指标和交互历史，提供状态持久化和查询功能
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session

from app.core.utils.database_context import get_db_session
from app.core.utils.cache_manager import cache_get, cache_set, cache_delete
from app.core.management.logging_manager import log_operation_start, log_operation_success, log_operation_error, log_info
from app.models.chat_models import Conversation, Message
from app.models.ai_character_models import AICharacter
from app.models.user_models import AuthUser
from app.core.flow.models import ConversationState

logger = logging.getLogger(__name__)

@dataclass
class RoleCognitionState:
    """角色认知维度状态"""
    character_identity: str  # 角色身份
    personality_traits: List[str]  # 性格特征
    knowledge_base: Dict[str, Any]  # 知识库
    memory_context: List[str]  # 记忆上下文
    role_boundaries: Dict[str, Any]  # 角色边界
    consistency_score: float  # 一致性评分

@dataclass
class InteractionDynamicsState:
    """交互动态维度状态"""
    conversation_phase: str  # 对话阶段 (greeting, main, closing)
    user_engagement_level: float  # 用户参与度
    response_urgency: str  # 响应紧急度 (low, medium, high)
    topic_flow: List[str]  # 话题流向
    interaction_pattern: str  # 交互模式
    emotional_resonance: float  # 情感共鸣度

@dataclass
class ExpressionRulesState:
    """表达规则维度状态"""
    speaking_style: str  # 说话风格
    language_level: str  # 语言水平
    humor_preference: str  # 幽默偏好
    formality_level: str  # 正式程度
    cultural_context: str  # 文化背景
    expression_constraints: List[str]  # 表达约束

@dataclass
class CapabilityPermissionsState:
    """能力权限维度状态"""
    available_functions: List[str]  # 可用功能
    access_level: str  # 访问级别
    feature_permissions: Dict[str, bool]  # 功能权限
    resource_limits: Dict[str, Any]  # 资源限制
    security_constraints: List[str]  # 安全约束

@dataclass
class EnvironmentScenarioState:
    """环境场景维度状态"""
    current_scenario: str  # 当前场景
    time_context: str  # 时间上下文
    location_context: str  # 位置上下文
    social_context: str  # 社交上下文
    activity_context: str  # 活动上下文
    mood_atmosphere: str  # 氛围情绪

@dataclass
class DynamicAdjustmentState:
    """动态调整维度状态"""
    learning_rate: float  # 学习速率
    adaptation_level: str  # 适应级别
    feedback_integration: Dict[str, Any]  # 反馈整合
    performance_metrics: Dict[str, float]  # 性能指标
    adjustment_history: List[Dict[str, Any]]  # 调整历史

class StateManager:
    """六维状态管理器"""
    
    def __init__(self):
        # 状态缓存配置
        self.cache_ttl = {
            "user_state": 300,  # 5分钟
            "conversation_state": 180,  # 3分钟
            "character_state": 600,  # 10分钟
            "environment_state": 120  # 2分钟
        }
    
    async def update_state(self, user_id: int, conversation_id: Optional[str], 
                          parsed_input) -> 'ConversationState':
        """
        更新六维状态指标
        
        Args:
            user_id: 用户ID
            conversation_id: 对话ID
            parsed_input: 解析后的输入
            
        Returns:
            ConversationState: 更新后的对话状态
        """
        log_operation_start("更新状态", user_id=user_id, conversation_id=conversation_id)
        
        try:
            # 获取当前状态
            current_state = await self.get_conversation_state(user_id, conversation_id)
            
            # 更新各个维度的状态
            updated_state = await self._update_six_dimensions(
                current_state, parsed_input, user_id
            )
            
            # 持久化状态
            await self._persist_state(updated_state)
            
            log_operation_success("更新状态", user_id=user_id, conversation_id=conversation_id)
            
            return updated_state
            
        except Exception as e:
            log_operation_error("更新状态", str(e), user_id=user_id)
            # 返回默认状态
            return await self._create_default_state(user_id, conversation_id)
    
    async def get_conversation_state(self, user_id: int, conversation_id: Optional[str]) -> 'ConversationState':
        """获取对话状态"""
        cache_key = f"conversation_state:{user_id}:{conversation_id or 'default'}"
        
        # 尝试从缓存获取
        cached_state = cache_get(cache_key)
        if cached_state:
            return self._dict_to_conversation_state(cached_state)
        
        # 从数据库获取
        try:
            with get_db_session() as db:
                # 获取对话信息
                conversation = None
                if conversation_id:
                    conversation = db.query(Conversation).filter(
                        Conversation.conversation_id == conversation_id,
                        Conversation.user1_id == user_id
                    ).first()
                
                # 获取AI角色信息
                ai_character_id = conversation.ai_character_id if conversation else None
                
                # 构建状态
                state = await self._build_conversation_state(
                    user_id, conversation_id, ai_character_id, db
                )
                
                # 缓存状态
                cache_set(cache_key, asdict(state), ttl=self.cache_ttl["conversation_state"])
                
                return state
                
        except Exception as e:
            logger.error(f"获取对话状态失败: {e}")
            return await self._create_default_state(user_id, conversation_id)
    
    async def _update_six_dimensions(self, current_state: 'ConversationState', 
                                   parsed_input, user_id: int) -> 'ConversationState':
        """更新六维状态指标"""
        
        # 1. 更新角色认知维度
        role_cognition = await self._update_role_cognition(
            current_state.role_cognition, parsed_input
        )
        
        # 2. 更新交互动态维度
        interaction_dynamics = await self._update_interaction_dynamics(
            current_state.interaction_dynamics, parsed_input
        )
        
        # 3. 更新表达规则维度
        expression_rules = await self._update_expression_rules(
            current_state.expression_rules, parsed_input
        )
        
        # 4. 更新能力权限维度
        capability_permissions = await self._update_capability_permissions(
            current_state.capability_permissions, parsed_input
        )
        
        # 5. 更新环境场景维度
        environment_scenario = await self._update_environment_scenario(
            current_state.environment_scenario, parsed_input
        )
        
        # 6. 更新动态调整维度
        dynamic_adjustment = await self._update_dynamic_adjustment(
            current_state.dynamic_adjustment, parsed_input
        )
        
        # 更新情绪链和交互历史
        emotion_chain = await self._update_emotion_chain(
            current_state.emotion_chain, parsed_input
        )
        
        interaction_history = await self._update_interaction_history(
            current_state.interaction_history, parsed_input
        )
        
        # 构建更新后的状态
        updated_state = ConversationState(
            user_id=current_state.user_id,
            conversation_id=current_state.conversation_id,
            ai_character_id=current_state.ai_character_id,
            role_cognition=role_cognition,
            interaction_dynamics=interaction_dynamics,
            expression_rules=expression_rules,
            capability_permissions=capability_permissions,
            environment_scenario=environment_scenario,
            dynamic_adjustment=dynamic_adjustment,
            emotion_chain=emotion_chain,
            interaction_history=interaction_history,
            context_memory=current_state.context_memory,
            last_update_time=datetime.utcnow()
        )
        
        return updated_state
    
    async def _update_role_cognition(self, current: Dict[str, Any], parsed_input) -> Dict[str, Any]:
        """更新角色认知维度"""
        # 基于解析输入更新角色认知
        updated = current.copy()
        
        # 更新记忆上下文
        if hasattr(parsed_input, 'intent') and parsed_input.intent:
            memory_context = updated.get('memory_context', [])
            if parsed_input.intent not in memory_context:
                memory_context.append(parsed_input.intent)
                updated['memory_context'] = memory_context[-10:]  # 保持最近10个记忆
        
        # 更新一致性评分
        consistency_score = updated.get('consistency_score', 0.8)
        # 简单的评分更新逻辑
        if hasattr(parsed_input, 'confidence'):
            consistency_score = (consistency_score + parsed_input.confidence) / 2
        updated['consistency_score'] = min(max(consistency_score, 0.0), 1.0)
        
        return updated
    
    async def _update_interaction_dynamics(self, current: Dict[str, Any], parsed_input) -> Dict[str, Any]:
        """更新交互动态维度"""
        updated = current.copy()
        
        # 更新对话阶段
        if hasattr(parsed_input, 'intent'):
            if parsed_input.intent in ['greeting', 'hello']:
                updated['conversation_phase'] = 'greeting'
            elif parsed_input.intent in ['farewell', 'goodbye']:
                updated['conversation_phase'] = 'closing'
            else:
                updated['conversation_phase'] = 'main'
        
        # 更新用户参与度
        engagement_level = updated.get('user_engagement_level', 0.5)
        if hasattr(parsed_input, 'confidence'):
            engagement_level = (engagement_level + parsed_input.confidence) / 2
        updated['user_engagement_level'] = min(max(engagement_level, 0.0), 1.0)
        
        return updated
    
    async def _update_expression_rules(self, current: Dict[str, Any], parsed_input) -> Dict[str, Any]:
        """更新表达规则维度"""
        updated = current.copy()
        
        # 基于用户输入调整表达规则
        if hasattr(parsed_input, 'sentiment'):
            if parsed_input.sentiment == 'positive':
                updated['formality_level'] = 'casual'
            elif parsed_input.sentiment == 'negative':
                updated['formality_level'] = 'formal'
        
        return updated
    
    async def _update_capability_permissions(self, current: Dict[str, Any], parsed_input) -> Dict[str, Any]:
        """更新能力权限维度"""
        updated = current.copy()
        
        # 权限通常在系统级别设置，这里主要更新资源使用情况
        resource_limits = updated.get('resource_limits', {})
        resource_limits['last_usage'] = datetime.utcnow().isoformat()
        updated['resource_limits'] = resource_limits
        
        return updated
    
    async def _update_environment_scenario(self, current: Dict[str, Any], parsed_input) -> Dict[str, Any]:
        """更新环境场景维度"""
        updated = current.copy()
        
        # 更新时间上下文
        current_time = datetime.utcnow()
        hour = current_time.hour
        
        if 6 <= hour < 12:
            time_context = 'morning'
        elif 12 <= hour < 18:
            time_context = 'afternoon'
        elif 18 <= hour < 22:
            time_context = 'evening'
        else:
            time_context = 'night'
        
        updated['time_context'] = time_context
        
        return updated
    
    async def _update_dynamic_adjustment(self, current: Dict[str, Any], parsed_input) -> Dict[str, Any]:
        """更新动态调整维度"""
        updated = current.copy()
        
        # 更新性能指标
        performance_metrics = updated.get('performance_metrics', {})
        performance_metrics['interaction_count'] = performance_metrics.get('interaction_count', 0) + 1
        performance_metrics['last_interaction'] = datetime.utcnow().isoformat()
        updated['performance_metrics'] = performance_metrics
        
        return updated
    
    async def _update_emotion_chain(self, current: List[Dict[str, Any]], parsed_input) -> List[Dict[str, Any]]:
        """更新情绪链"""
        emotion_chain = current.copy() if current else []
        
        # 添加新的情绪状态
        if hasattr(parsed_input, 'sentiment') and parsed_input.sentiment:
            emotion_state = {
                'emotion': parsed_input.sentiment,
                'intensity': parsed_input.confidence if hasattr(parsed_input, 'confidence') else 0.5,
                'timestamp': datetime.utcnow().isoformat(),
                'trigger': parsed_input.intent if hasattr(parsed_input, 'intent') else 'unknown'
            }
            emotion_chain.append(emotion_state)
        
        # 保持情绪链长度（最近20个情绪状态）
        return emotion_chain[-20:]
    
    async def _update_interaction_history(self, current: List[Dict[str, Any]], parsed_input) -> List[Dict[str, Any]]:
        """更新交互历史"""
        interaction_history = current.copy() if current else []
        
        # 添加新的交互记录
        interaction_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'intent': parsed_input.intent if hasattr(parsed_input, 'intent') else 'unknown',
            'entities': parsed_input.entities if hasattr(parsed_input, 'entities') else {},
            'confidence': parsed_input.confidence if hasattr(parsed_input, 'confidence') else 1.0
        }
        interaction_history.append(interaction_record)
        
        # 保持交互历史长度（最近50个交互）
        return interaction_history[-50:]
    
    async def _build_conversation_state(self, user_id: int, conversation_id: Optional[str], 
                                      ai_character_id: Optional[str], db: Session) -> 'ConversationState':
        """构建对话状态"""
        
        # 获取AI角色信息
        ai_character = None
        if ai_character_id:
            ai_character = db.query(AICharacter).filter(
                AICharacter.character_id == ai_character_id
            ).first()
        
        # 构建默认的六维状态
        role_cognition = {
            'character_identity': ai_character.nickname if ai_character else 'unknown',
            'personality_traits': ai_character.personality.split(',') if ai_character and ai_character.personality else [],
            'knowledge_base': {},
            'memory_context': [],
            'role_boundaries': {},
            'consistency_score': 0.8
        }
        
        interaction_dynamics = {
            'conversation_phase': 'greeting',
            'user_engagement_level': 0.5,
            'response_urgency': 'medium',
            'topic_flow': [],
            'interaction_pattern': 'standard',
            'emotional_resonance': 0.5
        }
        
        expression_rules = {
            'speaking_style': ai_character.speaking_style if ai_character else 'natural',
            'language_level': 'intermediate',
            'humor_preference': 'moderate',
            'formality_level': 'casual',
            'cultural_context': 'neutral',
            'expression_constraints': []
        }
        
        capability_permissions = {
            'available_functions': ['chat', 'question_answer', 'creative_writing'],
            'access_level': 'standard',
            'feature_permissions': {'chat': True, 'question_answer': True, 'creative_writing': True},
            'resource_limits': {'max_tokens': 1000, 'rate_limit': 100},
            'security_constraints': []
        }
        
        environment_scenario = {
            'current_scenario': 'general_chat',
            'time_context': 'afternoon',
            'location_context': 'unknown',
            'social_context': 'one_on_one',
            'activity_context': 'chatting',
            'mood_atmosphere': 'neutral'
        }
        
        dynamic_adjustment = {
            'learning_rate': 0.1,
            'adaptation_level': 'medium',
            'feedback_integration': {},
            'performance_metrics': {'interaction_count': 0},
            'adjustment_history': []
        }
        
        return ConversationState(
            user_id=user_id,
            conversation_id=conversation_id or '',
            ai_character_id=ai_character_id or '',
            role_cognition=role_cognition,
            interaction_dynamics=interaction_dynamics,
            expression_rules=expression_rules,
            capability_permissions=capability_permissions,
            environment_scenario=environment_scenario,
            dynamic_adjustment=dynamic_adjustment,
            emotion_chain=[],
            interaction_history=[],
            context_memory={}
        )
    
    async def _create_default_state(self, user_id: int, conversation_id: Optional[str]) -> 'ConversationState':
        """创建默认状态"""
        return ConversationState(
            user_id=user_id,
            conversation_id=conversation_id or '',
            ai_character_id='',
            role_cognition={
                'character_identity': 'assistant',
                'personality_traits': ['helpful', 'friendly'],
                'knowledge_base': {},
                'memory_context': [],
                'role_boundaries': {},
                'consistency_score': 0.8
            },
            interaction_dynamics={
                'conversation_phase': 'greeting',
                'user_engagement_level': 0.5,
                'response_urgency': 'medium',
                'topic_flow': [],
                'interaction_pattern': 'standard',
                'emotional_resonance': 0.5
            },
            expression_rules={
                'speaking_style': 'natural',
                'language_level': 'intermediate',
                'humor_preference': 'moderate',
                'formality_level': 'casual',
                'cultural_context': 'neutral',
                'expression_constraints': []
            },
            capability_permissions={
                'available_functions': ['chat'],
                'access_level': 'standard',
                'feature_permissions': {'chat': True},
                'resource_limits': {'max_tokens': 500},
                'security_constraints': []
            },
            environment_scenario={
                'current_scenario': 'general_chat',
                'time_context': 'afternoon',
                'location_context': 'unknown',
                'social_context': 'one_on_one',
                'activity_context': 'chatting',
                'mood_atmosphere': 'neutral'
            },
            dynamic_adjustment={
                'learning_rate': 0.1,
                'adaptation_level': 'medium',
                'feedback_integration': {},
                'performance_metrics': {'interaction_count': 0},
                'adjustment_history': []
            },
            emotion_chain=[],
            interaction_history=[],
            context_memory={}
        )
    
    def _dict_to_conversation_state(self, state_dict: Dict[str, Any]) -> 'ConversationState':
        """将字典转换为ConversationState对象"""
        return ConversationState(**state_dict)
    
    async def _persist_state(self, state: 'ConversationState'):
        """持久化状态到缓存"""
        cache_key = f"conversation_state:{state.user_id}:{state.conversation_id}"
        cache_set(cache_key, asdict(state), ttl=self.cache_ttl["conversation_state"])
    
    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """获取用户档案信息"""
        cache_key = f"user_profile:{user_id}"
        
        # 尝试从缓存获取
        cached_profile = cache_get(cache_key)
        if cached_profile:
            return cached_profile
        
        try:
            with get_db_session() as db:
                user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
                if user:
                    profile = {
                        'user_id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'preferences': {},
                        'interaction_history_count': 0
                    }
                    cache_set(cache_key, profile, ttl=self.cache_ttl["user_state"])
                    return profile
        except Exception as e:
            logger.error(f"获取用户档案失败: {e}")
        
        return {}
    
    async def get_character_profile(self, character_id: str) -> Dict[str, Any]:
        """获取AI角色档案信息"""
        if not character_id:
            return {}
        
        cache_key = f"character_profile:{character_id}"
        
        # 尝试从缓存获取
        cached_profile = cache_get(cache_key)
        if cached_profile:
            return cached_profile
        
        try:
            with get_db_session() as db:
                character = db.query(AICharacter).filter(
                    AICharacter.character_id == character_id
                ).first()
                if character:
                    profile = {
                        'character_id': character.character_id,
                        'nickname': character.nickname,
                        'description': character.description,
                        'personality': character.personality,
                        'speaking_style': character.speaking_style,
                        'usage_count': character.usage_count
                    }
                    cache_set(cache_key, profile, ttl=self.cache_ttl["character_state"])
                    return profile
        except Exception as e:
            logger.error(f"获取角色档案失败: {e}")
        
        return {}
    
    async def get_conversation_context(self, conversation_id: str) -> Dict[str, Any]:
        """获取对话上下文"""
        if not conversation_id:
            return {}
        
        cache_key = f"conversation_context:{conversation_id}"
        
        # 尝试从缓存获取
        cached_context = cache_get(cache_key)
        if cached_context:
            return cached_context
        
        try:
            with get_db_session() as db:
                # 获取最近的消息
                messages = db.query(Message).filter(
                    Message.conversation_id == conversation_id
                ).order_by(Message.create_time.desc()).limit(10).all()
                
                context = {
                    'conversation_id': conversation_id,
                    'message_count': len(messages),
                    'recent_messages': [
                        {
                            'message_id': msg.message_id,
                            'content': msg.content,
                            'is_ai_message': msg.is_ai_message,
                            'timestamp': msg.create_time.isoformat()
                        }
                        for msg in messages
                    ]
                }
                
                cache_set(cache_key, context, ttl=self.cache_ttl["conversation_state"])
                return context
                
        except Exception as e:
            logger.error(f"获取对话上下文失败: {e}")
        
        return {}
    
    async def get_environment_context(self, user_id: int, conversation_id: str) -> Dict[str, Any]:
        """获取环境上下文"""
        return {
            'current_time': datetime.utcnow().isoformat(),
            'user_timezone': 'UTC',  # 可以从用户配置获取
            'platform': 'web',
            'session_duration': 0  # 可以从会话开始时间计算
        }
    
    async def update_conversation_state(self, user_id: int, conversation_id: str, 
                                      ai_response, decision):
        """更新对话状态（在AI响应后）"""
        try:
            # 清理相关缓存
            cache_keys = [
                f"conversation_state:{user_id}:{conversation_id}",
                f"conversation_context:{conversation_id}"
            ]
            
            for key in cache_keys:
                cache_delete(key)
            
            log_info("对话状态已更新", user_id=user_id, conversation_id=conversation_id)
            
        except Exception as e:
            logger.error(f"更新对话状态失败: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查数据库连接
            with get_db_session() as db:
                from sqlalchemy import text
                db.execute(text("SELECT 1"))
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "cache_ttl": self.cache_ttl
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
