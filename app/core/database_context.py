"""
数据库会话上下文管理器
提供统一的数据库会话管理，减少重复代码
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy.orm import Session

from app.db import mysql_db
from app.core.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    数据库会话上下文管理器
    自动处理数据库会话的创建、提交和关闭
    """
    db = None
    try:
        db = mysql_db.get_session()
        yield db
        db.commit()
    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"数据库操作失败: {e}")
        raise
    finally:
        if db:
            db.close()

@contextmanager
def get_db_session_with_error_handling() -> Generator[Session, None, None]:
    """
    带错误处理的数据库会话上下文管理器
    返回标准化的错误响应
    """
    db = None
    try:
        db = mysql_db.get_session()
        yield db
        db.commit()
    except Exception as e:
        if db:
            db.rollback()
        error_response = ErrorHandler.handle_database_error(e)
        logger.error(f"数据库操作失败: {error_response}")
        raise Exception(error_response["error"])
    finally:
        if db:
            db.close()

class DatabaseSessionManager:
    """数据库会话管理器类"""
    
    @staticmethod
    def execute_with_session(func, *args, **kwargs):
        """
        在数据库会话中执行函数
        自动处理会话管理和错误处理
        """
        with get_db_session() as db:
            return func(db, *args, **kwargs)
    
    @staticmethod
    def execute_with_error_handling(func, *args, **kwargs):
        """
        在数据库会话中执行函数，带错误处理
        """
        with get_db_session_with_error_handling() as db:
            return func(db, *args, **kwargs)
