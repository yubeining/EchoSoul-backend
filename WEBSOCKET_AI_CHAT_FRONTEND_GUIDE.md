# WebSocket AI聊天接口前端调用指南

## 📋 概述

本文档详细说明前端如何调用WebSocket AI聊天接口，包括连接建立、会话管理、消息发送等完整流程。

## 🔌 连接建立

### 连接URL
```
ws://localhost:8080/api/ws/ai-chat/{user_id}
```

**参数说明：**
- `user_id`: 用户ID（整数）

**示例：**
```javascript
const userId = 19;
const wsUrl = `ws://localhost:8080/api/ws/ai-chat/${userId}`;
const websocket = new WebSocket(wsUrl);
```

### 连接状态处理
```javascript
websocket.onopen = function(event) {
    console.log('WebSocket连接已建立');
};

websocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
};

websocket.onerror = function(error) {
    console.error('WebSocket错误:', error);
};

websocket.onclose = function(event) {
    console.log('WebSocket连接已关闭');
};
```

## 📨 消息格式规范

### 1. 开始AI会话

**发送消息：**
```javascript
const startSessionMessage = {
    type: "start_ai_session",
    ai_character_id: "char_jva1t0fu"  // AI角色ID
};

websocket.send(JSON.stringify(startSessionMessage));
```

**响应格式：**
```json
// 第一个响应：会话开始确认
{
    "type": "ai_session_started",
    "ai_character_id": "char_jva1t0fu",
    "message": "AI会话已开始",
    "timestamp": "2025-09-22T15:50:38.707259Z"
}

// 第二个响应：会话创建结果
{
    "type": "response",
    "original_type": "start_ai_session",
    "result": {
        "success": true,
        "conversation_id": "da3f90e9-0b0f-4ca9-86e7-0a09b62a36e7",
        "ai_character": {
            "character_id": "char_jva1t0fu",
            "nickname": "Alice",
            "description": "一个温柔善良的AI助手",
            "personality": "温柔、耐心、善解人意"
        }
    }
}
```

### 2. 发送聊天消息

**发送消息：**
```javascript
const chatMessage = {
    type: "chat_message",
    content: "你好，我想和你聊天",
    conversation_id: "da3f90e9-0b0f-4ca9-86e7-0a09b62a36e7",  // 从开始会话响应中获取
    message_type: "text"
};

websocket.send(JSON.stringify(chatMessage));
```

**响应格式：**
```json
// 用户消息确认
{
    "type": "user_message_sent",
    "message_id": "e3b26237-9cba-4236-8e28-84b08d39a5b7",
    "content": "你好，我想和你聊天",
    "timestamp": "2025-09-22T15:50:38.715399Z"
}

// 消息处理结果
{
    "type": "response",
    "original_type": "chat_message",
    "result": {
        "success": true,
        "message_id": "e3b26237-9cba-4236-8e28-84b08d39a5b7",
        "conversation_id": "da3f90e9-0b0f-4ca9-86e7-0a09b62a36e7",
        "ai_processing": true
    }
}
```

### 3. 获取AI角色列表

**发送消息：**
```javascript
const getCharactersMessage = {
    type: "get_ai_characters"
};

websocket.send(JSON.stringify(getCharactersMessage));
```

**响应格式：**
```json
{
    "type": "response",
    "original_type": "get_ai_characters",
    "result": {
        "success": true,
        "ai_characters": [
            {
                "character_id": "char_jva1t0fu",
                "nickname": "Alice",
                "description": "一个温柔善良的AI助手",
                "personality": "温柔、耐心、善解人意",
                "speaking_style": "自然",
                "usage_count": 15
            }
        ]
    }
}
```

### 4. 获取会话历史

**发送消息：**
```javascript
const getHistoryMessage = {
    type: "get_conversation_history",
    conversation_id: "da3f90e9-0b0f-4ca9-86e7-0a09b62a36e7",
    limit: 20  // 可选，默认20条
};

websocket.send(JSON.stringify(getHistoryMessage));
```

### 5. 结束AI会话

**发送消息：**
```javascript
const endSessionMessage = {
    type: "end_ai_session"
};

websocket.send(JSON.stringify(endSessionMessage));
```

### 6. Ping测试

**发送消息：**
```javascript
const pingMessage = {
    type: "ping"
};

websocket.send(JSON.stringify(pingMessage));
```

## ⚠️ 重要注意事项

### 1. 会话流程要求
- **必须先开始AI会话**：发送聊天消息前，必须先调用`start_ai_session`
- **会话ID获取**：从`start_ai_session`的响应中获取`conversation_id`
- **会话状态检查**：确保AI会话处于活跃状态

### 2. 消息发送顺序
```javascript
// 正确的调用顺序
1. 建立WebSocket连接
2. 等待连接确认消息
3. 发送 start_ai_session
4. 等待会话创建成功
5. 发送 chat_message
6. 处理AI回复
```

### 3. 错误处理
```javascript
// 常见错误响应
{
    "type": "response",
    "result": {
        "success": false,
        "error": "没有活跃的AI会话"  // 或其他错误信息
    }
}
```

**常见错误：**
- `"没有活跃的AI会话"`: 需要先调用`start_ai_session`
- `"会话不存在或无权限"`: 会话ID无效或用户无权限
- `"AI角色不存在"`: AI角色ID无效
- `"消息内容过长"`: 消息超过10000字符限制

### 4. 消息字段要求

**必需字段：**
- `type`: 消息类型（字符串）
- `content`: 消息内容（字符串，最大10000字符）
- `conversation_id`: 会话ID（字符串，从开始会话响应获取）
- `message_type`: 消息类型（字符串，通常为"text"）

**可选字段：**
- `ai_character_id`: AI角色ID（仅在开始会话时需要）
- `limit`: 历史消息数量限制（仅在获取历史时需要）

### 5. 连接管理
```javascript
// 连接状态检查
if (websocket.readyState === WebSocket.OPEN) {
    // 发送消息
    websocket.send(JSON.stringify(message));
} else {
    console.error('WebSocket连接未建立');
}

// 重连机制
function reconnect() {
    setTimeout(() => {
        websocket = new WebSocket(wsUrl);
        setupWebSocketHandlers();
    }, 3000);
}
```

## 🔄 完整示例代码

```javascript
class AIChatWebSocket {
    constructor(userId) {
        this.userId = userId;
        this.wsUrl = `ws://localhost:8080/api/ws/ai-chat/${userId}`;
        this.websocket = null;
        this.conversationId = null;
        this.isSessionActive = false;
    }

    connect() {
        this.websocket = new WebSocket(this.wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket连接已建立');
        };

        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.websocket.onerror = (error) => {
            console.error('WebSocket错误:', error);
        };

        this.websocket.onclose = () => {
            console.log('WebSocket连接已关闭');
            this.isSessionActive = false;
        };
    }

    handleMessage(data) {
        switch (data.type) {
            case 'connection_established':
                console.log('连接确认:', data.message);
                break;
            
            case 'ai_session_started':
                console.log('AI会话开始确认');
                break;
            
            case 'response':
                if (data.original_type === 'start_ai_session' && data.result.success) {
                    this.conversationId = data.result.conversation_id;
                    this.isSessionActive = true;
                    console.log('会话创建成功:', this.conversationId);
                }
                break;
            
            case 'user_message_sent':
                console.log('用户消息已发送:', data.message_id);
                break;
            
            case 'ai_message':
                console.log('AI回复:', data.content);
                break;
        }
    }

    startAISession(aiCharacterId) {
        if (this.websocket.readyState !== WebSocket.OPEN) {
            console.error('WebSocket连接未建立');
            return;
        }

        const message = {
            type: "start_ai_session",
            ai_character_id: aiCharacterId
        };

        this.websocket.send(JSON.stringify(message));
    }

    sendMessage(content) {
        if (!this.isSessionActive || !this.conversationId) {
            console.error('AI会话未激活或会话ID无效');
            return;
        }

        if (this.websocket.readyState !== WebSocket.OPEN) {
            console.error('WebSocket连接未建立');
            return;
        }

        const message = {
            type: "chat_message",
            content: content,
            conversation_id: this.conversationId,
            message_type: "text"
        };

        this.websocket.send(JSON.stringify(message));
    }

    endSession() {
        if (this.websocket.readyState !== WebSocket.OPEN) {
            return;
        }

        const message = {
            type: "end_ai_session"
        };

        this.websocket.send(JSON.stringify(message));
        this.isSessionActive = false;
        this.conversationId = null;
    }

    disconnect() {
        if (this.websocket) {
            this.websocket.close();
        }
    }
}

// 使用示例
const aiChat = new AIChatWebSocket(19);
aiChat.connect();

// 开始AI会话
aiChat.startAISession('char_jva1t0fu');

// 发送消息
aiChat.sendMessage('你好，我想和你聊天');

// 结束会话
aiChat.endSession();
```

## 📊 状态码说明

| 状态 | 说明 |
|------|------|
| `connection_established` | WebSocket连接已建立 |
| `ai_session_started` | AI会话开始确认 |
| `user_message_sent` | 用户消息发送确认 |
| `ai_message` | AI回复消息 |
| `response` | 通用响应消息 |
| `error` | 错误消息 |

## 🚀 最佳实践

1. **连接管理**: 实现自动重连机制
2. **状态跟踪**: 维护会话状态和会话ID
3. **错误处理**: 处理所有可能的错误情况
4. **消息队列**: 在连接断开时缓存消息
5. **用户体验**: 提供连接状态指示器
6. **性能优化**: 避免频繁的连接建立和断开

## 🔧 调试建议

1. **日志记录**: 记录所有发送和接收的消息
2. **状态检查**: 定期检查连接和会话状态
3. **错误监控**: 监控并处理所有错误响应
4. **测试环境**: 在测试环境中验证所有功能

---

**注意**: 请确保在生产环境中使用HTTPS和WSS协议，并实现适当的认证和授权机制。
