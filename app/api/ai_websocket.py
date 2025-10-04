"""
AI对话WebSocket API端点
提供用户与AI角色的实时对话功能
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
import json
import logging
from typing import Optional

from app.websocket.ai_manager import ai_manager
from app.websocket.ai_handler import AIMessageHandler
from app.websocket.enhanced_ai_handler import enhanced_ai_handler
from app.core.utils.auth import verify_token
from app.core.management.logging_manager import log_info, log_operation_error
from app.core.management.response_handler import success_response

router = APIRouter()
logger = logging.getLogger(__name__)

# 用于WebSocket认证的token验证
security = HTTPBearer()

@router.websocket("/ai-chat/{user_id}")
async def ai_chat_websocket_endpoint(
    websocket: WebSocket, 
    user_id: int,
    token: Optional[str] = Query(None, description="认证token"),
    use_enhanced: Optional[bool] = Query(False, description="是否使用增强版架构")
):
    """
    AI对话WebSocket连接端点（兼容增强版架构）
    
    参数:
    - user_id: 用户ID
    - token: 认证token（可选，用于身份验证）
    - use_enhanced: 是否使用增强版架构（可选，默认为False）
    
    基础消息类型:
    - start_ai_session: 开始AI会话
    - end_ai_session: 结束AI会话
    - chat_message: 发送聊天消息
    - get_conversation_history: 获取对话历史
    - get_ai_characters: 获取AI角色列表
    - ping: 心跳检测
    
    增强版消息类型（仅在use_enhanced=true时支持）:
    - get_user_state: 获取用户状态
    - update_user_preferences: 更新用户偏好
    - switch_ai_character: 切换AI角色
    
    使用示例:
    - 基础架构: ws://localhost:8000/ai-chat/123
    - 增强版架构: ws://localhost:8000/ai-chat/123?use_enhanced=true
    """
    
    # 验证token并获取实际用户ID
    actual_user_id = user_id
    if token:
        try:
            payload = verify_token(token)
            if payload:
                actual_user_id = int(payload.get("sub"))
                log_info(f"Token验证成功，用户ID: {actual_user_id}")
            else:
                await websocket.close(code=1008, reason="Token验证失败")
                return
        except Exception as e:
            log_operation_error("Token验证", str(e), user_id=user_id)
            await websocket.close(code=1008, reason="Token验证异常")
            return
    
    # 建立连接
    success = await ai_manager.connect(websocket, actual_user_id)
    if not success:
        await websocket.close(code=1008, reason="连接失败")
        return
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "无效的JSON格式"
                }))
                continue
            
            # 根据use_enhanced参数选择处理器
            if use_enhanced:
                # 使用增强版处理器
                result = await enhanced_ai_handler.handle_message(actual_user_id, message_data)
            else:
                # 使用原有处理器
                result = await AIMessageHandler.handle_message(actual_user_id, message_data)
            
            # 发送处理结果
            await websocket.send_text(json.dumps({
                "type": "response",
                "original_type": message_data.get("type"),
                "result": result
            }))
    
    except WebSocketDisconnect:
        await ai_manager.disconnect(actual_user_id)
        architecture_type = "增强版" if use_enhanced else "基础版"
        log_info(f"用户断开AI对话连接 ({architecture_type}架构)", user_id=actual_user_id)
    except Exception as e:
        architecture_type = "增强版" if use_enhanced else "基础版"
        log_operation_error(f"AI对话WebSocket ({architecture_type}架构)", str(e), user_id=actual_user_id)
        await ai_manager.disconnect(actual_user_id)

@router.get("/ai-chat/stats")
async def get_ai_chat_stats():
    """获取AI对话统计信息（包含基础版和增强版架构）"""
    try:
        # 获取基础版统计信息
        basic_stats = ai_manager.get_stats()
        
        # 获取增强版统计信息
        enhanced_stats = await enhanced_ai_handler.get_flow_processor_stats()
        
        # 合并统计信息
        combined_stats = {
            "basic_architecture": {
                "ai_manager_stats": basic_stats,
                "description": "基础版AI对话架构"
            },
            "enhanced_architecture": {
                "flow_processor_stats": enhanced_stats,
                "description": "增强版AI对话架构（六维状态管理 + 智能决策）"
            },
            "architecture_features": {
                "basic": ["WebSocket连接管理", "基础消息处理", "AI角色对话"],
                "enhanced": ["六维状态管理", "智能决策引擎", "统一流程处理", "LangGraph流程控制", "输入解析", "输出适配"]
            }
        }
        
        return success_response(
            data=combined_stats,
            message="获取AI对话统计信息成功"
        )
    except Exception as e:
        log_operation_error("获取AI对话统计信息", str(e))
        raise HTTPException(status_code=500, detail="获取统计信息失败")

@router.get("/ai-chat/online")
async def get_ai_chat_online_users():
    """获取AI对话在线用户"""
    online_users = ai_manager.get_online_users()
    return success_response(
        data={
            "online_users": online_users,
            "count": len(online_users)
        },
        message="获取AI对话在线用户成功"
    )

@router.get("/ai-chat/user/{user_id}/status")
async def get_user_ai_chat_status(user_id: int):
    """获取指定用户的AI对话状态"""
    is_online = ai_manager.is_user_online(user_id)
    ai_session = ai_manager.get_user_ai_session(user_id)
    
    return success_response(
        data={
            "user_id": user_id,
            "is_online": is_online,
            "ai_session": ai_session,
            "has_active_session": ai_session is not None
        },
        message="获取用户AI对话状态成功"
    )

@router.post("/ai-chat/user/{user_id}/disconnect")
async def disconnect_user_ai_chat(user_id: int):
    """强制断开指定用户的AI对话连接"""
    try:
        await ai_manager.disconnect(user_id)
        return success_response(
            data={"user_id": user_id},
            message="用户AI对话连接已断开"
        )
    except Exception as e:
        log_operation_error("断开用户AI对话连接", str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail="断开连接失败")

@router.websocket("/ai-chat-enhanced/{user_id}")
async def ai_chat_enhanced_websocket_endpoint(
    websocket: WebSocket, 
    user_id: int,
    token: Optional[str] = Query(None, description="认证token")
):
    """
    增强版AI对话WebSocket连接端点
    使用统一流程处理模块，支持六维状态管理和智能决策
    
    参数:
    - user_id: 用户ID
    - token: 认证token（可选，用于身份验证）
    
    连接后可以发送以下类型的消息:
    - start_ai_session: 开始AI会话
    - end_ai_session: 结束AI会话
    - chat_message: 发送聊天消息
    - get_conversation_history: 获取对话历史
    - get_ai_characters: 获取AI角色列表
    - get_user_state: 获取用户状态
    - update_user_preferences: 更新用户偏好
    - switch_ai_character: 切换AI角色
    - ping: 心跳检测
    """
    
    # 建立连接
    success = await ai_manager.connect(websocket, user_id)
    if not success:
        await websocket.close(code=1008, reason="连接失败")
        return
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "无效的JSON格式"
                }))
                continue
            
            # 使用增强版处理器处理消息
            result = await enhanced_ai_handler.handle_message(user_id, message_data)
            
            # 发送处理结果
            await websocket.send_text(json.dumps({
                "type": "response",
                "original_type": message_data.get("type"),
                "result": result
            }))
    
    except WebSocketDisconnect:
        await ai_manager.disconnect(user_id)
        log_info(f"用户断开增强版AI对话连接", user_id=user_id)
    except Exception as e:
        log_operation_error("增强版AI对话WebSocket", str(e), user_id=user_id)
        await ai_manager.disconnect(user_id)

@router.get("/ai-chat-enhanced/stats")
async def get_enhanced_ai_chat_stats():
    """获取增强版AI对话统计信息"""
    try:
        flow_stats = await enhanced_ai_handler.get_flow_processor_stats()
        ai_stats = ai_manager.get_stats()
        
        return success_response(
            data={
                "ai_manager_stats": ai_stats,
                "flow_processor_stats": flow_stats,
                "enhanced_features": {
                    "six_dimension_state": True,
                    "intelligent_decision": True,
                    "unified_flow_processing": True,
                    "langgraph_flow_control": True
                }
            },
            message="获取增强版AI对话统计信息成功"
        )
    except Exception as e:
        log_operation_error("获取增强版AI对话统计信息", str(e))
        raise HTTPException(status_code=500, detail="获取统计信息失败")

@router.get("/ai-chat/health")
async def ai_chat_health_check():
    """AI对话健康检查（包含基础版和增强版架构）"""
    try:
        # 基础版健康检查
        basic_health = {
            "status": "healthy",
            "timestamp": "2024-12-19T10:00:00Z",
            "components": {
                "ai_manager": {"status": "healthy"},
                "websocket_connections": {"status": "healthy"}
            }
        }
        
        # 增强版健康检查
        enhanced_health = await enhanced_ai_handler.health_check()
        
        # 合并健康状态
        combined_health = {
            "overall_status": "healthy",
            "timestamp": "2024-12-19T10:00:00Z",
            "basic_architecture": {
                "status": basic_health["status"],
                "components": basic_health["components"]
            },
            "enhanced_architecture": enhanced_health,
            "recommendations": {
                "use_enhanced": "建议使用增强版架构以获得更好的AI对话体验",
                "features": "增强版支持六维状态管理、智能决策和统一流程处理"
            }
        }
        
        return success_response(
            data=combined_health,
            message="AI对话健康检查完成"
        )
    except Exception as e:
        log_operation_error("AI对话健康检查", str(e))
        raise HTTPException(status_code=500, detail="健康检查失败")

@router.get("/ai-chat/architecture-info")
async def get_architecture_info():
    """获取架构信息和使用指南"""
    try:
        architecture_info = {
            "websocket_endpoints": {
                "basic": {
                    "url": "/ai-chat/{user_id}",
                    "description": "基础版AI对话WebSocket端点",
                    "features": ["基础消息处理", "AI角色对话", "WebSocket连接管理"]
                },
                "enhanced": {
                    "url": "/ai-chat/{user_id}?use_enhanced=true",
                    "description": "增强版AI对话WebSocket端点",
                    "features": ["六维状态管理", "智能决策引擎", "统一流程处理", "LangGraph流程控制"]
                }
            },
            "message_types": {
                "basic": [
                    "start_ai_session",
                    "end_ai_session", 
                    "chat_message",
                    "get_conversation_history",
                    "get_ai_characters",
                    "ping"
                ],
                "enhanced": [
                    "start_ai_session",
                    "end_ai_session",
                    "chat_message", 
                    "get_conversation_history",
                    "get_ai_characters",
                    "ping",
                    "get_user_state",
                    "update_user_preferences",
                    "switch_ai_character"
                ]
            },
            "usage_examples": {
                "javascript_basic": """
const ws = new WebSocket('ws://localhost:8000/ai-chat/123');
ws.send(JSON.stringify({
    type: 'chat_message',
    content: '你好',
    conversation_id: 'conv_001'
}));""",
                "javascript_enhanced": """
const ws = new WebSocket('ws://localhost:8000/ai-chat/123?use_enhanced=true');
ws.send(JSON.stringify({
    type: 'get_user_state',
    conversation_id: 'conv_001'
}));"""
            },
            "migration_guide": {
                "from_basic_to_enhanced": [
                    "1. 将WebSocket连接URL添加 ?use_enhanced=true 参数",
                    "2. 可以使用新增的消息类型如 get_user_state",
                    "3. 享受六维状态管理和智能决策功能",
                    "4. 原有消息类型完全兼容，无需修改现有代码"
                ]
            }
        }
        
        return success_response(
            data=architecture_info,
            message="获取架构信息成功"
        )
    except Exception as e:
        log_operation_error("获取架构信息", str(e))
        raise HTTPException(status_code=500, detail="获取架构信息失败")

@router.get("/ai-chat-enhanced/health")
async def enhanced_ai_chat_health_check():
    """增强版AI对话健康检查"""
    try:
        health_status = await enhanced_ai_handler.health_check()
        return success_response(
            data=health_status,
            message="增强版AI对话健康检查完成"
        )
    except Exception as e:
        log_operation_error("增强版AI对话健康检查", str(e))
        raise HTTPException(status_code=500, detail="健康检查失败")


