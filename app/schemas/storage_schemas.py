"""
EchoSoul AI Platform Storage Schemas
对象存储相关的Pydantic模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .common_schemas import BaseResponse

class FileUploadData(BaseModel):
    """文件上传数据模式"""
    object_name: str = Field(..., description="对象名称")
    filename: str = Field(..., description="原始文件名")
    size: int = Field(..., description="文件大小（字节）")
    content_type: str = Field(..., description="文件MIME类型")
    public_url: str = Field(..., description="公开访问URL")
    upload_time: str = Field(..., description="上传时间")
    user_id: Optional[int] = Field(None, description="用户ID")

class FileUploadResponse(BaseModel):
    """文件上传响应模式"""
    code: int = Field(1, description="响应码")
    msg: str = Field(..., description="提示信息")
    data: Optional[FileUploadData] = Field(None, description="上传结果数据")

class FileInfoData(BaseModel):
    """文件信息数据模式"""
    object_name: str = Field(..., description="对象名称")
    size: int = Field(..., description="文件大小（字节）")
    content_type: str = Field(..., description="文件MIME类型")
    last_modified: str = Field(..., description="最后修改时间")
    etag: str = Field(..., description="文件ETag")
    public_url: str = Field(..., description="公开访问URL")

class FileInfoResponse(BaseModel):
    """文件信息响应模式"""
    code: int = Field(1, description="响应码")
    msg: str = Field(..., description="提示信息")
    data: Optional[FileInfoData] = Field(None, description="文件信息数据")

class FileListData(BaseModel):
    """文件列表数据模式"""
    files: List[FileInfoData] = Field(..., description="文件列表")
    total: int = Field(..., description="文件总数")
    prefix: str = Field(..., description="查询前缀")

class FileListResponse(BaseModel):
    """文件列表响应模式"""
    code: int = Field(1, description="响应码")
    msg: str = Field(..., description="提示信息")
    data: Optional[FileListData] = Field(None, description="文件列表数据")

class StorageStatusData(BaseModel):
    """存储状态数据模式"""
    connected: bool = Field(..., description="连接状态")
    bucket_name: str = Field(..., description="存储桶名称")
    endpoint: str = Field(..., description="服务端点")
    max_file_size: int = Field(..., description="最大文件大小")
    allowed_extensions: List[str] = Field(..., description="允许的文件扩展名")
    allowed_mime_types: List[str] = Field(..., description="允许的MIME类型")

class StorageStatusResponse(BaseModel):
    """存储状态响应模式"""
    code: int = Field(1, description="响应码")
    msg: str = Field(..., description="提示信息")
    data: Optional[StorageStatusData] = Field(None, description="存储状态数据")

class FileDeleteResponse(BaseModel):
    """文件删除响应模式"""
    code: int = Field(1, description="响应码")
    msg: str = Field(..., description="提示信息")
    data: Optional[Dict[str, str]] = Field(None, description="删除结果数据")
