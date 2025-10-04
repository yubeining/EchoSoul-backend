"""
输出适配器 (OutputAdapter)
基于决策结果和状态生成AI响应，支持多种输出格式和流式响应
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from app.core.management.logging_manager import log_operation_start, log_operation_success, log_operation_error, log_info
from app.core.flow.models import FlowDecision, ConversationState, UserInput, AIResponse
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    """响应类型枚举"""
    TEXT = "text"
    STREAMING = "streaming"
    STRUCTURED = "structured"
    MULTIMEDIA = "multimedia"
    ERROR = "error"

class ResponseStyle(Enum):
    """响应风格枚举"""
    DIRECT = "direct"
    EMPATHETIC = "empathetic"
    CREATIVE = "creative"
    FORMAL = "formal"
    CASUAL = "casual"
    SUPPORTIVE = "supportive"

@dataclass
class ResponseMetadata:
    """响应元数据"""
    generation_time: float
    token_count: int
    model_used: str
    confidence_score: float
    response_style: str
    processing_notes: List[str]

class OutputAdapter:
    """输出适配器"""
    
    def __init__(self):
        
        # 响应模板
        self.response_templates = {
            "greeting": "你好！我是{character_name}，很高兴见到你！{character_description}",
            "question": "关于{question_topic}，让我来为你解答：{answer}",
            "emotional_support": "我理解你的感受。{supportive_message}",
            "creative_request": "好的，让我为你创作一个{creative_type}：{content}",
            "clarification": "我需要更多信息来帮助你。能否详细说明一下{clarification_point}？",
            "error": "抱歉，处理你的请求时遇到了问题：{error_message}。请稍后再试。"
        }
        
        # 处理统计
        self.stats = {
            "total_responses": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "average_generation_time": 0.0,
            "response_type_distribution": {}
        }
    
    async def generate_response(self, decision, state, user_input) -> 'AIResponse':
        """
        生成AI响应
        
        Args:
            decision: 决策结果
            state: 对话状态
            user_input: 用户输入
            
        Returns:
            AIResponse: AI响应结果
        """
        log_operation_start("生成AI响应", user_id=user_input.user_id, 
                          decision_type=decision.decision_type)
        
        start_time = datetime.utcnow()
        
        try:
            # 1. 确定响应策略
            response_strategy = await self._determine_response_strategy(decision, state)
            
            # 2. 生成响应内容
            response_content = await self._generate_response_content(
                decision, state, user_input, response_strategy
            )
            
            # 3. 应用角色风格
            styled_content = await self._apply_character_style(
                response_content, state, response_strategy
            )
            
            # 4. 构建响应元数据
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            response_metadata = await self._build_response_metadata(
                generation_time, response_strategy, decision
            )
            
            # 5. 构建AI响应对象
            ai_response = AIResponse(
                user_id=user_input.user_id,
                conversation_id=user_input.conversation_id or "",
                message_id=user_input.message_id or str(uuid.uuid4()),
                content=styled_content,
                message_type=response_strategy.get("response_type", "text"),
                is_streaming=response_strategy.get("streaming", False),
                metadata=asdict(response_metadata)
            )
            
            # 更新统计信息
            self._update_stats(response_strategy, generation_time, success=True)
            
            log_operation_success("生成AI响应", user_id=user_input.user_id, 
                                generation_time=generation_time)
            
            return ai_response
            
        except Exception as e:
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats({"response_type": "error"}, generation_time, success=False)
            
            log_operation_error("生成AI响应", str(e), user_id=user_input.user_id)
            
            # 返回错误响应
            return AIResponse(
                user_id=user_input.user_id,
                conversation_id=user_input.conversation_id or "",
                message_id=user_input.message_id or str(uuid.uuid4()),
                content=f"抱歉，我遇到了一些技术问题，无法正常回复。请稍后再试。",
                message_type="error",
                is_streaming=False,
                metadata={"error": str(e)}
            )
    
    async def _determine_response_strategy(self, decision, state) -> Dict[str, Any]:
        """确定响应策略"""
        strategy = {
            "response_type": "text",
            "response_style": "direct",
            "streaming": False,
            "max_tokens": 500,
            "temperature": 0.7,
            "use_template": False,
            "custom_instructions": []
        }
        
        # 基于决策类型确定策略
        decision_type = decision.decision_type
        
        if decision_type == "respond_immediately":
            strategy.update({
                "response_type": "text",
                "response_style": "direct",
                "max_tokens": 300,
                "temperature": 0.7
            })
        
        elif decision_type == "ask_clarification":
            strategy.update({
                "response_type": "text",
                "response_style": "formal",
                "max_tokens": 200,
                "temperature": 0.5,
                "use_template": True,
                "template_key": "clarification"
            })
        
        elif decision_type == "emotional_support":
            strategy.update({
                "response_type": "text",
                "response_style": "empathetic",
                "max_tokens": 400,
                "temperature": 0.8,
                "use_template": True,
                "template_key": "emotional_support"
            })
        
        elif decision_type == "creative_response":
            strategy.update({
                "response_type": "streaming",
                "response_style": "creative",
                "streaming": True,
                "max_tokens": 800,
                "temperature": 0.9,
                "use_template": True,
                "template_key": "creative_request"
            })
        
        elif decision_type == "provide_information":
            strategy.update({
                "response_type": "structured",
                "response_style": "formal",
                "max_tokens": 600,
                "temperature": 0.6
            })
        
        # 基于角色状态调整策略
        character_style = state.expression_rules.get('speaking_style', 'natural')
        if character_style == 'formal':
            strategy['response_style'] = 'formal'
            strategy['temperature'] = min(strategy['temperature'], 0.6)
        elif character_style == 'casual':
            strategy['response_style'] = 'casual'
            strategy['temperature'] = max(strategy['temperature'], 0.8)
        
        # 基于用户参与度调整
        user_engagement = state.interaction_dynamics.get('user_engagement_level', 0.5)
        if user_engagement > 0.8:
            strategy['max_tokens'] = min(strategy['max_tokens'] * 1.5, 1000)
        elif user_engagement < 0.3:
            strategy['max_tokens'] = max(strategy['max_tokens'] * 0.7, 100)
        
        return strategy
    
    async def _generate_response_content(self, decision, state, user_input, strategy: Dict[str, Any]) -> str:
        """生成响应内容"""
        
        # 如果使用模板，先尝试模板生成
        if strategy.get("use_template") and strategy.get("template_key"):
            template_content = await self._generate_from_template(
                strategy["template_key"], decision, state, user_input
            )
            if template_content:
                return template_content
        
        # 使用LLM生成响应
        try:
            # 构建提示词
            prompt = await self._build_generation_prompt(decision, state, user_input, strategy)
            
            # 调用LLM服务
            if strategy.get("streaming", False):
                # 流式生成（这里简化为非流式）
                response = await self._generate_streaming_response(prompt, strategy)
            else:
                response = await self._generate_text_response(prompt, strategy)
            
            return response or "抱歉，我暂时无法生成回复。"
            
        except Exception as e:
            logger.error(f"生成响应内容失败: {e}")
            return f"抱歉，生成回复时遇到了问题：{str(e)}"
    
    async def _generate_from_template(self, template_key: str, decision, state, user_input) -> Optional[str]:
        """从模板生成响应"""
        try:
            template = self.response_templates.get(template_key)
            if not template:
                return None
            
            # 获取角色信息
            character_name = state.role_cognition.get('character_identity', 'AI助手')
            character_description = state.role_cognition.get('personality_traits', ['友好', '乐于助人'])
            
            # 根据模板类型填充内容
            if template_key == "greeting":
                return template.format(
                    character_name=character_name,
                    character_description=f"我是一个{', '.join(character_description[:2])}的AI"
                )
            
            elif template_key == "clarification":
                user_content = user_input.content or ""
                return template.format(clarification_point="你的具体需求")
            
            elif template_key == "emotional_support":
                return template.format(supportive_message="我会尽力帮助你。")
            
            elif template_key == "creative_request":
                return template.format(creative_type="创意内容", content="[创意内容]")
            
            elif template_key == "error":
                error_msg = decision.parameters.get("error_message", "未知错误")
                return template.format(error_message=error_msg)
            
            return template
            
        except Exception as e:
            logger.error(f"模板生成失败: {e}")
            return None
    
    async def _build_generation_prompt(self, decision, state, user_input, strategy: Dict[str, Any]) -> str:
        """构建生成提示词"""
        
        # 基础角色信息
        character_name = state.role_cognition.get('character_identity', 'AI助手')
        personality = ', '.join(state.role_cognition.get('personality_traits', ['友好', '乐于助人']))
        speaking_style = state.expression_rules.get('speaking_style', '自然')
        
        # 用户输入
        user_content = user_input.content or ""
        
        # 对话上下文
        conversation_phase = state.interaction_dynamics.get('conversation_phase', 'main')
        user_engagement = state.interaction_dynamics.get('user_engagement_level', 0.5)
        
        # 构建提示词
        prompt_parts = [
            f"你是{character_name}，一个{personality}的AI助手。",
            f"你的说话风格是：{speaking_style}。",
            f"当前对话阶段：{conversation_phase}。",
            f"用户参与度：{user_engagement:.1f}。",
            "",
            f"用户说：{user_content}",
            "",
            "请根据你的角色设定和当前情况，给出合适的回复。"
        ]
        
        # 添加特殊指令
        if decision.decision_type == "emotional_support":
            prompt_parts.append("请以同理心和关怀的语气回复。")
        elif decision.decision_type == "creative_response":
            prompt_parts.append("请发挥创意，给出有趣的内容。")
        elif decision.decision_type == "ask_clarification":
            prompt_parts.append("请礼貌地询问更多细节。")
        
        return "\n".join(prompt_parts)
    
    async def _generate_text_response(self, prompt: str, strategy: Dict[str, Any]) -> str:
        """生成文本响应"""
        try:
            # 调用LLM服务
            response = await LLMService.simple_chat(
                user_message=prompt,
                system_prompt=strategy.get("system_prompt", "你是一个友好的AI助手"),
                max_tokens=strategy.get("max_tokens", 500),
                temperature=strategy.get("temperature", 0.7)
            )
            
            return response or "抱歉，我暂时无法生成回复。"
            
        except Exception as e:
            logger.error(f"文本生成失败: {e}")
            return f"抱歉，生成回复时遇到了问题。"
    
    async def _generate_streaming_response(self, prompt: str, strategy: Dict[str, Any]) -> str:
        """生成流式响应（简化实现）"""
        try:
            # 这里可以集成真正的流式LLM服务
            # 目前简化为普通文本生成
            response = await self._generate_text_response(prompt, strategy)
            
            # 模拟流式效果，将响应分块
            chunks = self._split_into_chunks(response, chunk_size=50)
            return "".join(chunks)  # 返回完整响应，实际应该逐块发送
            
        except Exception as e:
            logger.error(f"流式生成失败: {e}")
            return "抱歉，生成流式回复时遇到了问题。"
    
    def _split_into_chunks(self, text: str, chunk_size: int = 50) -> List[str]:
        """将文本分割成块"""
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks
    
    async def _apply_character_style(self, content: str, state, strategy: Dict[str, Any]) -> str:
        """应用角色风格"""
        if not content:
            return content
        
        # 获取角色风格设置
        speaking_style = state.expression_rules.get('speaking_style', 'natural')
        formality_level = state.expression_rules.get('formality_level', 'casual')
        humor_preference = state.expression_rules.get('humor_preference', 'moderate')
        
        # 应用正式程度
        if formality_level == 'formal':
            # 移除过于随意的表达
            content = content.replace('哈哈', '')
            content = content.replace('嗯嗯', '是的')
        elif formality_level == 'casual':
            # 添加更随意的表达
            if not any(word in content for word in ['哦', '嗯', '呢']):
                if content.endswith('。'):
                    content = content[:-1] + '呢。'
        
        # 应用幽默偏好
        if humor_preference == 'high' and '哈哈' not in content:
            # 可以在适当位置添加幽默元素（这里简化处理）
            pass
        elif humor_preference == 'low':
            # 移除幽默元素
            content = content.replace('哈哈', '')
        
        return content
    
    async def _build_response_metadata(self, generation_time: float, strategy: Dict[str, Any], decision) -> ResponseMetadata:
        """构建响应元数据"""
        return ResponseMetadata(
            generation_time=generation_time,
            token_count=strategy.get("max_tokens", 500),
            model_used="llm_service",  # 实际应该从LLM服务获取
            confidence_score=decision.confidence,
            response_style=strategy.get("response_style", "direct"),
            processing_notes=[
                f"决策类型: {decision.decision_type}",
                f"响应策略: {strategy.get('response_type', 'text')}",
                f"生成时间: {generation_time:.2f}s"
            ]
        )
    
    def _update_stats(self, strategy: Dict[str, Any], generation_time: float, success: bool):
        """更新统计信息"""
        self.stats["total_responses"] += 1
        
        if success:
            self.stats["successful_responses"] += 1
        else:
            self.stats["failed_responses"] += 1
        
        # 更新平均生成时间
        total_time = self.stats["average_generation_time"] * (self.stats["total_responses"] - 1)
        self.stats["average_generation_time"] = (total_time + generation_time) / self.stats["total_responses"]
        
        # 更新响应类型分布
        response_type = strategy.get("response_type", "text")
        if response_type not in self.stats["response_type_distribution"]:
            self.stats["response_type_distribution"][response_type] = 0
        self.stats["response_type_distribution"][response_type] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        
        # 计算成功率
        if stats["total_responses"] > 0:
            stats["success_rate"] = stats["successful_responses"] / stats["total_responses"]
        else:
            stats["success_rate"] = 0.0
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试LLM服务连接
            test_prompt = "你好，请简单回复。"
            test_response = await LLMService.simple_chat(
                user_message=test_prompt,
                system_prompt="你是一个友好的AI助手",
                max_tokens=50,
                temperature=0.7
            )
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "llm_service_status": "connected",
                "test_response_length": len(test_response) if test_response else 0,
                "stats": self.get_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "llm_service_status": "disconnected"
            }
