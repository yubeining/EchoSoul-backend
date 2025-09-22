"""
API Package - EchoSoul AI Platform
统一管理所有API路由和端点
"""

from fastapi import APIRouter
from app.api import (
    database, stats, auth, security, user_search, 
    chat, ai_character, llm_chat, websocket, ai_websocket
)
from config.settings import settings

# 创建主API路由器
api_router = APIRouter()

# 注册核心API路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(database.router, prefix="/db", tags=["数据库"])
api_router.include_router(user_search.router, prefix="/users", tags=["用户搜索"])
api_router.include_router(chat.router, prefix="/chat", tags=["聊天"])
api_router.include_router(ai_character.router, prefix="/ai", tags=["AI角色"])
api_router.include_router(llm_chat.router, prefix="/llm", tags=["大模型"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
api_router.include_router(ai_websocket.router, prefix="/ws", tags=["AI WebSocket"])
api_router.include_router(stats.router, prefix="/stats", tags=["统计"])
api_router.include_router(security.router, prefix="/security", tags=["安全"])

# 注册存储API路由（可选）
try:
    from app.api import storage
    api_router.include_router(storage.router, prefix="/storage", tags=["存储"])
except ImportError:
    pass

# API健康检查端点
@api_router.get("/health")
async def api_health_check():
    """API健康检查端点"""
    return {
        "status": "healthy",
        "message": "EchoSoul AI Platform API is running",
        "version": settings.APP_VERSION,
        "cors_origins": settings.CORS_ORIGINS
    }

__all__ = ["api_router"]
