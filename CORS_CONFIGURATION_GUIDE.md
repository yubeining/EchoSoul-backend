# CORS跨域配置指南

## 📋 概述

本文档详细说明EchoSoul AI Platform的CORS（跨域资源共享）配置，包括当前设置、支持的域名、请求方法和头部信息。

## 🔧 当前CORS配置

### 基本配置
- **允许的源域名**: `*` (所有域名)
- **允许的凭据**: `true`
- **最大缓存时间**: `86400` 秒 (24小时)

### 允许的HTTP方法
```javascript
[
    "GET",      // 获取数据
    "POST",     // 创建数据
    "PUT",      // 更新数据
    "DELETE",   // 删除数据
    "OPTIONS"   // 预检请求
]
```

### 允许的请求头
```javascript
[
    "Content-Type",     // 内容类型
    "Authorization",    // 认证令牌
    "X-Requested-With", // AJAX请求标识
    "Accept",          // 接受的内容类型
    "Origin"           // 请求来源
]
```

## 🌐 支持的域名

### 当前配置
**所有域名都被允许访问API接口**，包括：

- ✅ `http://localhost:*` - 本地开发环境
- ✅ `https://echosoul.com` - 生产域名
- ✅ `https://cedezmdpgixn.sealosbja.site` - Sealos部署域名
- ✅ `https://ohciuodbxwdp.sealosbja.site` - Sealos部署域名
- ✅ `https://your-domain.com` - 任何其他域名
- ✅ `http://your-domain.com` - 任何其他域名

### 特殊说明
- **通配符配置**: 使用 `*` 允许所有域名访问
- **开发环境**: 支持所有本地端口和域名
- **生产环境**: 支持所有HTTPS和HTTP域名

## 📡 API接口访问

### 基础URL
```
https://your-backend-domain.com/api
```

### 主要API端点
```
# 认证相关
POST /api/auth/login          # 用户登录
POST /api/auth/register       # 用户注册
GET  /api/auth/user/info      # 获取用户信息
POST /api/auth/refresh        # 刷新令牌

# AI角色管理
GET  /api/ai/characters       # 获取AI角色列表
GET  /api/ai/characters/{id}  # 获取特定AI角色
POST /api/ai/characters       # 创建AI角色
PUT  /api/ai/characters/{id}  # 更新AI角色
DELETE /api/ai/characters/{id} # 删除AI角色

# 对话管理
GET  /api/chat/conversations  # 获取对话列表
GET  /api/chat/conversations/{id} # 获取特定对话
POST /api/chat/conversations  # 创建对话
GET  /api/chat/conversations/{id}/messages # 获取对话消息

# WebSocket连接
WS   /api/ws/ai-chat/{user_id} # AI聊天WebSocket
WS   /api/ws/{user_id}         # 简单WebSocket

# 用户管理
GET  /api/users/profile/{username} # 获取用户资料
PUT  /api/users/profile/{username} # 更新用户资料
```

## 🔐 认证配置

### JWT令牌
- **算法**: `HS256`
- **访问令牌过期时间**: `30` 分钟
- **刷新令牌过期时间**: `7` 天

### 请求头配置
```javascript
// 在请求头中包含认证令牌
headers: {
    'Authorization': 'Bearer your-jwt-token',
    'Content-Type': 'application/json'
}
```

## 🚀 前端集成示例

### 1. 基础HTTP请求
```javascript
// 使用fetch API
const response = await fetch('https://your-backend-domain.com/api/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-token'
    },
    credentials: 'include', // 包含凭据
    body: JSON.stringify({
        username: 'your-username',
        password: 'your-password'
    })
});

const data = await response.json();
```

### 2. Axios配置
```javascript
import axios from 'axios';

const api = axios.create({
    baseURL: 'https://your-backend-domain.com/api',
    withCredentials: true, // 自动包含凭据
    headers: {
        'Content-Type': 'application/json'
    }
});

// 请求拦截器 - 自动添加认证令牌
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// 响应拦截器 - 处理令牌刷新
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // 处理令牌过期，刷新令牌
            await refreshToken();
        }
        return Promise.reject(error);
    }
);
```

### 3. WebSocket连接
```javascript
// AI聊天WebSocket
const ws = new WebSocket('wss://your-backend-domain.com/api/ws/ai-chat/19');

ws.onopen = () => {
    console.log('WebSocket连接已建立');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
};

// 发送消息
ws.send(JSON.stringify({
    type: 'chat_message',
    content: '你好',
    conversation_id: 'your-conversation-id',
    message_type: 'text'
}));
```

## ⚠️ 安全注意事项

### 1. 生产环境建议
虽然当前配置允许所有域名访问，但在生产环境中建议：

```python
# 在config/settings.py中设置特定域名
CORS_ORIGINS = [
    "https://your-production-domain.com",
    "https://your-admin-domain.com",
    "https://your-mobile-app-domain.com"
]
```

### 2. 环境变量配置
```bash
# 开发环境
CORS_ORIGINS="http://localhost:3000,http://localhost:3001"

# 生产环境
CORS_ORIGINS="https://your-domain.com,https://admin.your-domain.com"

# 开放所有域名（当前配置）
CORS_ORIGINS="*"
```

### 3. 安全头部
服务器自动添加以下安全头部：
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'
```

## 🔧 配置修改

### 修改允许的域名
1. **环境变量方式**:
```bash
export CORS_ORIGINS="https://your-domain.com,https://another-domain.com"
```

2. **直接修改配置文件**:
```python
# config/settings.py
CORS_ORIGINS = [
    "https://your-domain.com",
    "https://another-domain.com"
]
```

### 添加自定义请求头
```python
# config/settings.py
CORS_ALLOW_HEADERS = [
    "Content-Type",
    "Authorization", 
    "X-Requested-With",
    "Accept",
    "Origin",
    "X-Custom-Header"  # 添加自定义头部
]
```

### 添加自定义HTTP方法
```python
# config/settings.py
CORS_ALLOW_METHODS = [
    "GET", "POST", "PUT", "DELETE", "OPTIONS",
    "PATCH"  # 添加PATCH方法
]
```

## 📊 监控和调试

### 1. 检查CORS配置
```bash
# 获取当前CORS配置
curl -X GET "https://your-backend-domain.com/api/security/config" \
  -H "Authorization: Bearer your-token"
```

### 2. 预检请求测试
```bash
# 测试OPTIONS请求
curl -X OPTIONS "https://your-backend-domain.com/api/auth/login" \
  -H "Origin: https://your-frontend-domain.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -v
```

### 3. 浏览器开发者工具
在浏览器开发者工具的Network标签中查看：
- **OPTIONS请求**: 预检请求的响应
- **CORS头部**: `Access-Control-Allow-*` 头部信息
- **错误信息**: CORS相关的错误提示

## 🐛 常见问题解决

### 1. CORS错误
```
Access to fetch at 'https://api.example.com' from origin 'https://frontend.example.com' 
has been blocked by CORS policy
```

**解决方案**:
- 检查域名是否在允许列表中
- 确认请求方法和头部是否被允许
- 检查服务器CORS配置

### 2. 预检请求失败
```
Response to preflight request doesn't pass access control check
```

**解决方案**:
- 确保OPTIONS方法被允许
- 检查请求头是否在允许列表中
- 确认服务器正确处理OPTIONS请求

### 3. 凭据问题
```
The value of the 'Access-Control-Allow-Credentials' header is '' 
which must be 'true'
```

**解决方案**:
- 确保`CORS_ALLOW_CREDENTIALS = True`
- 检查请求是否包含`credentials: 'include'`

## 📞 技术支持

如果在配置CORS时遇到问题，请：

1. **检查服务器日志**: 查看CORS相关的错误信息
2. **验证配置**: 使用上述测试方法验证配置
3. **联系开发团队**: 提供具体的错误信息和配置详情

---

**最后更新**: 2025-09-22  
**版本**: 1.0.0  
**维护者**: EchoSoul AI Platform Team
