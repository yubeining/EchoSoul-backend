"""
WebSocket API端点
提供双人会话的实时通信功能
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.websocket.simple_manager import simple_manager
from app.websocket.simple_handler import SimpleMessageHandler
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket连接端点
    
    参数:
    - user_id: 用户ID
    
    连接后可以发送以下类型的消息:
    - chat_message: 聊天消息
    - typing: 输入状态
    - ping: 心跳检测
    - get_online_status: 获取在线状态
    """
    
    # 建立连接
    success = await simple_manager.connect(websocket, user_id)
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
            result = await SimpleMessageHandler.handle_message(user_id, message_data)
            
            # 发送处理结果
            await websocket.send_text(json.dumps({
                "type": "response",
                "original_type": message_data.get("type"),
                "result": result
            }))
    
    except WebSocketDisconnect:
        simple_manager.disconnect(user_id)
        logger.info(f"用户 {user_id} 断开连接")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        simple_manager.disconnect(user_id)

@router.get("/stats")
async def get_websocket_stats():
    """获取WebSocket统计信息"""
    return {
        "code": 1,
        "msg": "获取统计信息成功",
        "data": simple_manager.get_stats()
    }

@router.get("/online")
async def get_online_users():
    """获取在线用户"""
    return {
        "code": 1,
        "msg": "获取在线用户成功",
        "data": {
            "online_users": simple_manager.get_online_users(),
            "count": len(simple_manager.get_online_users())
        }
    }

@router.get("/user/{user_id}/status")
async def get_user_status(user_id: int):
    """获取指定用户的在线状态"""
    is_online = simple_manager.is_user_online(user_id)
    other_user_id = simple_manager.get_other_user_id(user_id)
    
    return {
        "code": 1,
        "msg": "获取用户状态成功",
        "data": {
            "user_id": user_id,
            "is_online": is_online,
            "other_user_id": other_user_id,
            "other_user_online": other_user_id is not None
        }
    }
