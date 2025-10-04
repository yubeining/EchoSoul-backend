"""
EchoSoul AI Platform Background Tasks
后台任务管理模块
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# 延迟导入以避免循环导入
# from app.websocket.ai_manager import ai_manager
# from app.websocket.simple_manager import simple_manager

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """后台任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}
        self.running = False
    
    async def start_all_tasks(self):
        """启动所有后台任务"""
        if self.running:
            return
        
        self.running = True
        logger.info("启动后台任务管理器")
        
        # 启动连接清理任务
        self.tasks["connection_cleanup"] = asyncio.create_task(
            self._connection_cleanup_task()
        )
        
        # 启动健康检查任务
        self.tasks["health_check"] = asyncio.create_task(
            self._health_check_task()
        )
        
        # 启动统计报告任务
        self.tasks["stats_report"] = asyncio.create_task(
            self._stats_report_task()
        )
    
    async def stop_all_tasks(self):
        """停止所有后台任务"""
        if not self.running:
            return
        
        self.running = False
        logger.info("停止后台任务管理器")
        
        # 取消所有任务
        for task_name, task in self.tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"后台任务 {task_name} 已取消")
        
        self.tasks.clear()
    
    async def _connection_cleanup_task(self):
        """连接清理任务"""
        while self.running:
            try:
                # 延迟导入以避免循环导入
                from app.websocket.ai_manager import ai_manager
                from app.websocket.simple_manager import simple_manager
                
                # 清理AI对话非活跃连接
                await ai_manager.cleanup_inactive_connections(timeout_minutes=30)
                
                # 清理简单WebSocket非活跃连接
                await simple_manager.cleanup_inactive_connections(timeout_minutes=30)
                
                # 每5分钟执行一次
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"连接清理任务异常: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟再重试
    
    async def _health_check_task(self):
        """健康检查任务"""
        while self.running:
            try:
                # 延迟导入以避免循环导入
                from app.websocket.ai_manager import ai_manager
                from app.websocket.simple_manager import simple_manager
                
                # 检查AI对话连接健康状态
                await ai_manager.health_check_connections()
                
                # 检查简单WebSocket连接健康状态
                await simple_manager.health_check_connections()
                
                # 每2分钟执行一次
                await asyncio.sleep(120)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查任务异常: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟再重试
    
    async def _stats_report_task(self):
        """统计报告任务"""
        while self.running:
            try:
                # 延迟导入以避免循环导入
                from app.websocket.ai_manager import ai_manager
                from app.websocket.simple_manager import simple_manager
                
                # 获取AI对话统计
                ai_stats = ai_manager.get_connection_stats()
                
                # 获取简单WebSocket统计
                simple_stats = simple_manager.get_stats()
                
                # 记录统计信息
                logger.info(f"WebSocket统计 - AI对话: {ai_stats['active_connections']} 连接, "
                           f"简单WebSocket: {simple_stats.get('active_connections', 0)} 连接")
                
                # 每10分钟执行一次
                await asyncio.sleep(600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"统计报告任务异常: {e}")
                await asyncio.sleep(300)  # 出错后等待5分钟再重试
    
    def get_task_status(self) -> Dict[str, Any]:
        """获取任务状态"""
        status = {}
        for task_name, task in self.tasks.items():
            status[task_name] = {
                "running": not task.done(),
                "cancelled": task.cancelled(),
                "exception": task.exception() if task.done() and not task.cancelled() else None
            }
        return status

# 全局后台任务管理器实例
background_task_manager = BackgroundTaskManager()
