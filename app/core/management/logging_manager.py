"""
日志管理器
统一管理日志输出，减少不必要的控制台输出
"""

import logging
import os
from typing import Optional
from config.settings import settings

class LoggingManager:
    """日志管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.debug_mode = settings.DEBUG
        self.log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    def should_log(self, level: int) -> bool:
        """判断是否应该记录日志"""
        return level >= self.log_level
    
    def log_operation_start(self, operation: str, **kwargs):
        """记录操作开始（仅在调试模式下）"""
        if self.debug_mode and self.should_log(logging.DEBUG):
            details = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.debug(f"开始执行: {operation}" + (f" ({details})" if details else ""))
    
    def log_operation_success(self, operation: str, **kwargs):
        """记录操作成功（仅在调试模式下）"""
        if self.debug_mode and self.should_log(logging.DEBUG):
            details = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.debug(f"操作成功: {operation}" + (f" ({details})" if details else ""))
    
    def log_operation_error(self, operation: str, error: str, **kwargs):
        """记录操作错误（总是记录）"""
        details = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.logger.error(f"操作失败: {operation} - {error}" + (f" ({details})" if details else ""))
    
    def log_info(self, message: str, **kwargs):
        """记录信息日志"""
        if self.should_log(logging.INFO):
            details = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.info(f"{message}" + (f" ({details})" if details else ""))
    
    def log_warning(self, message: str, **kwargs):
        """记录警告日志"""
        if self.should_log(logging.WARNING):
            details = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.warning(f"{message}" + (f" ({details})" if details else ""))
    
    def log_error(self, message: str, **kwargs):
        """记录错误日志"""
        if self.should_log(logging.ERROR):
            details = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.error(f"{message}" + (f" ({details})" if details else ""))

# 全局日志管理器实例
logging_manager = LoggingManager()

# 便捷函数
def log_operation_start(operation: str, **kwargs):
    """记录操作开始"""
    logging_manager.log_operation_start(operation, **kwargs)

def log_operation_success(operation: str, **kwargs):
    """记录操作成功"""
    logging_manager.log_operation_success(operation, **kwargs)

def log_operation_error(operation: str, error: str, **kwargs):
    """记录操作错误"""
    logging_manager.log_operation_error(operation, error, **kwargs)

def log_info(message: str, **kwargs):
    """记录信息日志"""
    logging_manager.log_info(message, **kwargs)

def log_warning(message: str, **kwargs):
    """记录警告日志"""
    logging_manager.log_warning(message, **kwargs)

def log_error(message: str, **kwargs):
    """记录错误日志"""
    logging_manager.log_error(message, **kwargs)
