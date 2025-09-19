"""
EchoSoul AI Platform Object Storage Service
对象存储服务 - 处理文件上传和管理
"""

import os
import uuid
import hashlib
import mimetypes
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from minio import Minio
from minio.error import S3Error
import logging

from config.storage import storage_config

logger = logging.getLogger(__name__)

class ObjectStorageService:
    """对象存储服务类"""
    
    def __init__(self):
        self.config = storage_config
        self.client: Optional[Minio] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化MinIO客户端"""
        try:
            self.client = self.config.get_minio_client()
            # 确保bucket存在
            self._ensure_bucket_exists()
            logger.info(f"Object storage client initialized successfully for bucket: {self.config.bucket_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize object storage client: {e}")
            logger.warning("Object storage service will be disabled")
            self.client = None
    
    def _ensure_bucket_exists(self):
        """确保bucket存在"""
        if not self.client:
            raise Exception("MinIO client not initialized")
        
        try:
            if not self.client.bucket_exists(self.config.bucket_name):
                self.client.make_bucket(self.config.bucket_name)
                logger.info(f"Created bucket: {self.config.bucket_name}")
            else:
                logger.info(f"Bucket already exists: {self.config.bucket_name}")
        except S3Error as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            raise
    
    def upload_file(
        self, 
        file_data: bytes, 
        filename: str, 
        content_type: str,
        user_id: Optional[int] = None,
        folder: str = "uploads"
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """上传文件到对象存储"""
        
        if not self.client:
            return False, "对象存储服务未初始化", None
        
        try:
            # 验证文件
            is_valid, message = self.config.validate_file(filename, content_type, len(file_data))
            if not is_valid:
                return False, message, None
            
            # 生成对象名称
            object_name = self._generate_object_name(filename, user_id, folder)
            
            # 上传文件
            from io import BytesIO
            file_stream = BytesIO(file_data)
            
            self.client.put_object(
                bucket_name=self.config.bucket_name,
                object_name=object_name,
                data=file_stream,
                length=len(file_data),
                content_type=content_type
            )
            
            # 生成访问URL
            public_url = self.config.get_public_url(object_name)
            
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
            
            logger.info(f"File uploaded successfully: {object_name}")
            return True, "文件上传成功", result
            
        except S3Error as e:
            logger.error(f"S3 error during file upload: {e}")
            return False, f"上传失败: {str(e)}", None
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
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
        """删除文件"""
        if not self.client:
            return False, "对象存储服务未初始化"
        
        try:
            self.client.remove_object(self.config.bucket_name, object_name)
            logger.info(f"File deleted successfully: {object_name}")
            return True, "文件删除成功"
        except S3Error as e:
            logger.error(f"S3 error during file deletion: {e}")
            return False, f"删除失败: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during file deletion: {e}")
            return False, f"删除失败: {str(e)}"
    
    def get_file_info(self, object_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取文件信息"""
        if not self.client:
            return False, "对象存储服务未初始化", None
        
        try:
            stat = self.client.stat_object(self.config.bucket_name, object_name)
            
            result = {
                "object_name": object_name,
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified.isoformat(),
                "etag": stat.etag,
                "public_url": self.config.get_public_url(object_name)
            }
            
            return True, "获取文件信息成功", result
            
        except S3Error as e:
            logger.error(f"S3 error during file info retrieval: {e}")
            return False, f"获取文件信息失败: {str(e)}", None
        except Exception as e:
            logger.error(f"Unexpected error during file info retrieval: {e}")
            return False, f"获取文件信息失败: {str(e)}", None
    
    def list_files(self, prefix: str = "", limit: int = 100) -> Tuple[bool, str, Optional[list]]:
        """列出文件"""
        if not self.client:
            return False, "对象存储服务未初始化", None
        
        try:
            objects = self.client.list_objects(
                bucket_name=self.config.bucket_name,
                prefix=prefix,
                recursive=True
            )
            
            files = []
            count = 0
            for obj in objects:
                if count >= limit:
                    break
                
                file_info = {
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat(),
                    "etag": obj.etag,
                    "public_url": self.config.get_public_url(obj.object_name)
                }
                files.append(file_info)
                count += 1
            
            return True, f"获取文件列表成功，共{len(files)}个文件", files
            
        except S3Error as e:
            logger.error(f"S3 error during file listing: {e}")
            return False, f"获取文件列表失败: {str(e)}", None
        except Exception as e:
            logger.error(f"Unexpected error during file listing: {e}")
            return False, f"获取文件列表失败: {str(e)}", None
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试连接"""
        if not self.client:
            return False, "对象存储服务未初始化"
        
        try:
            # 尝试列出bucket
            list(self.client.list_objects(self.config.bucket_name))
            return True, "对象存储连接正常"
        except S3Error as e:
            logger.error(f"S3 error during connection test: {e}")
            return False, f"连接测试失败: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}")
            return False, f"连接测试失败: {str(e)}"

# 全局服务实例 - 延迟初始化
storage_service = None

def get_storage_service():
    """获取存储服务实例，延迟初始化"""
    global storage_service
    if storage_service is None:
        storage_service = ObjectStorageService()
    return storage_service
