# CORS跨域配置快速参考

## 🚀 当前配置状态

⚠️ **重要更新**: 由于启用了 `credentials: 'include'`，**不能使用通配符 `*`**

✅ **已配置具体域名访问API接口**

## 📡 基础配置

### 允许的源域名
```
http://localhost:3000
https://cedezmdpgixn.sealosbja.site
```

### 允许的HTTP方法
```
GET, POST, PUT, DELETE, OPTIONS
```

### 允许的请求头
```
Content-Type, Authorization, X-Requested-With, Accept, Origin
```

### 凭据支持
```
✅ 支持 (withCredentials: true)
```

## 🔗 API基础URL

```
https://your-backend-domain.com/api
```

## 📝 前端请求示例

### 1. Fetch API
```javascript
fetch('https://your-backend-domain.com/api/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-token'
    },
    credentials: 'include',
    body: JSON.stringify({ username: 'user', password: 'pass' })
});
```

### 2. Axios配置
```javascript
const api = axios.create({
    baseURL: 'https://your-backend-domain.com/api',
    withCredentials: true
});
```

### 3. WebSocket连接
```javascript
const ws = new WebSocket('wss://your-backend-domain.com/api/ws/ai-chat/19');
```

## ⚠️ 重要提醒

**🚨 CORS安全限制**: 当 `allow_credentials=True` 时，浏览器**不允许**使用通配符 `*`

- ❌ **不能使用**: `Access-Control-Allow-Origin: *`
- ✅ **必须明确指定**: 具体的域名列表
- ✅ **开发环境**: 需要明确指定 `http://localhost:3000` 等
- ✅ **生产环境**: 需要明确指定 `https://your-domain.com`

## 🔧 配置允许的域名

### 方法1: 修改环境变量 (推荐)
```bash
export CORS_ORIGINS="https://your-domain.com,https://another-domain.com,http://localhost:3000"
```

### 方法2: 修改 `config/settings.py`
```python
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://your-domain.com,http://localhost:3000").split(",")
```

### 方法3: Docker环境变量
```bash
docker run -e CORS_ORIGINS="https://your-domain.com,http://localhost:3000" your-app
```

---

**当前状态**: 已配置具体域名，支持凭据传递  
**最后更新**: 2025-01-27  
**重要**: 当 `credentials: 'include'` 时，必须明确指定域名，不能使用通配符 `*`
