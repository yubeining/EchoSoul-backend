# 集成架构使用指南

## 📋 概述

原有的WebSocket接口 `/ai-chat/{user_id}` 现在支持通过 `use_enhanced` 参数来选择使用基础版或增强版架构。这种设计确保了向后兼容性，同时提供了新架构的强大功能。

## 🔌 WebSocket端点

### 基础版架构（默认）
```
ws://localhost:8000/ai-chat/{user_id}
```

### 增强版架构
```
ws://localhost:8000/ai-chat/{user_id}?use_enhanced=true
```

## 📝 使用示例

### JavaScript示例

#### 基础版架构
```javascript
// 连接到基础版WebSocket
const ws = new WebSocket('ws://localhost:8000/ai-chat/123');

ws.onopen = function() {
    console.log('基础版架构连接已建立');
    
    // 发送ping消息
    ws.send(JSON.stringify({
        type: 'ping'
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到响应:', data);
};

ws.onclose = function() {
    console.log('连接已关闭');
};
```

#### 增强版架构
```javascript
// 连接到增强版WebSocket
const ws = new WebSocket('ws://localhost:8000/ai-chat/123?use_enhanced=true');

ws.onopen = function() {
    console.log('增强版架构连接已建立');
    
    // 发送ping消息
    ws.send(JSON.stringify({
        type: 'ping'
    }));
    
    // 获取用户状态（增强版特有功能）
    ws.send(JSON.stringify({
        type: 'get_user_state',
        conversation_id: 'conv_001'
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到响应:', data);
    
    // 处理不同类型的响应
    if (data.type === 'response') {
        const result = data.result;
        if (result.success) {
            console.log('操作成功:', result);
        } else {
            console.error('操作失败:', result.error);
        }
    }
};

ws.onclose = function() {
    console.log('连接已关闭');
};
```

### Python示例

#### 基础版架构
```python
import asyncio
import json
import websockets

async def basic_chat():
    uri = "ws://localhost:8000/ai-chat/123"
    
    async with websockets.connect(uri) as websocket:
        print("基础版架构连接已建立")
        
        # 发送ping消息
        message = {"type": "ping"}
        await websocket.send(json.dumps(message))
        
        # 接收响应
        response = await websocket.recv()
        data = json.loads(response)
        print("收到响应:", data)

# 运行
asyncio.run(basic_chat())
```

#### 增强版架构
```python
import asyncio
import json
import websockets

async def enhanced_chat():
    uri = "ws://localhost:8000/ai-chat/123?use_enhanced=true"
    
    async with websockets.connect(uri) as websocket:
        print("增强版架构连接已建立")
        
        # 发送ping消息
        message = {"type": "ping"}
        await websocket.send(json.dumps(message))
        
        # 接收响应
        response = await websocket.recv()
        data = json.loads(response)
        print("收到ping响应:", data)
        
        # 获取用户状态（增强版特有功能）
        state_message = {
            "type": "get_user_state",
            "conversation_id": "conv_001"
        }
        await websocket.send(json.dumps(state_message))
        
        # 接收状态响应
        state_response = await websocket.recv()
        state_data = json.loads(state_response)
        print("收到状态响应:", state_data)

# 运行
asyncio.run(enhanced_chat())
```

## 📊 消息类型对比

### 基础版支持的消息类型
- `start_ai_session` - 开始AI会话
- `end_ai_session` - 结束AI会话
- `chat_message` - 发送聊天消息
- `get_conversation_history` - 获取对话历史
- `get_ai_characters` - 获取AI角色列表
- `ping` - 心跳检测

### 增强版支持的消息类型
- **基础版所有消息类型**（完全兼容）
- `get_user_state` - 获取用户状态
- `update_user_preferences` - 更新用户偏好
- `switch_ai_character` - 切换AI角色

## 🔄 迁移指南

### 从基础版迁移到增强版

1. **修改WebSocket连接URL**
   ```javascript
   // 原来
   const ws = new WebSocket('ws://localhost:8000/ai-chat/123');
   
   // 现在
   const ws = new WebSocket('ws://localhost:8000/ai-chat/123?use_enhanced=true');
   ```

2. **现有代码无需修改**
   - 所有原有的消息类型和格式保持不变
   - 原有的处理逻辑完全兼容

3. **享受新功能**
   - 可以使用新增的消息类型
   - 享受六维状态管理和智能决策功能
   - 获得更好的AI对话体验

## 📡 REST API端点

### 架构信息
```
GET /ai-chat/architecture-info
```
获取架构信息和使用指南

### 统计信息
```
GET /ai-chat/stats
```
获取基础版和增强版的统计信息

### 健康检查
```
GET /ai-chat/health
```
检查基础版和增强版的健康状态

### 增强版专用健康检查
```
GET /ai-chat-enhanced/health
```
仅检查增强版的健康状态

## 🧪 测试验证

### 运行集成测试
```bash
cd /home/devbox/project
python test_integrated_architecture.py
```

### 测试内容
- 基础版架构功能测试
- 增强版架构功能测试
- API端点测试
- 兼容性测试

## 🔧 配置和部署

### 环境要求
- Python 3.8+
- FastAPI
- WebSocket支持
- 数据库连接（增强版需要）

### 启动服务器
```bash
cd /home/devbox/project
python app/main.py
```

### 验证部署
```bash
# 检查服务器状态
curl http://localhost:8000/ai-chat/health

# 获取架构信息
curl http://localhost:8000/ai-chat/architecture-info
```

## 🎯 最佳实践

### 1. 渐进式迁移
- 先在测试环境使用增强版架构
- 验证功能正常后再迁移生产环境
- 保留基础版作为备用方案

### 2. 错误处理
```javascript
ws.onerror = function(error) {
    console.error('WebSocket错误:', error);
    // 可以尝试重新连接或降级到基础版
};

ws.onclose = function(event) {
    console.log('连接关闭:', event.code, event.reason);
    // 根据错误码决定是否重连
};
```

### 3. 性能监控
- 定期检查 `/ai-chat/stats` 端点
- 监控连接数和响应时间
- 使用 `/ai-chat/health` 进行健康检查

### 4. 功能选择
- **基础版**: 适合简单的AI对话需求
- **增强版**: 适合需要状态管理、智能决策的复杂场景

## 🚀 高级功能

### 增强版特有功能

#### 1. 六维状态管理
- 角色认知维度
- 交互动态维度
- 表达规则维度
- 能力权限维度
- 环境场景维度
- 动态调整维度

#### 2. 智能决策引擎
- 基于规则的决策系统
- 多种决策类型支持
- 自适应决策策略

#### 3. 统一流程处理
- 标准化的输入处理流程
- 模块化的组件设计
- 可扩展的架构

#### 4. LangGraph流程控制
- 智能对话流程控制
- 多节点流程管理
- 错误恢复机制

## 📞 支持和反馈

如果在使用过程中遇到问题：

1. 检查服务器日志
2. 运行健康检查API
3. 查看架构信息API
4. 参考测试脚本进行验证

---

**版本**: v1.0.0  
**更新时间**: 2024-12-19  
**兼容性**: 完全向后兼容
