"""
决策引擎 (DecisionEngine)
基于六维状态指标和上下文数据，智能决策对话流程和响应策略
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from app.core.management.logging_manager import log_operation_start, log_operation_success, log_operation_error, log_info
from app.core.flow.models import ConversationState, FlowDecision

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """决策类型枚举"""
    RESPOND_IMMEDIATELY = "respond_immediately"
    ASK_CLARIFICATION = "ask_clarification"
    PROVIDE_INFORMATION = "provide_information"
    CREATIVE_RESPONSE = "creative_response"
    EMOTIONAL_SUPPORT = "emotional_support"
    TOPIC_SWITCH = "topic_switch"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    DEFER_RESPONSE = "defer_response"

class ActionType(Enum):
    """行动类型枚举"""
    GENERATE_TEXT = "generate_text"
    GENERATE_STREAMING = "generate_streaming"
    REQUEST_MORE_INFO = "request_more_info"
    SWITCH_CHARACTER = "switch_character"
    END_CONVERSATION = "end_conversation"
    SEND_NOTIFICATION = "send_notification"
    TRIGGER_FUNCTION = "trigger_function"

@dataclass
class DecisionContext:
    """决策上下文"""
    user_intent: str
    user_sentiment: Optional[str]
    conversation_phase: str
    user_engagement: float
    topic_continuity: float
    emotional_state: str
    available_functions: List[str]
    resource_availability: Dict[str, Any]
    time_constraints: Dict[str, Any]

@dataclass
class DecisionRule:
    """决策规则"""
    rule_id: str
    condition: Dict[str, Any]
    decision_type: DecisionType
    action_type: ActionType
    parameters: Dict[str, Any]
    priority: int
    confidence_threshold: float

class DecisionEngine:
    """决策引擎"""
    
    def __init__(self):
        self.decision_rules = self._initialize_decision_rules()
        self.decision_history = []
        self.performance_metrics = {
            "total_decisions": 0,
            "successful_decisions": 0,
            "average_confidence": 0.0,
            "decision_type_distribution": {}
        }
    
    async def make_decision(self, state, context: Dict[str, Any], parsed_input) -> 'FlowDecision':
        """
        基于状态和上下文做出决策
        
        Args:
            state: 对话状态
            context: 上下文数据
            parsed_input: 解析后的输入
            
        Returns:
            FlowDecision: 决策结果
        """
        log_operation_start("决策引擎处理", user_id=state.user_id)
        
        try:
            # 构建决策上下文
            decision_context = await self._build_decision_context(state, context, parsed_input)
            
            # 评估决策规则
            applicable_rules = await self._evaluate_rules(decision_context, state)
            
            # 选择最佳决策
            best_decision = await self._select_best_decision(applicable_rules, decision_context)
            
            # 生成决策结果
            decision_result = await self._generate_decision_result(
                best_decision, decision_context, state
            )
            
            # 记录决策历史
            self._record_decision(decision_result)
            
            log_operation_success("决策引擎处理", user_id=state.user_id, 
                                decision_type=decision_result.decision_type)
            
            return decision_result
            
        except Exception as e:
            log_operation_error("决策引擎处理", str(e), user_id=state.user_id)
            
            # 返回默认决策
            return FlowDecision(
                decision_type="respond_immediately",
                action="generate_text",
                parameters={"fallback": True, "error_handled": True},
                confidence=0.5,
                reasoning="决策引擎异常，使用默认响应",
                next_steps=["monitor_system_health"],
                state_changes={}
            )
    
    async def _build_decision_context(self, state, context: Dict[str, Any], parsed_input) -> DecisionContext:
        """构建决策上下文"""
        
        # 提取用户意图和情感
        user_intent = getattr(parsed_input, 'intent', 'unknown')
        user_sentiment = getattr(parsed_input, 'sentiment', None)
        
        # 从状态中提取关键信息
        conversation_phase = state.interaction_dynamics.get('conversation_phase', 'main')
        user_engagement = state.interaction_dynamics.get('user_engagement_level', 0.5)
        
        # 计算话题连续性
        topic_continuity = await self._calculate_topic_continuity(state, parsed_input)
        
        # 确定情感状态
        emotional_state = await self._determine_emotional_state(state, parsed_input)
        
        # 获取可用功能
        available_functions = state.capability_permissions.get('available_functions', ['chat'])
        
        # 资源可用性
        resource_availability = state.capability_permissions.get('resource_limits', {})
        
        # 时间约束
        time_constraints = {
            'response_deadline': 30,  # 30秒响应超时
            'processing_priority': 'normal'
        }
        
        return DecisionContext(
            user_intent=user_intent,
            user_sentiment=user_sentiment,
            conversation_phase=conversation_phase,
            user_engagement=user_engagement,
            topic_continuity=topic_continuity,
            emotional_state=emotional_state,
            available_functions=available_functions,
            resource_availability=resource_availability,
            time_constraints=time_constraints
        )
    
    async def _evaluate_rules(self, context: DecisionContext, state) -> List[Dict[str, Any]]:
        """评估适用的决策规则"""
        applicable_rules = []
        
        for rule in self.decision_rules:
            if await self._evaluate_rule_condition(rule, context, state):
                rule_result = {
                    'rule': rule,
                    'match_score': await self._calculate_match_score(rule, context, state),
                    'priority': rule.priority,
                    'confidence': await self._calculate_confidence(rule, context, state)
                }
                applicable_rules.append(rule_result)
        
        # 按优先级和匹配分数排序
        applicable_rules.sort(key=lambda x: (x['priority'], x['match_score']), reverse=True)
        
        return applicable_rules
    
    async def _evaluate_rule_condition(self, rule: DecisionRule, context: DecisionContext, state) -> bool:
        """评估规则条件是否满足"""
        condition = rule.condition
        
        try:
            # 检查用户意图匹配
            if 'intent' in condition:
                if not self._match_pattern(context.user_intent, condition['intent']):
                    return False
            
            # 检查对话阶段
            if 'conversation_phase' in condition:
                if context.conversation_phase != condition['conversation_phase']:
                    return False
            
            # 检查用户参与度
            if 'min_engagement' in condition:
                if context.user_engagement < condition['min_engagement']:
                    return False
            
            # 检查情感状态
            if 'sentiment' in condition:
                if context.user_sentiment != condition['sentiment']:
                    return False
            
            # 检查可用功能
            if 'required_functions' in condition:
                required = condition['required_functions']
                if not all(func in context.available_functions for func in required):
                    return False
            
            # 检查角色一致性评分
            if 'min_consistency' in condition:
                consistency_score = state.role_cognition.get('consistency_score', 0.5)
                if consistency_score < condition['min_consistency']:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"评估规则条件失败: {e}")
            return False
    
    def _match_pattern(self, text: str, pattern: str) -> bool:
        """简单的模式匹配"""
        if isinstance(pattern, str):
            return pattern.lower() in text.lower()
        elif isinstance(pattern, list):
            return any(p.lower() in text.lower() for p in pattern)
        return False
    
    async def _calculate_match_score(self, rule: DecisionRule, context: DecisionContext, state) -> float:
        """计算规则匹配分数"""
        score = 0.0
        total_weight = 0.0
        
        # 意图匹配权重
        if 'intent' in rule.condition:
            if self._match_pattern(context.user_intent, rule.condition['intent']):
                score += 0.3
            total_weight += 0.3
        
        # 对话阶段匹配权重
        if 'conversation_phase' in rule.condition:
            if context.conversation_phase == rule.condition['conversation_phase']:
                score += 0.2
            total_weight += 0.2
        
        # 用户参与度权重
        if 'min_engagement' in rule.condition:
            engagement_score = min(context.user_engagement / 0.8, 1.0)
            score += engagement_score * 0.2
            total_weight += 0.2
        
        # 情感匹配权重
        if 'sentiment' in rule.condition:
            if context.user_sentiment == rule.condition['sentiment']:
                score += 0.15
            total_weight += 0.15
        
        # 角色一致性权重
        consistency_score = state.role_cognition.get('consistency_score', 0.5)
        score += consistency_score * 0.15
        total_weight += 0.15
        
        return score / total_weight if total_weight > 0 else 0.0
    
    async def _calculate_confidence(self, rule: DecisionRule, context: DecisionContext, state) -> float:
        """计算决策置信度"""
        base_confidence = 0.7
        
        # 根据用户参与度调整
        engagement_factor = context.user_engagement * 0.2
        
        # 根据话题连续性调整
        continuity_factor = context.topic_continuity * 0.2
        
        # 根据角色一致性调整
        consistency_factor = state.role_cognition.get('consistency_score', 0.5) * 0.1
        
        confidence = base_confidence + engagement_factor + continuity_factor + consistency_factor
        
        return min(max(confidence, 0.0), 1.0)
    
    async def _select_best_decision(self, applicable_rules: List[Dict[str, Any]], 
                                  context: DecisionContext) -> Dict[str, Any]:
        """选择最佳决策"""
        if not applicable_rules:
            # 返回默认决策
            return {
                'rule': DecisionRule(
                    rule_id="default",
                    condition={},
                    decision_type=DecisionType.RESPOND_IMMEDIATELY,
                    action_type=ActionType.GENERATE_TEXT,
                    parameters={"fallback": True},
                    priority=0,
                    confidence_threshold=0.0
                ),
                'match_score': 0.5,
                'priority': 0,
                'confidence': 0.5
            }
        
        # 选择置信度最高的规则
        best_rule = max(applicable_rules, key=lambda x: x['confidence'])
        
        # 确保置信度超过阈值
        if best_rule['confidence'] < best_rule['rule'].confidence_threshold:
            # 降级到默认决策
            return {
                'rule': DecisionRule(
                    rule_id="fallback",
                    condition={},
                    decision_type=DecisionType.RESPOND_IMMEDIATELY,
                    action_type=ActionType.GENERATE_TEXT,
                    parameters={"low_confidence": True},
                    priority=0,
                    confidence_threshold=0.0
                ),
                'match_score': 0.3,
                'priority': 0,
                'confidence': 0.3
            }
        
        return best_rule
    
    async def _generate_decision_result(self, rule_result: Dict[str, Any], 
                                      context: DecisionContext, state) -> 'FlowDecision':
        """生成决策结果"""
        rule = rule_result['rule']
        confidence = rule_result['confidence']
        
        # 生成推理说明
        reasoning = await self._generate_reasoning(rule, context, confidence)
        
        # 确定下一步行动
        next_steps = await self._determine_next_steps(rule, context)
        
        # 确定状态变更
        state_changes = await self._determine_state_changes(rule, context, state)
        
        return FlowDecision(
            decision_type=rule.decision_type.value,
            action=rule.action_type.value,
            parameters=rule.parameters.copy(),
            confidence=confidence,
            reasoning=reasoning,
            next_steps=next_steps,
            state_changes=state_changes
        )
    
    async def _generate_reasoning(self, rule: DecisionRule, context: DecisionContext, confidence: float) -> str:
        """生成决策推理说明"""
        reasoning_parts = []
        
        # 基于规则类型生成推理
        if rule.decision_type == DecisionType.RESPOND_IMMEDIATELY:
            reasoning_parts.append("用户输入清晰，可以立即响应")
        
        elif rule.decision_type == DecisionType.ASK_CLARIFICATION:
            reasoning_parts.append("用户输入需要澄清")
        
        elif rule.decision_type == DecisionType.PROVIDE_INFORMATION:
            reasoning_parts.append("用户请求信息，提供详细回复")
        
        elif rule.decision_type == DecisionType.CREATIVE_RESPONSE:
            reasoning_parts.append("用户请求创造性内容")
        
        elif rule.decision_type == DecisionType.EMOTIONAL_SUPPORT:
            reasoning_parts.append("检测到用户需要情感支持")
        
        # 添加置信度信息
        if confidence > 0.8:
            reasoning_parts.append("高置信度决策")
        elif confidence > 0.6:
            reasoning_parts.append("中等置信度决策")
        else:
            reasoning_parts.append("低置信度决策，使用保守策略")
        
        return "；".join(reasoning_parts)
    
    async def _determine_next_steps(self, rule: DecisionRule, context: DecisionContext) -> List[str]:
        """确定下一步行动"""
        next_steps = []
        
        if rule.action_type == ActionType.GENERATE_TEXT:
            next_steps.append("generate_response")
            next_steps.append("update_conversation_state")
        
        elif rule.action_type == ActionType.GENERATE_STREAMING:
            next_steps.append("start_streaming_response")
            next_steps.append("stream_response_chunks")
            next_steps.append("finalize_streaming")
        
        elif rule.action_type == ActionType.REQUEST_MORE_INFO:
            next_steps.append("prepare_clarification_question")
            next_steps.append("send_question")
            next_steps.append("wait_for_user_response")
        
        elif rule.action_type == ActionType.SWITCH_CHARACTER:
            next_steps.append("validate_character_switch")
            next_steps.append("update_character_context")
            next_steps.append("notify_character_change")
        
        else:
            next_steps.append("execute_action")
            next_steps.append("monitor_result")
        
        return next_steps
    
    async def _determine_state_changes(self, rule: DecisionRule, context: DecisionContext, state) -> Dict[str, Any]:
        """确定状态变更"""
        state_changes = {}
        
        # 基于决策类型确定状态变更
        if rule.decision_type == DecisionType.TOPIC_SWITCH:
            state_changes['topic_flow'] = context.user_intent
            state_changes['conversation_phase'] = 'main'
        
        elif rule.decision_type == DecisionType.EMOTIONAL_SUPPORT:
            state_changes['emotional_resonance'] = min(state.interaction_dynamics.get('emotional_resonance', 0.5) + 0.2, 1.0)
        
        elif rule.decision_type == DecisionType.ASK_CLARIFICATION:
            state_changes['response_urgency'] = 'low'
            state_changes['conversation_phase'] = 'clarification'
        
        # 更新交互历史
        state_changes['last_decision'] = {
            'decision_type': rule.decision_type.value,
            'action': rule.action_type.value,
            'timestamp': datetime.utcnow().isoformat(),
            'confidence': rule_result['confidence'] if 'rule_result' in locals() else 0.5
        }
        
        return state_changes
    
    async def _calculate_topic_continuity(self, state, parsed_input) -> float:
        """计算话题连续性"""
        # 简单的连续性计算
        interaction_history = state.interaction_history
        if len(interaction_history) < 2:
            return 0.5
        
        # 比较最近两次交互的意图
        recent_intents = [h.get('intent', '') for h in interaction_history[-2:]]
        if recent_intents[0] == recent_intents[1]:
            return 0.8
        else:
            return 0.3
    
    async def _determine_emotional_state(self, state, parsed_input) -> str:
        """确定情感状态"""
        # 从情绪链中获取最新情感
        emotion_chain = state.emotion_chain
        if emotion_chain:
            latest_emotion = emotion_chain[-1].get('emotion', 'neutral')
            return latest_emotion
        
        # 从解析输入中获取情感
        if hasattr(parsed_input, 'sentiment'):
            return parsed_input.sentiment or 'neutral'
        
        return 'neutral'
    
    def _record_decision(self, decision: 'FlowDecision'):
        """记录决策历史"""
        decision_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'decision_type': decision.decision_type,
            'action': decision.action,
            'confidence': decision.confidence,
            'reasoning': decision.reasoning
        }
        
        self.decision_history.append(decision_record)
        
        # 保持历史记录长度
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]
        
        # 更新性能指标
        self._update_performance_metrics(decision)
    
    def _update_performance_metrics(self, decision: 'FlowDecision'):
        """更新性能指标"""
        self.performance_metrics['total_decisions'] += 1
        
        if decision.confidence > 0.6:
            self.performance_metrics['successful_decisions'] += 1
        
        # 更新平均置信度
        total_confidence = self.performance_metrics['average_confidence'] * (self.performance_metrics['total_decisions'] - 1)
        self.performance_metrics['average_confidence'] = (total_confidence + decision.confidence) / self.performance_metrics['total_decisions']
        
        # 更新决策类型分布
        decision_type = decision.decision_type
        if decision_type not in self.performance_metrics['decision_type_distribution']:
            self.performance_metrics['decision_type_distribution'][decision_type] = 0
        self.performance_metrics['decision_type_distribution'][decision_type] += 1
    
    def _initialize_decision_rules(self) -> List[DecisionRule]:
        """初始化决策规则"""
        rules = [
            # 立即响应规则
            DecisionRule(
                rule_id="immediate_response",
                condition={
                    'intent': ['greeting', 'question', 'request'],
                    'min_engagement': 0.3
                },
                decision_type=DecisionType.RESPOND_IMMEDIATELY,
                action_type=ActionType.GENERATE_TEXT,
                parameters={'response_style': 'direct', 'max_tokens': 500},
                priority=10,
                confidence_threshold=0.6
            ),
            
            # 澄清问题规则
            DecisionRule(
                rule_id="clarification_needed",
                condition={
                    'intent': ['unclear', 'ambiguous'],
                    'min_engagement': 0.2
                },
                decision_type=DecisionType.ASK_CLARIFICATION,
                action_type=ActionType.REQUEST_MORE_INFO,
                parameters={'question_type': 'clarification'},
                priority=8,
                confidence_threshold=0.5
            ),
            
            # 情感支持规则
            DecisionRule(
                rule_id="emotional_support",
                condition={
                    'sentiment': ['negative', 'sad', 'frustrated'],
                    'min_engagement': 0.4
                },
                decision_type=DecisionType.EMOTIONAL_SUPPORT,
                action_type=ActionType.GENERATE_TEXT,
                parameters={'response_style': 'empathetic', 'tone': 'supportive'},
                priority=9,
                confidence_threshold=0.7
            ),
            
            # 创造性响应规则
            DecisionRule(
                rule_id="creative_response",
                condition={
                    'intent': ['creative', 'story', 'imagination'],
                    'required_functions': ['creative_writing']
                },
                decision_type=DecisionType.CREATIVE_RESPONSE,
                action_type=ActionType.GENERATE_STREAMING,
                parameters={'response_style': 'creative', 'streaming': True},
                priority=7,
                confidence_threshold=0.6
            ),
            
            # 话题切换规则
            DecisionRule(
                rule_id="topic_switch",
                condition={
                    'intent': ['topic_change', 'new_subject'],
                    'min_engagement': 0.5
                },
                decision_type=DecisionType.TOPIC_SWITCH,
                action_type=ActionType.GENERATE_TEXT,
                parameters={'response_style': 'transitional'},
                priority=6,
                confidence_threshold=0.6
            ),
            
            # 默认响应规则
            DecisionRule(
                rule_id="default_response",
                condition={},
                decision_type=DecisionType.RESPOND_IMMEDIATELY,
                action_type=ActionType.GENERATE_TEXT,
                parameters={'response_style': 'general', 'fallback': True},
                priority=1,
                confidence_threshold=0.0
            )
        ]
        
        return rules
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        metrics = self.performance_metrics.copy()
        
        # 计算成功率
        if metrics['total_decisions'] > 0:
            metrics['success_rate'] = metrics['successful_decisions'] / metrics['total_decisions']
        else:
            metrics['success_rate'] = 0.0
        
        # 添加最近决策历史
        metrics['recent_decisions'] = self.decision_history[-10:]
        
        return metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查决策规则数量
            rules_count = len(self.decision_rules)
            
            # 检查历史记录
            history_count = len(self.decision_history)
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "rules_count": rules_count,
                "history_count": history_count,
                "performance_metrics": self.get_performance_metrics()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
