"""
EchoSoul AI Platform Mock Storage Service
模拟对象存储服务 - 用于测试和演示
"""

import os
import uuid
import hashlib
import mimetypes
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MockObjectStorageService:
    """模拟对象存储服务类"""
    
    def __init__(self):
        self.config = {
            "bucket_name": "echosoul-avatar",
            "endpoint": "objectstorageapi.bja.sealos.run",
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "allowed_extensions": {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'},
            "allowed_mime_types": {
                'image/jpeg', 'image/png', 'image/gif', 'image/webp', 
                'image/bmp', 'image/svg+xml'
            },
            "public_url_base": "https://objectstorageapi.bja.sealos.run"
        }
        
        # 模拟存储
        self.mock_files = {}
        logger.info("Mock object storage service initialized")
    
    def validate_file(self, filename: str, content_type: str, size: int) -> tuple[bool, str]:
        """验证文件是否符合要求"""
        # 检查文件大小
        if size > self.config["max_file_size"]:
            return False, f"文件大小超过限制 ({self.config['max_file_size'] // (1024*1024)}MB)"
        
        # 检查文件扩展名
        if not any(filename.lower().endswith(ext) for ext in self.config["allowed_extensions"]):
            return False, f"不支持的文件类型，支持的格式: {', '.join(self.config['allowed_extensions'])}"
        
        # 检查MIME类型
        if content_type not in self.config["allowed_mime_types"]:
            return False, f"不支持的文件MIME类型: {content_type}"
        
        return True, "文件验证通过"
    
    def upload_file(
        self, 
        file_data: bytes, 
        filename: str, 
        content_type: str,
        user_id: Optional[int] = None,
        folder: str = "uploads"
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """模拟上传文件到对象存储"""
        
        try:
            # 验证文件
            is_valid, message = self.validate_file(filename, content_type, len(file_data))
            if not is_valid:
                return False, message, None
            
            # 生成对象名称
            object_name = self._generate_object_name(filename, user_id, folder)
            
            # 模拟存储文件
            self.mock_files[object_name] = {
                "data": file_data,
                "filename": filename,
                "content_type": content_type,
                "size": len(file_data),
                "upload_time": datetime.utcnow()
            }
            
            # 生成访问URL
            public_url = f"{self.config['public_url_base']}/{self.config['bucket_name']}/{object_name}"
            
            # 返回上传结果
            result = {
                "object_name": object_name,
                "filename": filename,
                "size": len(file_data),
                "content_type": content_type,
                "public_url": public_url,
                "upload_time": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
            
            logger.info(f"Mock file uploaded successfully: {object_name}")
            return True, "文件上传成功（模拟）", result
            
        except Exception as e:
            logger.error(f"Unexpected error during mock file upload: {e}")
            return False, f"上传失败: {str(e)}", None
    
    def _generate_object_name(self, filename: str, user_id: Optional[int], folder: str) -> str:
        """生成唯一的对象名称"""
        # 获取文件扩展名
        _, ext = os.path.splitext(filename)
        
        # 生成时间戳
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # 生成唯一ID
        unique_id = str(uuid.uuid4())[:8]
        
        # 构建对象名称
        if user_id:
            object_name = f"{folder}/user_{user_id}/{timestamp}_{unique_id}{ext}"
        else:
            object_name = f"{folder}/{timestamp}_{unique_id}{ext}"
        
        return object_name
    
    def delete_file(self, object_name: str) -> Tuple[bool, str]:
        """模拟删除文件"""
        try:
            if object_name in self.mock_files:
                del self.mock_files[object_name]
                logger.info(f"Mock file deleted successfully: {object_name}")
                return True, "文件删除成功（模拟）"
            else:
                return False, "文件不存在"
        except Exception as e:
            logger.error(f"Unexpected error during mock file deletion: {e}")
            return False, f"删除失败: {str(e)}"
    
    def get_file_info(self, object_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取文件信息"""
        try:
            if object_name not in self.mock_files:
                return False, "文件不存在", None
            
            file_data = self.mock_files[object_name]
            
            result = {
                "object_name": object_name,
                "size": file_data["size"],
                "content_type": file_data["content_type"],
                "last_modified": file_data["upload_time"].isoformat(),
                "etag": hashlib.md5(file_data["data"]).hexdigest(),
                "public_url": f"{self.config['public_url_base']}/{self.config['bucket_name']}/{object_name}"
            }
            
            return True, "获取文件信息成功（模拟）", result
            
        except Exception as e:
            logger.error(f"Unexpected error during mock file info retrieval: {e}")
            return False, f"获取文件信息失败: {str(e)}", None
    
    def list_files(self, prefix: str = "", limit: int = 100) -> Tuple[bool, str, Optional[list]]:
        """列出文件"""
        try:
            files = []
            count = 0
            
            for object_name, file_data in self.mock_files.items():
                if prefix and not object_name.startswith(prefix):
                    continue
                
                if count >= limit:
                    break
                
                file_info = {
                    "object_name": object_name,
                    "size": file_data["size"],
                    "last_modified": file_data["upload_time"].isoformat(),
                    "etag": hashlib.md5(file_data["data"]).hexdigest(),
                    "public_url": f"{self.config['public_url_base']}/{self.config['bucket_name']}/{object_name}"
                }
                files.append(file_info)
                count += 1
            
            return True, f"获取文件列表成功（模拟），共{len(files)}个文件", files
            
        except Exception as e:
            logger.error(f"Unexpected error during mock file listing: {e}")
            return False, f"获取文件列表失败: {str(e)}", None
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试连接"""
        return True, "模拟存储服务连接正常"

# 全局服务实例
mock_storage_service = MockObjectStorageService()
