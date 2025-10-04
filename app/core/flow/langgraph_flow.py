"""
LangGraph流程控制器 (LangGraphFlow)
基于LangGraph实现智能对话流程控制和决策节点管理
"""

import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from app.core.management.logging_manager import log_operation_start, log_operation_success, log_operation_error, log_info

logger = logging.getLogger(__name__)

class NodeType(Enum):
    """节点类型枚举"""
    INPUT_PROCESSING = "input_processing"
    INTENT_ANALYSIS = "intent_analysis"
    CONTEXT_RETRIEVAL = "context_retrieval"
    RESPONSE_GENERATION = "response_generation"
    QUALITY_CHECK = "quality_check"
    OUTPUT_FORMATTING = "output_formatting"
    ERROR_HANDLING = "error_handling"

class FlowState(Enum):
    """流程状态枚举"""
    INITIALIZED = "initialized"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    RETRYING = "retrying"

@dataclass
class FlowNode:
    """流程节点"""
    node_id: str
    node_type: NodeType
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: Optional[Callable] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 30

@dataclass
class FlowExecution:
    """流程执行记录"""
    execution_id: str
    flow_name: str
    current_node: str
    state: FlowState
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error_info: Optional[Dict[str, Any]] = None
    start_time: datetime = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.utcnow()

class LangGraphFlow:
    """LangGraph流程控制器"""
    
    def __init__(self):
        # 流程定义
        self.flows = {
            "chat_flow": self._define_chat_flow(),
            "clarification_flow": self._define_clarification_flow(),
            "creative_flow": self._define_creative_flow(),
            "error_recovery_flow": self._define_error_recovery_flow()
        }
        
        # 节点处理器
        self.node_handlers = {
            NodeType.INPUT_PROCESSING: self._handle_input_processing,
            NodeType.INTENT_ANALYSIS: self._handle_intent_analysis,
            NodeType.CONTEXT_RETRIEVAL: self._handle_context_retrieval,
            NodeType.RESPONSE_GENERATION: self._handle_response_generation,
            NodeType.QUALITY_CHECK: self._handle_quality_check,
            NodeType.OUTPUT_FORMATTING: self._handle_output_formatting,
            NodeType.ERROR_HANDLING: self._handle_error_handling
        }
        
        # 执行记录
        self.executions: Dict[str, FlowExecution] = {}
        
        # 统计信息
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0,
            "node_execution_counts": {}
        }
    
    async def execute_flow(self, flow_name: str, input_data: Dict[str, Any], 
                          execution_id: Optional[str] = None) -> Dict[str, Any]:
        """
        执行指定流程
        
        Args:
            flow_name: 流程名称
            input_data: 输入数据
            execution_id: 执行ID（可选）
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        if execution_id is None:
            execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        log_operation_start("执行LangGraph流程", execution_id=execution_id, flow_name=flow_name)
        
        try:
            # 获取流程定义
            flow = self.flows.get(flow_name)
            if not flow:
                raise ValueError(f"未找到流程定义: {flow_name}")
            
            # 创建执行记录
            execution = FlowExecution(
                execution_id=execution_id,
                flow_name=flow_name,
                current_node=flow["start_node"],
                state=FlowState.INITIALIZED,
                input_data=input_data,
                output_data={}
            )
            
            self.executions[execution_id] = execution
            self.stats["total_executions"] += 1
            
            # 执行流程
            result = await self._execute_flow_nodes(execution, flow)
            
            # 更新执行状态
            execution.state = FlowState.COMPLETED
            execution.end_time = datetime.utcnow()
            execution.output_data = result
            
            self.stats["successful_executions"] += 1
            self._update_execution_time_stats(execution)
            
            log_operation_success("执行LangGraph流程", execution_id=execution_id, 
                                flow_name=flow_name, execution_time=execution.end_time - execution.start_time)
            
            return result
            
        except Exception as e:
            # 更新执行状态为错误
            if execution_id in self.executions:
                execution = self.executions[execution_id]
                execution.state = FlowState.ERROR
                execution.end_time = datetime.utcnow()
                execution.error_info = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            self.stats["failed_executions"] += 1
            
            log_operation_error("执行LangGraph流程", str(e), execution_id=execution_id, flow_name=flow_name)
            
            # 返回错误结果
            return {
                "success": False,
                "error": str(e),
                "execution_id": execution_id,
                "flow_name": flow_name
            }
    
    async def _execute_flow_nodes(self, execution: FlowExecution, flow: Dict[str, Any]) -> Dict[str, Any]:
        """执行流程节点"""
        current_node_id = execution.current_node
        node_data = {}
        
        while current_node_id and current_node_id != "end":
            # 获取当前节点
            node = flow["nodes"].get(current_node_id)
            if not node:
                raise ValueError(f"未找到节点: {current_node_id}")
            
            # 执行节点
            log_info(f"执行节点: {current_node_id}", execution_id=execution.execution_id)
            
            try:
                node_result = await self._execute_node(node, node_data, execution)
                node_data.update(node_result)
                
                # 更新节点执行计数
                self._update_node_execution_count(node.node_type.value)
                
                # 确定下一个节点
                current_node_id = await self._determine_next_node(node, node_result, flow)
                execution.current_node = current_node_id
                
            except Exception as e:
                logger.error(f"节点执行失败: {current_node_id}, 错误: {e}")
                
                # 尝试错误恢复
                error_recovery_result = await self._handle_node_error(node, e, execution)
                if error_recovery_result:
                    node_data.update(error_recovery_result)
                    current_node_id = await self._determine_next_node(node, error_recovery_result, flow)
                    execution.current_node = current_node_id
                else:
                    raise e
        
        return node_data
    
    async def _execute_node(self, node: FlowNode, node_data: Dict[str, Any], 
                          execution: FlowExecution) -> Dict[str, Any]:
        """执行单个节点"""
        execution.state = FlowState.PROCESSING
        
        # 获取节点处理器
        handler = self.node_handlers.get(node.node_type)
        if not handler:
            raise ValueError(f"未找到节点处理器: {node.node_type}")
        
        # 重试机制
        last_error = None
        for attempt in range(node.max_retries + 1):
            try:
                result = await handler(node, node_data, execution)
                node.retry_count = attempt
                return result
                
            except Exception as e:
                last_error = e
                node.retry_count = attempt
                
                if attempt < node.max_retries:
                    log_info(f"节点执行失败，重试 {attempt + 1}/{node.max_retries}", 
                           execution_id=execution.execution_id, node_id=node.node_id)
                    await asyncio.sleep(1)  # 重试前等待1秒
                else:
                    raise e
        
        raise last_error
    
    async def _determine_next_node(self, current_node: FlowNode, node_result: Dict[str, Any], 
                                 flow: Dict[str, Any]) -> Optional[str]:
        """确定下一个节点"""
        # 获取当前节点的连接信息
        connections = flow["connections"].get(current_node.node_id, {})
        
        # 根据节点结果和连接规则确定下一个节点
        if "default" in connections:
            return connections["default"]
        
        # 可以根据node_result的内容进行条件判断
        if "error" in node_result:
            return connections.get("error", "error_handling")
        
        if "success" in node_result and node_result["success"]:
            return connections.get("success", "end")
        
        return connections.get("next", "end")
    
    async def _handle_node_error(self, node: FlowNode, error: Exception, 
                               execution: FlowExecution) -> Optional[Dict[str, Any]]:
        """处理节点错误"""
        log_info(f"处理节点错误: {node.node_id}", execution_id=execution.execution_id, error=str(error))
        
        # 根据错误类型决定是否重试
        if isinstance(error, (TimeoutError, ConnectionError)):
            # 网络相关错误，可以重试
            return None
        
        elif isinstance(error, ValueError):
            # 参数错误，通常不需要重试
            return {"error": str(error), "retry": False}
        
        else:
            # 其他错误，尝试错误恢复流程
            try:
                error_recovery_result = await self.execute_flow("error_recovery_flow", {
                    "error": str(error),
                    "node_id": node.node_id,
                    "execution_id": execution.execution_id
                })
                
                return error_recovery_result
                
            except Exception as recovery_error:
                logger.error(f"错误恢复失败: {recovery_error}")
                return {"error": str(error), "recovery_failed": True}
    
    # 节点处理器实现
    async def _handle_input_processing(self, node: FlowNode, node_data: Dict[str, Any], 
                                     execution: FlowExecution) -> Dict[str, Any]:
        """处理输入处理节点"""
        input_data = execution.input_data
        
        # 验证输入数据
        if not input_data.get("user_input"):
            raise ValueError("缺少用户输入数据")
        
        # 预处理输入
        processed_input = {
            "raw_input": input_data["user_input"],
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": input_data.get("user_id", 0),
            "conversation_id": input_data.get("conversation_id", "")
        }
        
        return {
            "processed_input": processed_input,
            "success": True
        }
    
    async def _handle_intent_analysis(self, node: FlowNode, node_data: Dict[str, Any], 
                                    execution: FlowExecution) -> Dict[str, Any]:
        """处理意图分析节点"""
        processed_input = node_data.get("processed_input", {})
        raw_input = processed_input.get("raw_input", "")
        
        # 简单的意图分析（实际应该调用专门的意图识别服务）
        intent = "unknown"
        confidence = 0.5
        
        if any(word in raw_input.lower() for word in ["你好", "hello", "hi"]):
            intent = "greeting"
            confidence = 0.9
        elif "？" in raw_input or "?" in raw_input:
            intent = "question"
            confidence = 0.8
        elif any(word in raw_input.lower() for word in ["再见", "bye", "goodbye"]):
            intent = "farewell"
            confidence = 0.9
        
        return {
            "intent": intent,
            "confidence": confidence,
            "success": True
        }
    
    async def _handle_context_retrieval(self, node: FlowNode, node_data: Dict[str, Any], 
                                      execution: FlowExecution) -> Dict[str, Any]:
        """处理上下文检索节点"""
        processed_input = node_data.get("processed_input", {})
        
        # 检索相关上下文（实际应该从数据库或向量数据库检索）
        context = {
            "conversation_history": [],
            "user_profile": {},
            "relevant_knowledge": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "context": context,
            "success": True
        }
    
    async def _handle_response_generation(self, node: FlowNode, node_data: Dict[str, Any], 
                                        execution: FlowExecution) -> Dict[str, Any]:
        """处理响应生成节点"""
        intent = node_data.get("intent", "unknown")
        context = node_data.get("context", {})
        processed_input = node_data.get("processed_input", {})
        
        # 基于意图和上下文生成响应
        response_templates = {
            "greeting": "你好！很高兴见到你！",
            "question": "这是一个很好的问题，让我来为你解答。",
            "farewell": "再见！期待下次与你聊天！",
            "unknown": "我理解你的意思，让我想想如何回复。"
        }
        
        response = response_templates.get(intent, response_templates["unknown"])
        
        return {
            "response": response,
            "response_type": "text",
            "success": True
        }
    
    async def _handle_quality_check(self, node: FlowNode, node_data: Dict[str, Any], 
                                  execution: FlowExecution) -> Dict[str, Any]:
        """处理质量检查节点"""
        response = node_data.get("response", "")
        
        # 简单的质量检查
        quality_score = 0.5
        
        if len(response) > 10:  # 长度检查
            quality_score += 0.2
        
        if not any(char in response for char in ["错误", "error", "失败"]):  # 内容检查
            quality_score += 0.2
        
        if quality_score >= 0.6:  # 质量阈值
            return {
                "quality_score": quality_score,
                "quality_check_passed": True,
                "success": True
            }
        else:
            return {
                "quality_score": quality_score,
                "quality_check_passed": False,
                "success": False,
                "error": "响应质量不达标"
            }
    
    async def _handle_output_formatting(self, node: FlowNode, node_data: Dict[str, Any], 
                                      execution: FlowExecution) -> Dict[str, Any]:
        """处理输出格式化节点"""
        response = node_data.get("response", "")
        quality_score = node_data.get("quality_score", 0.5)
        
        # 格式化输出
        formatted_output = {
            "content": response,
            "metadata": {
                "quality_score": quality_score,
                "generation_time": datetime.utcnow().isoformat(),
                "execution_id": execution.execution_id
            },
            "success": True
        }
        
        return formatted_output
    
    async def _handle_error_handling(self, node: FlowNode, node_data: Dict[str, Any], 
                                   execution: FlowExecution) -> Dict[str, Any]:
        """处理错误处理节点"""
        error_info = execution.error_info or {}
        
        # 生成错误响应
        error_response = {
            "content": "抱歉，处理您的请求时遇到了问题。请稍后再试。",
            "error": True,
            "error_info": error_info,
            "success": False
        }
        
        return error_response
    
    def _update_node_execution_count(self, node_type: str):
        """更新节点执行计数"""
        if node_type not in self.stats["node_execution_counts"]:
            self.stats["node_execution_counts"][node_type] = 0
        self.stats["node_execution_counts"][node_type] += 1
    
    def _update_execution_time_stats(self, execution: FlowExecution):
        """更新执行时间统计"""
        if execution.end_time and execution.start_time:
            execution_time = (execution.end_time - execution.start_time).total_seconds()
            
            total_time = self.stats["average_execution_time"] * (self.stats["total_executions"] - 1)
            self.stats["average_execution_time"] = (total_time + execution_time) / self.stats["total_executions"]
    
    # 流程定义
    def _define_chat_flow(self) -> Dict[str, Any]:
        """定义聊天流程"""
        return {
            "name": "chat_flow",
            "description": "标准聊天对话流程",
            "start_node": "input_processing",
            "nodes": {
                "input_processing": FlowNode(
                    node_id="input_processing",
                    node_type=NodeType.INPUT_PROCESSING,
                    name="输入处理",
                    description="处理和验证用户输入",
                    input_schema={"user_input": "string"},
                    output_schema={"processed_input": "object"}
                ),
                "intent_analysis": FlowNode(
                    node_id="intent_analysis",
                    node_type=NodeType.INTENT_ANALYSIS,
                    name="意图分析",
                    description="分析用户意图",
                    input_schema={"processed_input": "object"},
                    output_schema={"intent": "string", "confidence": "float"}
                ),
                "context_retrieval": FlowNode(
                    node_id="context_retrieval",
                    node_type=NodeType.CONTEXT_RETRIEVAL,
                    name="上下文检索",
                    description="检索相关上下文信息",
                    input_schema={"processed_input": "object"},
                    output_schema={"context": "object"}
                ),
                "response_generation": FlowNode(
                    node_id="response_generation",
                    node_type=NodeType.RESPONSE_GENERATION,
                    name="响应生成",
                    description="生成AI响应",
                    input_schema={"intent": "string", "context": "object"},
                    output_schema={"response": "string"}
                ),
                "quality_check": FlowNode(
                    node_id="quality_check",
                    node_type=NodeType.QUALITY_CHECK,
                    name="质量检查",
                    description="检查响应质量",
                    input_schema={"response": "string"},
                    output_schema={"quality_score": "float", "quality_check_passed": "boolean"}
                ),
                "output_formatting": FlowNode(
                    node_id="output_formatting",
                    node_type=NodeType.OUTPUT_FORMATTING,
                    name="输出格式化",
                    description="格式化最终输出",
                    input_schema={"response": "string", "quality_score": "float"},
                    output_schema={"formatted_output": "object"}
                )
            },
            "connections": {
                "input_processing": {"default": "intent_analysis"},
                "intent_analysis": {"default": "context_retrieval"},
                "context_retrieval": {"default": "response_generation"},
                "response_generation": {"default": "quality_check"},
                "quality_check": {
                    "success": "output_formatting",
                    "error": "error_handling"
                },
                "output_formatting": {"default": "end"}
            }
        }
    
    def _define_clarification_flow(self) -> Dict[str, Any]:
        """定义澄清流程"""
        return {
            "name": "clarification_flow",
            "description": "用户输入澄清流程",
            "start_node": "input_processing",
            "nodes": {
                "input_processing": FlowNode(
                    node_id="input_processing",
                    node_type=NodeType.INPUT_PROCESSING,
                    name="输入处理",
                    description="处理澄清请求",
                    input_schema={"user_input": "string"},
                    output_schema={"processed_input": "object"}
                ),
                "response_generation": FlowNode(
                    node_id="response_generation",
                    node_type=NodeType.RESPONSE_GENERATION,
                    name="澄清响应生成",
                    description="生成澄清问题",
                    input_schema={"processed_input": "object"},
                    output_schema={"response": "string"}
                )
            },
            "connections": {
                "input_processing": {"default": "response_generation"},
                "response_generation": {"default": "end"}
            }
        }
    
    def _define_creative_flow(self) -> Dict[str, Any]:
        """定义创意流程"""
        return {
            "name": "creative_flow",
            "description": "创意内容生成流程",
            "start_node": "input_processing",
            "nodes": {
                "input_processing": FlowNode(
                    node_id="input_processing",
                    node_type=NodeType.INPUT_PROCESSING,
                    name="输入处理",
                    description="处理创意请求",
                    input_schema={"user_input": "string"},
                    output_schema={"processed_input": "object"}
                ),
                "response_generation": FlowNode(
                    node_id="response_generation",
                    node_type=NodeType.RESPONSE_GENERATION,
                    name="创意响应生成",
                    description="生成创意内容",
                    input_schema={"processed_input": "object"},
                    output_schema={"response": "string"}
                )
            },
            "connections": {
                "input_processing": {"default": "response_generation"},
                "response_generation": {"default": "end"}
            }
        }
    
    def _define_error_recovery_flow(self) -> Dict[str, Any]:
        """定义错误恢复流程"""
        return {
            "name": "error_recovery_flow",
            "description": "错误恢复处理流程",
            "start_node": "error_handling",
            "nodes": {
                "error_handling": FlowNode(
                    node_id="error_handling",
                    node_type=NodeType.ERROR_HANDLING,
                    name="错误处理",
                    description="处理错误情况",
                    input_schema={"error": "string"},
                    output_schema={"error_response": "object"}
                )
            },
            "connections": {
                "error_handling": {"default": "end"}
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        
        # 计算成功率
        if stats["total_executions"] > 0:
            stats["success_rate"] = stats["successful_executions"] / stats["total_executions"]
        else:
            stats["success_rate"] = 0.0
        
        # 添加活跃执行数量
        stats["active_executions"] = len([
            exec for exec in self.executions.values() 
            if exec.state == FlowState.PROCESSING
        ])
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试流程执行
            test_result = await self.execute_flow("chat_flow", {
                "user_input": "你好",
                "user_id": 0,
                "conversation_id": "test"
            })
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "flows_count": len(self.flows),
                "active_executions": len([
                    exec for exec in self.executions.values() 
                    if exec.state == FlowState.PROCESSING
                ]),
                "test_result": test_result.get("success", False),
                "stats": self.get_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
