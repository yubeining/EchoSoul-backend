"""
EchoSoul AI Platform Performance API
性能监控API端点
"""

from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.core.performance_monitor import performance_monitor
from app.core.background_tasks import background_task_manager
from app.models.user_models import AuthUser
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stats", summary="获取性能统计")
async def get_performance_stats(current_user: AuthUser = Depends(get_current_user)):
    """获取系统性能统计"""
    try:
        stats = performance_monitor.get_performance_summary()
        return {
            "code": 1,
            "msg": "获取性能统计成功",
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取性能统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取性能统计失败")

@router.get("/requests", summary="获取请求统计")
async def get_request_stats(
    endpoint: str = None,
    minutes: int = 60,
    current_user: AuthUser = Depends(get_current_user)
):
    """获取请求统计信息"""
    try:
        stats = performance_monitor.get_request_stats(endpoint, minutes)
        return {
            "code": 1,
            "msg": "获取请求统计成功",
            "data": {
                "endpoint": endpoint,
                "time_range_minutes": minutes,
                "stats": stats
            }
        }
    except Exception as e:
        logger.error(f"获取请求统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取请求统计失败")

@router.get("/system", summary="获取系统资源统计")
async def get_system_stats(current_user: AuthUser = Depends(get_current_user)):
    """获取系统资源使用情况"""
    try:
        stats = performance_monitor.get_system_stats()
        return {
            "code": 1,
            "msg": "获取系统统计成功",
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统统计失败")

@router.get("/background-tasks", summary="获取后台任务状态")
async def get_background_task_status(current_user: AuthUser = Depends(get_current_user)):
    """获取后台任务运行状态"""
    try:
        task_status = background_task_manager.get_task_status()
        return {
            "code": 1,
            "msg": "获取后台任务状态成功",
            "data": {
                "tasks": task_status,
                "manager_running": background_task_manager.running
            }
        }
    except Exception as e:
        logger.error(f"获取后台任务状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取后台任务状态失败")

@router.post("/cleanup", summary="清理性能数据")
async def cleanup_performance_data(
    hours: int = 24,
    current_user: AuthUser = Depends(get_current_user)
):
    """清理旧的性能监控数据"""
    try:
        performance_monitor.cleanup_old_metrics(hours)
        return {
            "code": 1,
            "msg": f"已清理{hours}小时前的性能数据",
            "data": {"cleaned_hours": hours}
        }
    except Exception as e:
        logger.error(f"清理性能数据失败: {e}")
        raise HTTPException(status_code=500, detail="清理性能数据失败")
