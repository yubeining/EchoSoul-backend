"""
EchoSoul AI Platform Storage API
对象存储API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from app.db import get_database_session
from app.core.auth import get_current_user
from app.models.user_models import AuthUser
from app.services.storage_service import get_storage_service
from app.schemas.storage_schemas import (
    FileUploadResponse, FileInfoResponse, FileListResponse,
    BaseResponse, StorageStatusResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/status", response_model=StorageStatusResponse, summary="获取存储服务状态")
async def get_storage_status():
    """获取对象存储服务状态"""
    try:
        storage_service = get_storage_service()
        is_connected, message = storage_service.test_connection()
        
        return StorageStatusResponse(
            code=1 if is_connected else 0,
            msg=message,
            data={
                "connected": is_connected,
                "bucket_name": storage_service.config.bucket_name,
                "endpoint": storage_service.config.endpoint,
                "max_file_size": storage_service.config.max_file_size,
                "allowed_extensions": list(storage_service.config.allowed_extensions),
                "allowed_mime_types": list(storage_service.config.allowed_mime_types)
            }
        )
    except Exception as e:
        logger.error(f"Failed to get storage status: {e}")
        raise HTTPException(status_code=500, detail="获取存储状态失败")

@router.post("/upload", response_model=FileUploadResponse, summary="上传文件")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Form(default="uploads"),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """上传文件到对象存储"""
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 上传文件
        storage_service = get_storage_service()
        success, message, result = storage_service.upload_file(
            file_data=file_content,
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            user_id=current_user.id,
            folder=folder
        )
        
        if success:
            return FileUploadResponse(
                code=1,
                msg=message,
                data=result
            )
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败")

@router.post("/upload/avatar", response_model=FileUploadResponse, summary="上传用户头像")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """上传用户头像"""
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只能上传图片文件")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 上传头像到专门的avatar文件夹
        storage_service = get_storage_service()
        success, message, result = storage_service.upload_file(
            file_data=file_content,
            filename=file.filename or "avatar.jpg",
            content_type=file.content_type,
            user_id=current_user.id,
            folder="avatars"
        )
        
        if success:
            # 更新用户头像URL
            current_user.avatar = result["public_url"]
            db.commit()
            
            return FileUploadResponse(
                code=1,
                msg="头像上传成功",
                data=result
            )
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload avatar: {e}")
        raise HTTPException(status_code=500, detail="头像上传失败")

@router.get("/files", response_model=FileListResponse, summary="获取文件列表")
async def list_files(
    prefix: str = "",
    limit: int = 50,
    current_user: AuthUser = Depends(get_current_user)
):
    """获取文件列表"""
    try:
        # 限制查询范围到当前用户
        user_prefix = f"uploads/user_{current_user.id}/"
        if prefix:
            user_prefix += prefix
        
        storage_service = get_storage_service()
        success, message, files = storage_service.list_files(
            prefix=user_prefix,
            limit=limit
        )
        
        if success:
            return FileListResponse(
                code=1,
                msg=message,
                data={
                    "files": files,
                    "total": len(files),
                    "prefix": prefix
                }
            )
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail="获取文件列表失败")

@router.get("/file/{object_name:path}", response_model=FileInfoResponse, summary="获取文件信息")
async def get_file_info(
    object_name: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """获取文件信息"""
    try:
        # 验证文件是否属于当前用户
        if not object_name.startswith(f"uploads/user_{current_user.id}/"):
            raise HTTPException(status_code=403, detail="无权访问此文件")
        
        storage_service = get_storage_service()
        success, message, file_info = storage_service.get_file_info(object_name)
        
        if success:
            return FileInfoResponse(
                code=1,
                msg=message,
                data=file_info
            )
        else:
            raise HTTPException(status_code=404, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        raise HTTPException(status_code=500, detail="获取文件信息失败")

@router.delete("/file/{object_name:path}", response_model=BaseResponse, summary="删除文件")
async def delete_file(
    object_name: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """删除文件"""
    try:
        # 验证文件是否属于当前用户
        if not object_name.startswith(f"uploads/user_{current_user.id}/"):
            raise HTTPException(status_code=403, detail="无权删除此文件")
        
        storage_service = get_storage_service()
        success, message = storage_service.delete_file(object_name)
        
        if success:
            return BaseResponse(
                code=1,
                msg=message,
                data={"object_name": object_name}
            )
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail="删除文件失败")

@router.post("/test-upload", response_model=FileUploadResponse, summary="测试文件上传")
async def test_upload(
    file: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """测试文件上传功能"""
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 上传到测试文件夹
        storage_service = get_storage_service()
        success, message, result = storage_service.upload_file(
            file_data=file_content,
            filename=file.filename or "test_file",
            content_type=file.content_type or "application/octet-stream",
            user_id=current_user.id,
            folder="test"
        )
        
        if success:
            return FileUploadResponse(
                code=1,
                msg=f"测试上传成功: {message}",
                data=result
            )
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test upload: {e}")
        raise HTTPException(status_code=500, detail="测试上传失败")
