"""
EchoSoul AI Platform LLM Service
大模型对话服务
"""

import httpx
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMService:
    """大模型服务类"""
    
    # API配置
    API_BASE_URL = "https://aiproxy.bja.sealos.run/v1/chat/completions"
    API_TOKEN = "sk-x6iUbkz1Tsd6tiy2SaNyIooATaSiYYsMAGoaR45SonVkG23U"
    
    # 默认模型配置
    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_MAX_TOKENS = 512
    DEFAULT_TEMPERATURE = 0.7
    
    @classmethod
    async def chat_completion(
        cls,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        stream: bool = False,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        调用大模型API进行对话
        
        Args:
            messages: 对话消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称，默认为 deepseek-chat
            max_tokens: 最大生成token数
            temperature: 温度参数，控制随机性
            stream: 是否流式返回
            **kwargs: 其他参数
            
        Returns:
            API响应结果或None（如果失败）
        """
        try:
            # 设置默认参数
            model = model or cls.DEFAULT_MODEL
            max_tokens = max_tokens or cls.DEFAULT_MAX_TOKENS
            temperature = temperature or cls.DEFAULT_TEMPERATURE
            
            # 构建请求数据
            request_data = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "max_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
            
            # 设置请求头
            headers = {
                "Authorization": f"Bearer {cls.API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"调用大模型API: {model}, 消息数量: {len(messages)}")
            
            # 发送请求
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    cls.API_BASE_URL,
                    headers=headers,
                    json=request_data
                )
                
                # 检查响应状态
                if response.status_code == 200:
                    if stream:
                        # 处理流式响应
                        return await cls._handle_stream_response(response)
                    else:
                        result = response.json()
                        logger.info(f"大模型API调用成功: {model}")
                        return result
                else:
                    logger.error(f"大模型API调用失败: {response.status_code}, {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("大模型API调用超时")
            return None
        except httpx.RequestError as e:
            logger.error(f"大模型API请求错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"大模型API调用异常: {str(e)}")
            return None
    
    @classmethod
    async def simple_chat(
        cls,
        user_message: str,
        system_prompt: str = None,
        conversation_history: List[Dict[str, str]] = None,
        **kwargs
    ) -> Optional[str]:
        """
        简单的对话接口
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            conversation_history: 对话历史
            **kwargs: 其他参数
            
        Returns:
            AI回复内容或None（如果失败）
        """
        try:
            # 构建消息列表
            messages = []
            
            # 添加系统提示词
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加对话历史
            if conversation_history:
                messages.extend(conversation_history)
            
            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 调用API
            result = await cls.chat_completion(messages, **kwargs)
            
            if result and "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return None
                
        except Exception as e:
            logger.error(f"简单对话调用异常: {str(e)}")
            return None
    
    @classmethod
    async def chat_with_character(
        cls,
        user_message: str,
        character_name: str,
        character_personality: str = None,
        conversation_history: List[Dict[str, str]] = None,
        **kwargs
    ) -> Optional[str]:
        """
        与AI角色对话
        
        Args:
            user_message: 用户消息
            character_name: 角色名称
            character_personality: 角色性格描述
            conversation_history: 对话历史
            **kwargs: 其他参数
            
        Returns:
            AI角色回复或None（如果失败）
        """
        try:
            # 构建角色系统提示词
            system_prompt = f"你是{character_name}，"
            if character_personality:
                system_prompt += f"具有以下性格特点：{character_personality}。"
            system_prompt += "请以这个角色的身份和用户对话，保持角色的一致性。"
            
            # 调用简单对话
            return await cls.simple_chat(
                user_message=user_message,
                system_prompt=system_prompt,
                conversation_history=conversation_history,
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"角色对话调用异常: {str(e)}")
            return None
    
    @classmethod
    def parse_api_response(cls, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析API响应
        
        Args:
            response: API原始响应
            
        Returns:
            解析后的响应数据
        """
        try:
            if not response:
                return {
                    "success": False,
                    "error": "API响应为空"
                }
            
            # 检查是否有错误
            if "error" in response:
                return {
                    "success": False,
                    "error": response["error"]
                }
            
            # 提取有用信息
            if "choices" in response and len(response["choices"]) > 0:
                choice = response["choices"][0]
                message = choice.get("message", {})
                
                return {
                    "success": True,
                    "content": message.get("content", ""),
                    "role": message.get("role", "assistant"),
                    "finish_reason": choice.get("finish_reason", "unknown"),
                    "usage": response.get("usage", {}),
                    "model": response.get("model", ""),
                    "created": response.get("created", 0)
                }
            else:
                return {
                    "success": False,
                    "error": "响应格式错误"
                }
                
        except Exception as e:
            logger.error(f"解析API响应异常: {str(e)}")
            return {
                "success": False,
                "error": f"解析响应失败: {str(e)}"
            }
    
    @classmethod
    async def _handle_stream_response(cls, response) -> Optional[Dict[str, Any]]:
        """
        处理流式响应
        
        Args:
            response: HTTP响应对象
            
        Returns:
            流式响应结果
        """
        try:
            full_content = ""
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # 移除 "data: " 前缀
                    
                    if data.strip() == "[DONE]":
                        break
                    
                    try:
                        chunk_data = json.loads(data)
                        if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                            choice = chunk_data["choices"][0]
                            if "delta" in choice and "content" in choice["delta"]:
                                content = choice["delta"]["content"]
                                full_content += content
                    except json.JSONDecodeError:
                        continue
            
            return {
                "success": True,
                "content": full_content,
                "role": "assistant",
                "finish_reason": "stop",
                "model": "streaming",
                "created": int(datetime.utcnow().timestamp())
            }
            
        except Exception as e:
            logger.error(f"处理流式响应异常: {str(e)}")
            return {
                "success": False,
                "error": f"处理流式响应失败: {str(e)}"
            }
    
    @classmethod
    async def stream_chat_completion(
        cls,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        流式聊天完成
        
        Args:
            messages: 对话消息列表
            model: 模型名称
            max_tokens: 最大生成token数
            temperature: 温度参数
            **kwargs: 其他参数
            
        Returns:
            流式响应结果
        """
        return await cls.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            **kwargs
        )
    
    @classmethod
    async def stream_chat_with_character(
        cls,
        user_message: str,
        character_name: str,
        character_personality: str = None,
        conversation_history: List[Dict[str, str]] = None,
        **kwargs
    ) -> Optional[str]:
        """
        流式与AI角色对话
        
        Args:
            user_message: 用户消息
            character_name: 角色名称
            character_personality: 角色性格描述
            conversation_history: 对话历史
            **kwargs: 其他参数
            
        Returns:
            AI角色流式回复或None（如果失败）
        """
        try:
            # 构建角色系统提示词
            system_prompt = f"你是{character_name}，"
            if character_personality:
                system_prompt += f"具有以下性格特点：{character_personality}。"
            system_prompt += "请以这个角色的身份和用户对话，保持角色的一致性。"
            
            # 构建消息列表
            messages = []
            
            # 添加系统提示词
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
            # 添加对话历史
            if conversation_history:
                messages.extend(conversation_history)
            
            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 调用流式API
            result = await cls.stream_chat_completion(messages, **kwargs)
            
            if result and result.get("success") and "content" in result:
                return result["content"]
            else:
                return None
                
        except Exception as e:
            logger.error(f"流式角色对话调用异常: {str(e)}")
            return None
