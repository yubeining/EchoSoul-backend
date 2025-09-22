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
from app.core.auth import get_current_user
from app.models.user_models import AuthUser

router = APIRouter()
logger = logging.getLogger(__name__)

# 用于WebSocket认证的token验证
security = HTTPBearer()

@router.websocket("/ai-chat/{user_id}")
async def ai_chat_websocket_endpoint(
    websocket: WebSocket, 
    user_id: int,
    token: Optional[str] = Query(None, description="认证token")
):
    """
    AI对话WebSocket连接端点
    
    参数:
    - user_id: 用户ID
    - token: 认证token（可选，用于身份验证）
    
    连接后可以发送以下类型的消息:
    - start_ai_session: 开始AI会话
    - end_ai_session: 结束AI会话
    - chat_message: 发送聊天消息
    - get_conversation_history: 获取对话历史
    - get_ai_characters: 获取AI角色列表
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
            
            # 处理消息
            result = await AIMessageHandler.handle_message(user_id, message_data)
            
            # 发送处理结果
            await websocket.send_text(json.dumps({
                "type": "response",
                "original_type": message_data.get("type"),
                "result": result
            }))
    
    except WebSocketDisconnect:
        await ai_manager.disconnect(user_id)
        logger.info(f"用户 {user_id} 断开AI对话连接")
    except Exception as e:
        logger.error(f"AI对话WebSocket错误: {e}")
        await ai_manager.disconnect(user_id)

@router.get("/ai-chat/stats")
async def get_ai_chat_stats():
    """获取AI对话统计信息"""
    return {
        "code": 1,
        "msg": "获取AI对话统计信息成功",
        "data": ai_manager.get_stats()
    }

@router.get("/ai-chat/online")
async def get_ai_chat_online_users():
    """获取AI对话在线用户"""
    return {
        "code": 1,
        "msg": "获取AI对话在线用户成功",
        "data": {
            "online_users": ai_manager.get_online_users(),
            "count": len(ai_manager.get_online_users())
        }
    }

@router.get("/ai-chat/user/{user_id}/status")
async def get_user_ai_chat_status(user_id: int):
    """获取指定用户的AI对话状态"""
    is_online = ai_manager.is_user_online(user_id)
    ai_session = ai_manager.get_user_ai_session(user_id)
    
    return {
        "code": 1,
        "msg": "获取用户AI对话状态成功",
        "data": {
            "user_id": user_id,
            "is_online": is_online,
            "ai_session": ai_session,
            "has_active_session": ai_session is not None
        }
    }

@router.post("/ai-chat/user/{user_id}/disconnect")
async def disconnect_user_ai_chat(user_id: int):
    """强制断开指定用户的AI对话连接"""
    try:
        await ai_manager.disconnect(user_id)
        return {
            "code": 1,
            "msg": "用户AI对话连接已断开",
            "data": {"user_id": user_id}
        }
    except Exception as e:
        logger.error(f"断开用户AI对话连接失败: {e}")
        raise HTTPException(status_code=500, detail="断开连接失败")

