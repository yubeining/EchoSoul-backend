"""
API Package - EchoSoul AI Platform
统一管理所有API路由和端点
"""

from fastapi import APIRouter
from app.api import database, stats, auth, security, user_search
from config.settings import settings

# 创建主API路由器
api_router = APIRouter()

# 注册核心API路由
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(database.router, prefix="/db", tags=["database"])
api_router.include_router(user_search.router, prefix="/users", tags=["user-search"])
# ai_requests 和 system_logs 路由已移除，因为项目中没有实际使用这些表
api_router.include_router(stats.router, prefix="/stats", tags=["statistics"])
api_router.include_router(security.router, prefix="/security", tags=["security"])

# 注册存储API路由（可选）
try:
    from app.api import storage
    api_router.include_router(storage.router, prefix="/storage", tags=["storage"])
    print("✅ Storage API router included")
except Exception as e:
    print(f"⚠️ Failed to include storage router: {e}")

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
