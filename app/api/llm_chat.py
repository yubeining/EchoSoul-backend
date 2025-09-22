"""
EchoSoul AI Platform LLM Chat API Routes
大模型对话API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.db import get_database_session
from app.core.auth import get_current_user
from app.models.user_models import AuthUser
from app.services.llm_service import LLMService
from app.schemas.chat_schemas import MessageResponse

router = APIRouter()

# 请求模型
class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色: user, assistant, system")
    content: str = Field(..., description="消息内容")

class ChatCompletionRequest(BaseModel):
    """聊天完成请求模型"""
    messages: List[ChatMessage] = Field(..., description="对话消息列表")
    model: Optional[str] = Field("deepseek-chat", description="模型名称")
    max_tokens: Optional[int] = Field(512, ge=1, le=4096, description="最大生成token数")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    stream: Optional[bool] = Field(False, description="是否流式返回")

class SimpleChatRequest(BaseModel):
    """简单对话请求模型"""
    message: str = Field(..., description="用户消息")
    system_prompt: Optional[str] = Field(None, description="系统提示词")

class CharacterChatRequest(BaseModel):
    """角色对话请求模型"""
    message: str = Field(..., description="用户消息")
    character_name: str = Field(..., description="角色名称")
    character_personality: Optional[str] = Field(None, description="角色性格描述")

# 响应模型
class ChatCompletionResponse(BaseModel):
    """聊天完成响应模型"""
    success: bool = Field(..., description="是否成功")
    content: Optional[str] = Field(None, description="AI回复内容")
    usage: Optional[Dict[str, Any]] = Field(None, description="使用统计")
    model: Optional[str] = Field(None, description="使用的模型")
    error: Optional[str] = Field(None, description="错误信息")

class SimpleChatResponse(BaseModel):
    """简单对话响应模型"""
    success: bool = Field(..., description="是否成功")
    reply: Optional[str] = Field(None, description="AI回复")
    error: Optional[str] = Field(None, description="错误信息")

@router.post("/chat/completions", 
             response_model=ChatCompletionResponse,
             summary="大模型对话完成接口")
async def chat_completions(
    request: ChatCompletionRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    调用大模型API进行对话完成
    
    这个接口完全兼容OpenAI的chat/completions格式
    """
    try:
        # 转换消息格式
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # 调用大模型服务
        result = await LLMService.chat_completion(
            messages=messages,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream
        )
        
        if result:
            # 解析响应
            parsed_result = LLMService.parse_api_response(result)
            
            if parsed_result["success"]:
                return ChatCompletionResponse(
                    success=True,
                    content=parsed_result["content"],
                    usage=parsed_result["usage"],
                    model=parsed_result["model"]
                )
            else:
                return ChatCompletionResponse(
                    success=False,
                    error=parsed_result["error"]
                )
        else:
            return ChatCompletionResponse(
                success=False,
                error="大模型API调用失败"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务内部错误: {str(e)}")

@router.post("/chat/simple", 
             response_model=SimpleChatResponse,
             summary="简单对话接口")
async def simple_chat(
    request: SimpleChatRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    简单的对话接口，适合快速对话场景
    """
    try:
        # 调用简单对话服务
        reply = await LLMService.simple_chat(
            user_message=request.message,
            system_prompt=request.system_prompt
        )
        
        if reply:
            return SimpleChatResponse(
                success=True,
                reply=reply
            )
        else:
            return SimpleChatResponse(
                success=False,
                error="AI回复生成失败"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务内部错误: {str(e)}")

@router.post("/chat/character", 
             response_model=SimpleChatResponse,
             summary="角色对话接口")
async def character_chat(
    request: CharacterChatRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    与AI角色对话接口
    """
    try:
        # 调用角色对话服务
        reply = await LLMService.chat_with_character(
            user_message=request.message,
            character_name=request.character_name,
            character_personality=request.character_personality
        )
        
        if reply:
            return SimpleChatResponse(
                success=True,
                reply=reply
            )
        else:
            return SimpleChatResponse(
                success=False,
                error="AI角色回复生成失败"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务内部错误: {str(e)}")

@router.get("/chat/models", 
            summary="获取可用模型列表")
async def get_available_models(
    current_user: AuthUser = Depends(get_current_user)
):
    """
    获取可用的模型列表
    """
    try:
        # 目前支持的主要模型
        models = [
            {
                "id": "deepseek-chat",
                "object": "model",
                "created": 1729672480,
                "owned_by": "deepseek",
                "description": "DeepSeek Chat模型，支持中文对话"
            },
            {
                "id": "gpt-3.5-turbo",
                "object": "model", 
                "created": 1729672480,
                "owned_by": "openai",
                "description": "GPT-3.5 Turbo模型"
            },
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1729672480,
                "owned_by": "openai", 
                "description": "GPT-4模型"
            }
        ]
        
        return {
            "object": "list",
            "data": models
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务内部错误: {str(e)}")

@router.get("/chat/health", 
            summary="大模型服务健康检查")
async def llm_health_check(
    current_user: AuthUser = Depends(get_current_user)
):
    """
    检查大模型服务是否正常
    """
    try:
        # 发送一个简单的测试请求
        test_messages = [{"role": "user", "content": "Hello"}]
        result = await LLMService.chat_completion(
            messages=test_messages,
            max_tokens=10
        )
        
        if result:
            return {
                "status": "healthy",
                "message": "大模型服务正常运行",
                "timestamp": int(datetime.now().timestamp())
            }
        else:
            return {
                "status": "unhealthy", 
                "message": "大模型服务异常",
                "timestamp": int(datetime.now().timestamp())
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"健康检查失败: {str(e)}",
            "timestamp": int(datetime.now().timestamp())
        }
