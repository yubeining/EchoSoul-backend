"""
统一流程处理模块 (FlowProcessor)
处理用户输入后的完整流程：用户输入 → 状态更新 → 模块调用 → 流程决策 → 输出反馈
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from app.core.management.logging_manager import log_operation_start, log_operation_success, log_operation_error, log_info
from app.core.flow.models import UserInput, MessageType, ConversationState, FlowDecision, AIResponse, ParsedInput
from app.core.flow.state_manager import StateManager
from app.core.flow.decision_engine import DecisionEngine
from app.core.flow.input_parser import InputParser
from app.core.flow.output_adapter import OutputAdapter
from app.core.flow.langgraph_flow import LangGraphFlow

logger = logging.getLogger(__name__)

# 数据模型已移至 app.core.models

class FlowProcessor:
    """
    统一流程处理模块 - 处理用户输入后的完整流程
    流程：用户输入 → 状态更新 → 模块调用 → 流程决策 → 输出反馈
    """
    
    def __init__(self):
        self.input_parser = InputParser()
        self.state_manager = StateManager()
        self.decision_engine = DecisionEngine()
        self.output_adapter = OutputAdapter()
        self.langgraph_flow = LangGraphFlow()
        
        # 处理统计
        self.stats = {
            "total_processed": 0,
            "successful_processed": 0,
            "failed_processed": 0,
            "average_processing_time": 0.0
        }
    
    async def process_user_input(self, user_input: UserInput) -> AIResponse:
        """
        处理用户输入的完整流程
        
        Args:
            user_input: 用户输入数据
            
        Returns:
            AIResponse: AI响应结果
        """
        start_time = datetime.utcnow()
        log_operation_start("处理用户输入", user_id=user_input.user_id, 
                          message_type=user_input.message_type.value)
        
        try:
            # 1. 输入解析阶段
            parsed_input = await self.input_parser.parse(user_input)
            log_info("输入解析完成", user_id=user_input.user_id, 
                    intent=parsed_input.intent, confidence=parsed_input.confidence)
            
            # 2. 状态更新阶段
            updated_state = await self.state_manager.update_state(
                user_id=user_input.user_id,
                conversation_id=user_input.conversation_id,
                parsed_input=parsed_input
            )
            log_info("状态更新完成", user_id=user_input.user_id, 
                    conversation_id=user_input.conversation_id)
            
            # 3. 模块调用阶段
            context_data = await self._call_core_modules(updated_state, parsed_input)
            log_info("核心模块调用完成", user_id=user_input.user_id)
            
            # 4. 流程决策阶段
            decision_result = await self.decision_engine.make_decision(
                state=updated_state,
                context=context_data,
                parsed_input=parsed_input
            )
            log_info("流程决策完成", user_id=user_input.user_id, 
                    decision_type=decision_result.decision_type)
            
            # 5. 输出反馈阶段
            ai_response = await self.output_adapter.generate_response(
                decision=decision_result,
                state=updated_state,
                user_input=user_input
            )
            
            # 更新状态
            await self.state_manager.update_conversation_state(
                user_id=user_input.user_id,
                conversation_id=user_input.conversation_id,
                ai_response=ai_response,
                decision=decision_result
            )
            
            # 更新统计信息
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats(processing_time, success=True)
            
            log_operation_success("处理用户输入", user_id=user_input.user_id, 
                                processing_time=processing_time)
            
            return ai_response
            
        except Exception as e:
            # 更新统计信息
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_stats(processing_time, success=False)
            
            log_operation_error("处理用户输入", str(e), user_id=user_input.user_id)
            
            # 返回错误响应
            return AIResponse(
                user_id=user_input.user_id,
                conversation_id=user_input.conversation_id or "",
                message_id=user_input.message_id or "",
                content=f"抱歉，处理您的请求时出现了错误：{str(e)}",
                message_type="error"
            )
    
    async def _call_core_modules(self, state: ConversationState, parsed_input: ParsedInput) -> Dict[str, Any]:
        """
        调用核心模块获取上下文数据
        
        Args:
            state: 对话状态
            parsed_input: 解析后的输入
            
        Returns:
            Dict[str, Any]: 上下文数据
        """
        context_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_profile": {},
            "character_profile": {},
            "conversation_context": {},
            "environment_context": {}
        }
        
        try:
            # 获取用户档案信息
            context_data["user_profile"] = await self.state_manager.get_user_profile(state.user_id)
            
            # 获取AI角色档案信息
            context_data["character_profile"] = await self.state_manager.get_character_profile(state.ai_character_id)
            
            # 获取对话上下文
            context_data["conversation_context"] = await self.state_manager.get_conversation_context(
                state.conversation_id
            )
            
            # 获取环境上下文
            context_data["environment_context"] = await self.state_manager.get_environment_context(
                state.user_id, state.conversation_id
            )
            
            # 添加解析输入的信息
            context_data["parsed_input"] = asdict(parsed_input)
            
        except Exception as e:
            logger.error(f"调用核心模块失败: {e}")
            context_data["error"] = str(e)
        
        return context_data
    
    def _update_stats(self, processing_time: float, success: bool):
        """更新处理统计信息"""
        self.stats["total_processed"] += 1
        
        if success:
            self.stats["successful_processed"] += 1
        else:
            self.stats["failed_processed"] += 1
        
        # 更新平均处理时间
        total_time = self.stats["average_processing_time"] * (self.stats["total_processed"] - 1)
        self.stats["average_processing_time"] = (total_time + processing_time) / self.stats["total_processed"]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_processed"] / self.stats["total_processed"] 
                if self.stats["total_processed"] > 0 else 0
            )
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        try:
            # 检查各个组件的健康状态
            health_status["components"]["input_parser"] = await self.input_parser.health_check()
            health_status["components"]["state_manager"] = await self.state_manager.health_check()
            health_status["components"]["decision_engine"] = await self.decision_engine.health_check()
            health_status["components"]["output_adapter"] = await self.output_adapter.health_check()
            health_status["components"]["langgraph_flow"] = await self.langgraph_flow.health_check()
            
            # 检查是否有组件不健康
            unhealthy_components = [
                name for name, status in health_status["components"].items()
                if status.get("status") != "healthy"
            ]
            
            if unhealthy_components:
                health_status["status"] = "degraded"
                health_status["unhealthy_components"] = unhealthy_components
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status

# 全局流程处理器实例
flow_processor = FlowProcessor()
