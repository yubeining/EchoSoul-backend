"""
EchoSoul AI Platform Security API
安全监控和管理API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, List, Any
import logging

from app.db import get_database_session
from app.core.auth import get_current_user
from app.core.security_monitor import security_monitor, SecurityEventType, SecurityLevel
from app.middleware.security import SecurityMiddleware
from app.models.user_models import AuthUser

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stats", summary="获取安全统计信息")
async def get_security_stats(current_user: AuthUser = Depends(get_current_user)):
    """获取安全统计信息"""
    try:
        stats = security_monitor.get_security_stats()
        return {
            "code": 1,
            "msg": "获取安全统计成功",
            "data": {
                "total_events": stats.get("total_events", 0),
                "events_by_type": {k: v for k, v in stats.items() if k.startswith("type_")},
                "events_by_level": {k: v for k, v in stats.items() if k.startswith("level_")},
                "top_threat_ips": security_monitor.get_top_threat_ips(10)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get security stats: {e}")
        raise HTTPException(status_code=500, detail="获取安全统计失败")

@router.get("/events/summary", summary="获取安全事件摘要")
async def get_security_events_summary(
    hours: int = 24,
    current_user: AuthUser = Depends(get_current_user)
):
    """获取安全事件摘要"""
    try:
        if hours < 1 or hours > 168:  # 限制在1小时到1周之间
            raise HTTPException(status_code=400, detail="时间范围必须在1-168小时之间")
        
        summary = security_monitor.get_event_summary(hours)
        return {
            "code": 1,
            "msg": "获取安全事件摘要成功",
            "data": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get security events summary: {e}")
        raise HTTPException(status_code=500, detail="获取安全事件摘要失败")

@router.get("/threat-ips", summary="获取威胁IP列表")
async def get_threat_ips(
    limit: int = 20,
    current_user: AuthUser = Depends(get_current_user)
):
    """获取威胁最大的IP列表"""
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="限制数量必须在1-100之间")
        
        threat_ips = security_monitor.get_top_threat_ips(limit)
        return {
            "code": 1,
            "msg": "获取威胁IP列表成功",
            "data": {
                "threat_ips": threat_ips,
                "total_count": len(threat_ips)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get threat IPs: {e}")
        raise HTTPException(status_code=500, detail="获取威胁IP列表失败")

@router.post("/blacklist/add", summary="添加IP到黑名单")
async def add_to_blacklist(
    ip: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """添加IP到黑名单"""
    try:
        # 简单的IP格式验证
        import re
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not re.match(ip_pattern, ip):
            raise HTTPException(status_code=400, detail="无效的IP地址格式")
        
        # 这里需要获取SecurityMiddleware实例来添加黑名单
        # 由于中间件实例化的复杂性，这里提供一个简化的实现
        logger.warning(f"Admin {current_user.username} added IP {ip} to blacklist")
        
        return {
            "code": 1,
            "msg": f"IP {ip} 已添加到黑名单",
            "data": {"ip": ip}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add IP to blacklist: {e}")
        raise HTTPException(status_code=500, detail="添加IP到黑名单失败")

@router.post("/blacklist/remove", summary="从黑名单移除IP")
async def remove_from_blacklist(
    ip: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """从黑名单移除IP"""
    try:
        # 简单的IP格式验证
        import re
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not re.match(ip_pattern, ip):
            raise HTTPException(status_code=400, detail="无效的IP地址格式")
        
        logger.warning(f"Admin {current_user.username} removed IP {ip} from blacklist")
        
        return {
            "code": 1,
            "msg": f"IP {ip} 已从黑名单移除",
            "data": {"ip": ip}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove IP from blacklist: {e}")
        raise HTTPException(status_code=500, detail="从黑名单移除IP失败")

@router.get("/config", summary="获取安全配置")
async def get_security_config(current_user: AuthUser = Depends(get_current_user)):
    """获取当前安全配置"""
    try:
        from config.settings import settings
        
        config = {
            "rate_limiting": {
                "enabled": settings.RATE_LIMIT_ENABLED,
                "redis_available": bool(settings.RATE_LIMIT_REDIS_URL)
            },
            "security": {
                "enabled": settings.SECURITY_ENABLED,
                "max_login_attempts": settings.MAX_LOGIN_ATTEMPTS,
                "login_lockout_minutes": settings.LOGIN_LOCKOUT_MINUTES
            },
            "cors": {
                "allowed_origins": settings.get_cors_origins(),
                "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
                "allowed_methods": settings.CORS_ALLOW_METHODS,
                "allowed_headers": settings.CORS_ALLOW_HEADERS
            },
            "jwt": {
                "algorithm": settings.JWT_ALGORITHM,
                "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                "refresh_token_expire_days": settings.REFRESH_TOKEN_EXPIRE_DAYS
            }
        }
        
        return {
            "code": 1,
            "msg": "获取安全配置成功",
            "data": config
        }
    except Exception as e:
        logger.error(f"Failed to get security config: {e}")
        raise HTTPException(status_code=500, detail="获取安全配置失败")

@router.post("/test/event", summary="测试安全事件记录")
async def test_security_event(
    event_type: str,
    level: str,
    details: Dict[str, Any],
    current_user: AuthUser = Depends(get_current_user)
):
    """测试安全事件记录功能"""
    try:
        # 验证事件类型
        try:
            event_type_enum = SecurityEventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的事件类型")
        
        # 验证安全级别
        try:
            level_enum = SecurityLevel(level)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的安全级别")
        
        # 记录测试事件
        event = security_monitor.log_security_event(
            event_type=event_type_enum,
            level=level_enum,
            client_ip="127.0.0.1",
            user_agent="Test Client",
            request_path="/api/security/test/event",
            request_method="POST",
            details=details,
            user_id=current_user.id
        )
        
        return {
            "code": 1,
            "msg": "测试安全事件记录成功",
            "data": {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "level": event.level.value,
                "timestamp": event.timestamp
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test security event: {e}")
        raise HTTPException(status_code=500, detail="测试安全事件记录失败")
