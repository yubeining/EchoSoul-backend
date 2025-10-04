"""
AI聊天架构核心数据模型
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class MessageType(Enum):
    """消息类型枚举"""
    START_AI_SESSION = "start_ai_session"
    END_AI_SESSION = "end_ai_session"
    CHAT_MESSAGE = "chat_message"
    GET_CONVERSATION_HISTORY = "get_conversation_history"
    GET_AI_CHARACTERS = "get_ai_characters"
    PING = "ping"
    GET_USER_STATE = "get_user_state"
    UPDATE_USER_PREFERENCES = "update_user_preferences"
    SWITCH_AI_CHARACTER = "switch_ai_character"

@dataclass
class UserInput:
    """用户输入数据结构"""
    user_id: int
    message_type: MessageType
    content: Optional[str] = None
    conversation_id: Optional[str] = None
    ai_character_id: Optional[str] = None
    message_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class ParsedEntity:
    """解析的实体"""
    entity_type: str
    value: str
    confidence: float
    position: tuple  # (start, end) 在原文中的位置

@dataclass
class ParsedInput:
    """解析后的输入数据"""
    original_text: str
    intent: str
    entities: List[ParsedEntity]
    sentiment: Optional[str] = None
    confidence: float = 1.0
    language: str = "unknown"
    processing_metadata: Optional[Dict[str, Any]] = None

@dataclass
class ConversationState:
    """对话状态数据结构"""
    user_id: int
    conversation_id: str
    ai_character_id: str
    # 六维状态指标
    role_cognition: Dict[str, Any]  # 角色认知维度
    interaction_dynamics: Dict[str, Any]  # 交互动态维度
    expression_rules: Dict[str, Any]  # 表达规则维度
    capability_permissions: Dict[str, Any]  # 能力权限维度
    environment_scenario: Dict[str, Any]  # 环境场景维度
    dynamic_adjustment: Dict[str, Any]  # 动态调整维度
    # 其他状态信息
    emotion_chain: List[Dict[str, Any]]  # 情绪链
    interaction_history: List[Dict[str, Any]]  # 交互历史
    context_memory: Dict[str, Any]  # 上下文记忆
    last_update_time: datetime = None
    
    def __post_init__(self):
        if self.last_update_time is None:
            self.last_update_time = datetime.utcnow()

@dataclass
class FlowDecision:
    """流程决策结果"""
    decision_type: str
    action: str
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str
    next_steps: List[str]
    state_changes: Dict[str, Any]

@dataclass
class AIResponse:
    """AI响应数据结构"""
    user_id: int
    conversation_id: str
    message_id: str
    content: str
    message_type: str = "text"
    is_streaming: bool = False
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
