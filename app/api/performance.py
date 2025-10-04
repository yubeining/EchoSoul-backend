"""
性能监控API端点
提供系统性能监控和统计信息
"""

from fastapi import APIRouter, Depends
from app.core.monitoring.performance_monitor import performance_monitor
from app.core.utils.cache_manager import cache_stats
from app.core.management.response_handler import success_response
from app.core.utils.auth import get_current_user
from app.models.user_models import AuthUser

router = APIRouter()

@router.get("/performance/stats")
async def get_performance_stats(current_user: AuthUser = Depends(get_current_user)):
    """获取性能统计信息"""
    stats = performance_monitor.get_performance_summary()
    return success_response(
        data=stats,
        message="获取性能统计信息成功"
    )

@router.get("/performance/requests")
async def get_request_stats(current_user: AuthUser = Depends(get_current_user)):
    """获取请求统计信息"""
    stats = performance_monitor.get_request_stats()
    return success_response(
        data=stats,
        message="获取请求统计信息成功"
    )

@router.get("/performance/system")
async def get_system_stats(current_user: AuthUser = Depends(get_current_user)):
    """获取系统统计信息"""
    stats = performance_monitor.get_system_stats()
    return success_response(
        data=stats,
        message="获取系统统计信息成功"
    )

@router.get("/performance/cache")
async def get_cache_stats(current_user: AuthUser = Depends(get_current_user)):
    """获取缓存统计信息"""
    stats = cache_stats()
    return success_response(
        data=stats,
        message="获取缓存统计信息成功"
    )

@router.post("/performance/cleanup")
async def cleanup_performance_data(current_user: AuthUser = Depends(get_current_user)):
    """清理性能数据"""
    performance_monitor.cleanup_old_metrics()
    return success_response(
        message="性能数据清理完成"
    )