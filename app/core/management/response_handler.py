"""
统一响应处理器
提供标准化的API响应格式，减少重复代码
"""

from typing import Any, Dict, Optional, Union
from datetime import datetime

class ResponseHandler:
    """统一响应处理器"""
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "操作成功", 
        code: int = 1
    ) -> Dict[str, Any]:
        """成功响应"""
        response = {
            "code": code,
            "msg": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if data is not None:
            response["data"] = data
            
        return response
    
    @staticmethod
    def error(
        message: str = "操作失败", 
        code: int = 0, 
        error_type: str = "general_error",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """错误响应"""
        response = {
            "code": code,
            "msg": message,
            "error_type": error_type,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if details:
            response["details"] = details
            
        return response
    
    @staticmethod
    def validation_error(
        message: str = "数据验证失败",
        validation_errors: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """验证错误响应"""
        return ResponseHandler.error(
            message=message,
            code=400,
            error_type="validation_error",
            details=validation_errors
        )
    
    @staticmethod
    def auth_error(
        message: str = "认证失败"
    ) -> Dict[str, Any]:
        """认证错误响应"""
        return ResponseHandler.error(
            message=message,
            code=401,
            error_type="auth_error"
        )
    
    @staticmethod
    def permission_error(
        message: str = "权限不足"
    ) -> Dict[str, Any]:
        """权限错误响应"""
        return ResponseHandler.error(
            message=message,
            code=403,
            error_type="permission_error"
        )
    
    @staticmethod
    def not_found_error(
        message: str = "资源不存在"
    ) -> Dict[str, Any]:
        """资源不存在错误响应"""
        return ResponseHandler.error(
            message=message,
            code=404,
            error_type="not_found_error"
        )
    
    @staticmethod
    def server_error(
        message: str = "服务器内部错误"
    ) -> Dict[str, Any]:
        """服务器错误响应"""
        return ResponseHandler.error(
            message=message,
            code=500,
            error_type="server_error"
        )
    
    @staticmethod
    def paginated_response(
        data: list,
        page: int,
        limit: int,
        total: int,
        message: str = "获取数据成功"
    ) -> Dict[str, Any]:
        """分页响应"""
        return ResponseHandler.success(
            data={
                "items": data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            },
            message=message
        )

# 便捷函数
def success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """成功响应便捷函数"""
    return ResponseHandler.success(data=data, message=message)

def error_response(message: str = "操作失败", code: int = 0) -> Dict[str, Any]:
    """错误响应便捷函数"""
    return ResponseHandler.error(message=message, code=code)

def validation_error_response(message: str = "数据验证失败") -> Dict[str, Any]:
    """验证错误响应便捷函数"""
    return ResponseHandler.validation_error(message=message)

def auth_error_response(message: str = "认证失败") -> Dict[str, Any]:
    """认证错误响应便捷函数"""
    return ResponseHandler.auth_error(message=message)

def not_found_response(message: str = "资源不存在") -> Dict[str, Any]:
    """资源不存在响应便捷函数"""
    return ResponseHandler.not_found_error(message=message)

def server_error_response(message: str = "服务器内部错误") -> Dict[str, Any]:
    """服务器错误响应便捷函数"""
    return ResponseHandler.server_error(message=message)
