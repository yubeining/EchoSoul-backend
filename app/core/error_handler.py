"""
EchoSoul AI Platform Error Handler
统一错误处理和响应模块
"""

import logging
import traceback
from typing import Any, Dict, Optional
from datetime import datetime
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def handle_database_error(e: Exception, operation: str = "数据库操作") -> Dict[str, Any]:
        """处理数据库错误"""
        error_msg = f"{operation}失败"
        
        # 记录详细错误信息
        logger.error(f"{operation}异常: {str(e)}")
        logger.debug(f"数据库错误堆栈: {traceback.format_exc()}")
        
        # 根据错误类型返回不同的错误信息
        if "connection" in str(e).lower():
            error_msg = "数据库连接失败，请稍后重试"
        elif "timeout" in str(e).lower():
            error_msg = "数据库操作超时，请稍后重试"
        elif "constraint" in str(e).lower():
            error_msg = "数据约束错误，请检查输入数据"
        elif "not found" in str(e).lower():
            error_msg = "请求的数据不存在"
        else:
            error_msg = f"{operation}失败: {str(e)}"
        
        return {
            "success": False,
            "error": error_msg,
            "error_type": "database_error",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    @staticmethod
    def handle_websocket_error(e: Exception, user_id: Optional[int] = None) -> Dict[str, Any]:
        """处理WebSocket错误"""
        error_msg = "WebSocket连接错误"
        
        # 记录详细错误信息
        if user_id:
            logger.error(f"用户 {user_id} WebSocket错误: {str(e)}")
        else:
            logger.error(f"WebSocket错误: {str(e)}")
        logger.debug(f"WebSocket错误堆栈: {traceback.format_exc()}")
        
        # 根据错误类型返回不同的错误信息
        if "connection" in str(e).lower():
            error_msg = "WebSocket连接已断开"
        elif "timeout" in str(e).lower():
            error_msg = "WebSocket操作超时"
        elif "closed" in str(e).lower():
            error_msg = "WebSocket连接已关闭"
        else:
            error_msg = f"WebSocket错误: {str(e)}"
        
        return {
            "success": False,
            "error": error_msg,
            "error_type": "websocket_error",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    @staticmethod
    def handle_llm_error(e: Exception, operation: str = "AI服务") -> Dict[str, Any]:
        """处理LLM服务错误"""
        error_msg = f"{operation}失败"
        
        # 记录详细错误信息
        logger.error(f"{operation}异常: {str(e)}")
        logger.debug(f"LLM错误堆栈: {traceback.format_exc()}")
        
        # 根据错误类型返回不同的错误信息
        if "timeout" in str(e).lower():
            error_msg = "AI服务响应超时，请稍后重试"
        elif "connection" in str(e).lower():
            error_msg = "AI服务连接失败，请稍后重试"
        elif "rate limit" in str(e).lower():
            error_msg = "AI服务请求过于频繁，请稍后重试"
        elif "quota" in str(e).lower():
            error_msg = "AI服务配额不足，请稍后重试"
        else:
            error_msg = f"{operation}暂时不可用，请稍后重试"
        
        return {
            "success": False,
            "error": error_msg,
            "error_type": "llm_error",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    @staticmethod
    def handle_validation_error(e: Exception, field: str = "输入数据") -> Dict[str, Any]:
        """处理数据验证错误"""
        error_msg = f"{field}验证失败"
        
        # 记录详细错误信息
        logger.warning(f"数据验证错误: {str(e)}")
        
        # 提取具体的验证错误信息
        if hasattr(e, 'errors'):
            # Pydantic验证错误
            error_details = []
            for error in e.errors():
                field_name = ".".join(str(x) for x in error.get("loc", []))
                error_msg_detail = error.get("msg", "验证失败")
                error_details.append(f"{field_name}: {error_msg_detail}")
            
            if error_details:
                error_msg = "; ".join(error_details)
        else:
            error_msg = str(e)
        
        return {
            "success": False,
            "error": error_msg,
            "error_type": "validation_error",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    @staticmethod
    def handle_auth_error(e: Exception, operation: str = "认证") -> Dict[str, Any]:
        """处理认证错误"""
        error_msg = f"{operation}失败"
        
        # 记录详细错误信息
        logger.warning(f"{operation}错误: {str(e)}")
        
        # 根据错误类型返回不同的错误信息
        if "token" in str(e).lower():
            error_msg = "认证令牌无效或已过期"
        elif "permission" in str(e).lower():
            error_msg = "权限不足"
        elif "password" in str(e).lower():
            error_msg = "密码错误"
        elif "user" in str(e).lower():
            error_msg = "用户不存在"
        else:
            error_msg = f"{operation}失败: {str(e)}"
        
        return {
            "success": False,
            "error": error_msg,
            "error_type": "auth_error",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    @staticmethod
    def handle_general_error(e: Exception, operation: str = "操作") -> Dict[str, Any]:
        """处理一般错误"""
        error_msg = f"{operation}失败"
        
        # 记录详细错误信息
        logger.error(f"{operation}异常: {str(e)}")
        logger.debug(f"一般错误堆栈: {traceback.format_exc()}")
        
        return {
            "success": False,
            "error": error_msg,
            "error_type": "general_error",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    @staticmethod
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """全局异常处理器"""
        # 记录异常信息
        logger.error(f"全局异常捕获: {str(exc)}")
        logger.debug(f"异常堆栈: {traceback.format_exc()}")
        
        # 根据异常类型处理
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": exc.detail,
                    "error_type": "http_error",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "服务器内部错误",
                    "error_type": "internal_error",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

# 便捷函数
def handle_error(e: Exception, error_type: str = "general", **kwargs) -> Dict[str, Any]:
    """便捷的错误处理函数"""
    handlers = {
        "database": ErrorHandler.handle_database_error,
        "websocket": ErrorHandler.handle_websocket_error,
        "llm": ErrorHandler.handle_llm_error,
        "validation": ErrorHandler.handle_validation_error,
        "auth": ErrorHandler.handle_auth_error,
        "general": ErrorHandler.handle_general_error
    }
    
    handler = handlers.get(error_type, ErrorHandler.handle_general_error)
    return handler(e, **kwargs)
