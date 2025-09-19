"""
EchoSoul AI Platform Object Storage Configuration
对象存储服务配置
"""

import os
from minio import Minio
from minio.error import S3Error
import logging

logger = logging.getLogger(__name__)

class ObjectStorageConfig:
    """对象存储配置类"""
    
    def __init__(self):
        # Sealos对象存储配置
        self.access_key = os.getenv("OBJECT_STORAGE_ACCESS_KEY", "7rdhhsv1")
        self.secret_key = os.getenv("OBJECT_STORAGE_SECRET_KEY", "wldzmkdvzdp7mtp7")
        # 使用外部域名，根据MinIO文档配置
        self.endpoint = os.getenv("OBJECT_STORAGE_ENDPOINT", "objectstorageapi.bja.sealos.run")
        self.bucket_name = os.getenv("OBJECT_STORAGE_BUCKET", "7rdhhsv1-echosoul-avatar")
        self.secure = os.getenv("OBJECT_STORAGE_SECURE", "true").lower() == "true"  # 使用HTTPS
        
        # 文件上传配置
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
        self.allowed_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'
        }
        self.allowed_mime_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/webp', 
            'image/bmp', 'image/svg+xml'
        }
        
        # URL配置 - 使用外部可访问的域名
        self.public_url_base = os.getenv("PUBLIC_URL_BASE", "https://static-host-7rdhhsv1-echosoul-avatar.sealosbja.site")
    
    def get_minio_client(self) -> Minio:
        """获取MinIO客户端实例"""
        try:
            client = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            return client
        except Exception as e:
            logger.error(f"Failed to create MinIO client: {e}")
            raise
    
    def validate_file(self, filename: str, content_type: str, size: int) -> tuple[bool, str]:
        """验证文件是否符合要求"""
        # 检查文件大小
        if size > self.max_file_size:
            return False, f"文件大小超过限制 ({self.max_file_size // (1024*1024)}MB)"
        
        # 检查文件扩展名
        if not any(filename.lower().endswith(ext) for ext in self.allowed_extensions):
            return False, f"不支持的文件类型，支持的格式: {', '.join(self.allowed_extensions)}"
        
        # 检查MIME类型
        if content_type not in self.allowed_mime_types:
            return False, f"不支持的文件MIME类型: {content_type}"
        
        return True, "文件验证通过"
    
    def get_public_url(self, object_name: str) -> str:
        """获取文件的公开访问URL"""
        return f"{self.public_url_base}/{self.bucket_name}/{object_name}"

# 全局配置实例
storage_config = ObjectStorageConfig()
