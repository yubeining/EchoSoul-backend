# EchoSoul AI Platform 用户认证接口文档

## 📋 接口概览

**基础URL**: `http://localhost:8080`  
**API版本**: v1.0.0  
**认证方式**: JWT Bearer Token  
**数据格式**: JSON  

## 🔐 用户认证接口

### 1. 用户注册

#### 1.1 基本信息
- **请求路径**: `/api/auth/register`
- **请求方式**: `POST`
- **接口描述**: 用户注册接口，支持手机号和邮箱注册
- **是否需要认证**: 否

#### 1.2 请求参数

**Content-Type**: `application/json`

| 参数名 | 类型 | 是否必须 | 长度限制 | 备注 |
|--------|------|----------|----------|------|
| mobileOrEmail | string | 必须 | - | 手机号或邮箱地址 |
| password | string | 必须 | 6-20位 | 密码 |
| confirmPassword | string | 必须 | 6-20位 | 确认密码 |
| nickname | string | 非必须 | 最大50字符 | 用户昵称 |

**请求参数示例**:
```json
{
    "mobileOrEmail": "13800138000",
    "password": "123456",
    "confirmPassword": "123456",
    "nickname": "张三"
}
```

#### 1.3 响应数据

**成功响应** (HTTP 200):
```json
{
    "code": 1,
    "msg": "注册成功",
    "data": {
        "userId": 1,
        "username": "user_13800138000",
        "nickname": "张三"
    }
}
```

**失败响应** (HTTP 400):
```json
{
    "detail": "手机号已存在"
}
```

#### 1.4 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| 1005 | 400 | 用户名已存在 |
| 1006 | 400 | 邮箱已存在 |
| 1007 | 400 | 手机号已存在 |
| 1008 | 400 | 密码强度不符合要求 |
| 1001 | 400 | 参数错误 |

---

### 2. 用户登录

#### 2.1 基本信息
- **请求路径**: `/api/auth/login`
- **请求方式**: `POST`
- **接口描述**: 用户登录接口，支持用户名/邮箱/手机号登录
- **是否需要认证**: 否

#### 2.2 请求参数

**Content-Type**: `application/json`

| 参数名 | 类型 | 是否必须 | 备注 |
|--------|------|----------|------|
| username | string | 必须 | 用户名/邮箱/手机号 |
| password | string | 必须 | 密码 |

**请求参数示例**:
```json
{
    "username": "13800138000",
    "password": "123456"
}
```

#### 2.3 响应数据

**成功响应** (HTTP 200):
```json
{
    "code": 1,
    "msg": "登录成功",
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU4MjM0NDg5fQ.MlX6-qN7bHvmAI3kgZN1d0QPHjm_j_1JOiAaOH9QTSM",
        "userInfo": {
            "id": 1,
            "username": "user_13800138000",
            "email": null,
            "mobile": "13800138000",
            "nickname": "张三",
            "avatar": null,
            "status": 1,
            "lastLoginTime": "2025-09-18T21:58:09",
            "createTime": "2025-09-18T21:58:05"
        },
        "isNewUser": false
    }
}
```

**失败响应** (HTTP 401):
```json
{
    "detail": "用户名或密码错误"
}
```

#### 2.4 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| 1002 | 401 | 用户名或密码错误 |
| 1003 | 401 | 用户不存在 |
| 1004 | 401 | 用户已被禁用 |

---

### 3. 获取用户信息

#### 3.1 基本信息
- **请求路径**: `/api/auth/user/info`
- **请求方式**: `GET`
- **接口描述**: 获取当前登录用户的详细信息
- **是否需要认证**: 是

#### 3.2 请求参数

**Header参数**:
| 参数名 | 类型 | 是否必须 | 备注 |
|--------|------|----------|------|
| Authorization | string | 必须 | Bearer token |

**请求示例**:
```bash
curl -X GET "http://localhost:8080/api/auth/user/info" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### 3.3 响应数据

**成功响应** (HTTP 200):
```json
{
    "code": 1,
    "msg": "success",
    "data": {
        "id": 1,
        "username": "user_13800138000",
        "email": null,
        "mobile": "13800138000",
        "nickname": "张三",
        "avatar": null,
        "status": 1,
        "lastLoginTime": "2025-09-18T21:58:09",
        "createTime": "2025-09-18T21:58:05"
    }
}
```

**失败响应** (HTTP 401):
```json
{
    "detail": "Could not validate credentials"
}
```

---

### 4. 修改用户资料

#### 4.1 基本信息
- **请求路径**: `/api/auth/user/profile`
- **请求方式**: `PUT`
- **接口描述**: 修改用户个人信息
- **是否需要认证**: 是

#### 4.2 请求参数

**Content-Type**: `application/json`

| 参数名 | 类型 | 是否必须 | 备注 |
|--------|------|----------|------|
| nickname | string | 非必须 | 昵称 |
| avatar | string | 非必须 | 头像URL |

**请求参数示例**:
```json
{
    "nickname": "新昵称",
    "avatar": "https://example.com/avatar.jpg"
}
```

#### 4.3 响应数据

**成功响应** (HTTP 200):
```json
{
    "code": 1,
    "msg": "修改成功",
    "data": null
}
```

---

### 5. 修改密码

#### 5.1 基本信息
- **请求路径**: `/api/auth/user/password`
- **请求方式**: `PUT`
- **接口描述**: 修改用户密码
- **是否需要认证**: 是

#### 5.2 请求参数

**Content-Type**: `application/json`

| 参数名 | 类型 | 是否必须 | 备注 |
|--------|------|----------|------|
| oldPassword | string | 必须 | 原密码 |
| newPassword | string | 必须 | 新密码 |
| confirmPassword | string | 必须 | 确认新密码 |

**请求参数示例**:
```json
{
    "oldPassword": "123456",
    "newPassword": "new123456",
    "confirmPassword": "new123456"
}
```

#### 5.3 响应数据

**成功响应** (HTTP 200):
```json
{
    "code": 1,
    "msg": "密码修改成功",
    "data": null
}
```

**失败响应** (HTTP 400):
```json
{
    "detail": "原密码错误"
}
```

---

### 6. 刷新Token

#### 6.1 基本信息
- **请求路径**: `/api/auth/refresh`
- **请求方式**: `POST`
- **接口描述**: 刷新JWT令牌
- **是否需要认证**: 是

#### 6.2 请求参数

**Header参数**:
| 参数名 | 类型 | 是否必须 | 备注 |
|--------|------|----------|------|
| Authorization | string | 必须 | Bearer token |

#### 6.3 响应数据

**成功响应** (HTTP 200):
```json
{
    "code": 1,
    "msg": "刷新成功",
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

---

### 7. 用户登出

#### 7.1 基本信息
- **请求路径**: `/api/auth/logout`
- **请求方式**: `POST`
- **接口描述**: 用户登出
- **是否需要认证**: 是

#### 7.2 请求参数

**Header参数**:
| 参数名 | 类型 | 是否必须 | 备注 |
|--------|------|----------|------|
| Authorization | string | 必须 | Bearer token |

#### 7.3 响应数据

**成功响应** (HTTP 200):
```json
{
    "code": 1,
    "msg": "登出成功",
    "data": null
}
```

---

### 8. 第三方登录

#### 8.1 基本信息
- **请求路径**: `/api/auth/oauth/login`
- **请求方式**: `POST`
- **接口描述**: 第三方登录（微信、QQ、微博）
- **是否需要认证**: 否

#### 8.2 请求参数

**Content-Type**: `application/json`

| 参数名 | 类型 | 是否必须 | 备注 |
|--------|------|----------|------|
| oauthType | string | 必须 | 第三方类型: wechat, qq, weibo |
| oauthCode | string | 必须 | 第三方授权码 |
| oauthState | string | 非必须 | 状态参数 |

**请求参数示例**:
```json
{
    "oauthType": "wechat",
    "oauthCode": "wx_auth_code_123456",
    "oauthState": "state_123"
}
```

#### 8.3 响应数据

**成功响应** (HTTP 200):
```json
{
    "code": 1,
    "msg": "登录成功",
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "userInfo": {
            "id": 1,
            "username": "user_wechat_123456",
            "nickname": "微信用户",
            "avatar": "https://wx.qlogo.cn/..."
        },
        "isNewUser": false
    }
}
```

---

## 🧪 测试数据

### 已创建的测试用户

| 用户ID | 用户名 | 邮箱/手机 | 密码 | 昵称 | 状态 |
|--------|--------|-----------|------|------|------|
| 7 | user_admin | admin@echosoul.com | admin123 | 管理员 | 正常 |
| 8 | user_demo | demo@echosoul.com | demo123 | 演示用户 | 正常 |
| 9 | user_18612345678 | 18612345678 | test123 | 测试用户 | 正常 |

### 测试用例

#### 1. 注册测试
```bash
# 手机号注册
curl -X POST "http://localhost:8080/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "mobileOrEmail": "13900139000",
    "password": "123456",
    "confirmPassword": "123456",
    "nickname": "测试用户"
  }'

# 邮箱注册
curl -X POST "http://localhost:8080/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "mobileOrEmail": "test@example.com",
    "password": "123456",
    "confirmPassword": "123456",
    "nickname": "邮箱用户"
  }'
```

#### 2. 登录测试
```bash
# 使用邮箱登录
curl -X POST "http://localhost:8080/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@echosoul.com",
    "password": "admin123"
  }'

# 使用手机号登录
curl -X POST "http://localhost:8080/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "18612345678",
    "password": "test123"
  }'
```

#### 3. 获取用户信息测试
```bash
# 先登录获取token
TOKEN=$(curl -s -X POST "http://localhost:8080/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@echosoul.com", "password": "admin123"}' | \
  python -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")

# 使用token获取用户信息
curl -X GET "http://localhost:8080/api/auth/user/info" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔧 前端集成指南

### 1. 环境配置
```javascript
const API_BASE_URL = 'http://localhost:8080';
const API_ENDPOINTS = {
  register: '/api/auth/register',
  login: '/api/auth/login',
  userInfo: '/api/auth/user/info',
  updateProfile: '/api/auth/user/profile',
  changePassword: '/api/auth/user/password',
  refresh: '/api/auth/refresh',
  logout: '/api/auth/logout',
  oauthLogin: '/api/auth/oauth/login'
};
```

### 2. 请求封装示例
```javascript
// 通用请求函数
async function apiRequest(endpoint, method = 'GET', data = null, token = null) {
  const config = {
    method,
    headers: {
      'Content-Type': 'application/json',
    }
  };
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  if (data) {
    config.body = JSON.stringify(data);
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  return await response.json();
}

// 用户注册
async function register(mobileOrEmail, password, confirmPassword, nickname) {
  return await apiRequest(API_ENDPOINTS.register, 'POST', {
    mobileOrEmail,
    password,
    confirmPassword,
    nickname
  });
}

// 用户登录
async function login(username, password) {
  return await apiRequest(API_ENDPOINTS.login, 'POST', {
    username,
    password
  });
}

// 获取用户信息
async function getUserInfo(token) {
  return await apiRequest(API_ENDPOINTS.userInfo, 'GET', null, token);
}
```

### 3. Token管理
```javascript
// Token存储
const TOKEN_KEY = 'echosoul_token';

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function removeToken() {
  localStorage.removeItem(TOKEN_KEY);
}

// 自动刷新Token
async function refreshToken() {
  const token = getToken();
  if (!token) return null;
  
  try {
    const response = await apiRequest(API_ENDPOINTS.refresh, 'POST', null, token);
    if (response.code === 1) {
      setToken(response.data.token);
      return response.data.token;
    }
  } catch (error) {
    console.error('Token刷新失败:', error);
    removeToken();
  }
  return null;
}
```

### 4. 错误处理
```javascript
function handleApiError(error) {
  const errorMessages = {
    1001: '参数错误',
    1002: '用户名或密码错误',
    1003: '用户不存在',
    1004: '用户已被禁用',
    1005: '用户名已存在',
    1006: '邮箱已存在',
    1007: '手机号已存在',
    1008: '密码强度不符合要求',
    1009: 'Token无效或已过期',
    1010: '第三方登录失败',
    1011: '原密码错误',
    1012: '新密码不能与原密码相同'
  };
  
  return errorMessages[error.code] || error.message || '未知错误';
}
```

---

## 📚 其他资源

### API文档访问
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

### 健康检查
- **健康检查**: http://localhost:8080/health
- **数据库状态**: http://localhost:8080/api/db/status

### 注意事项
1. **HTTPS**: 生产环境建议使用HTTPS协议
2. **Token过期**: JWT Token默认30分钟过期，需要及时刷新
3. **密码安全**: 密码使用bcrypt加密存储
4. **输入验证**: 所有输入参数都经过严格验证
5. **错误处理**: 建议前端实现完整的错误处理机制

---

**文档版本**: v1.0.0  
**最后更新**: 2025-09-18  
**维护团队**: EchoSoul AI Platform
