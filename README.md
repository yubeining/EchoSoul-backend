# EchoSoul AI Platform Backend

## 📢 项目状态
- **版本**: v2.0.0 (优化版)
- **状态**: ✅ 生产就绪
- **架构**: 🚀 已重构优化

## 🚀 项目概述

EchoSoul AI Platform 是一个基于 FastAPI 构建的现代化 AI 平台后端服务，提供用户认证、用户搜索、聊天系统、对象存储等核心功能。

**版本**: v2.0.0 (优化版)  
**状态**: ✅ 生产就绪  
**性能**: 🚀 已优化

## 🏗️ 技术架构

### 核心技术栈
- **FastAPI** - 现代、快速的 Web 框架
- **SQLAlchemy** - Python ORM
- **MySQL** - 主数据库
- **Redis** - 缓存和会话存储
- **MinIO** - 对象存储服务
- **JWT** - 身份认证
- **Uvicorn** - ASGI 服务器

### 项目结构
```
echosoul-backend/
├── app/                    # 应用核心代码
│   ├── api/               # API 路由
│   ├── core/              # 核心功能模块
│   ├── db/                # 数据库连接
│   ├── middleware/        # 中间件
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic 模式
│   ├── services/          # 业务逻辑
│   └── websocket/         # WebSocket处理
├── config/                 # 配置文件
├── docs/                   # 项目文档
└── requirements.txt        # 依赖管理
```

详细结构请查看 [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)

## 🔧 快速开始

### 环境要求
- Python 3.11+
- MySQL 8.0+
- Redis 6.0+

### 安装依赖
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量
```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=EchoSoul

# JWT 配置
JWT_SECRET_KEY=your-jwt-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 配置
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

### 启动服务
```bash
# 开发环境
python app/main.py

# 生产环境
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 📚 API 文档

详细的API文档请查看 `docs/` 目录：
- [聊天系统API文档](docs/CHAT_API_DOCUMENTATION.md)
- [聊天系统前端集成指南](docs/CHAT_FRONTEND_GUIDE.md)
- [CORS配置文档](docs/CORS_CONFIGURATION.md)

### 核心 API 端点

#### 🔐 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/user/info` - 获取用户信息
- `PUT /api/auth/user/profile` - 更新用户资料
- `PUT /api/auth/user/password` - 修改密码

#### 👥 用户管理
- `GET /api/users/search` - 用户搜索
- `GET /api/users/profile/{uid}` - 获取用户详情

#### 💬 聊天系统
- `POST /api/chat/conversations/get-or-create` - 获取或创建会话
- `GET /api/chat/conversations` - 获取会话列表
- `POST /api/chat/messages` - 发送消息
- `GET /api/chat/conversations/{id}/messages` - 获取消息列表

#### 🗄️ 数据库管理
- `GET /api/db/status` - 数据库状态
- `GET /api/db/status/all` - 所有数据库状态

#### 📊 系统监控
- `GET /api/stats/overview` - 系统概览
- `GET /api/stats/users` - 用户统计
- `GET /api/health` - 健康检查

#### 🗂️ 对象存储
- `POST /api/storage/upload` - 文件上传
- `POST /api/storage/upload/avatar` - 头像上传
- `GET /api/storage/files` - 文件列表
- `GET /api/storage/status` - 存储状态

### API 文档访问
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## 🔒 安全特性

- **JWT 认证** - 安全的用户身份验证
- **密码加密** - 使用 bcrypt 加密存储
- **CORS 支持** - 跨域请求安全配置
- **API 限流** - 防止恶意请求
- **输入验证** - 严格的数据验证和清理

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -t echosoul-backend .

# 运行容器
docker run -p 8080:8080 \
  -e MYSQL_HOST=your-mysql-host \
  -e MYSQL_PASSWORD=your-password \
  echosoul-backend
```

## 🧪 测试

```bash
# 运行测试
python -m pytest tests/

# 测试特定模块
python -m pytest tests/test_auth.py
```

## 📈 监控和日志

- **健康检查**: `GET /api/health`
- **系统统计**: `GET /api/stats/overview`
- **日志文件**: `logs/` 目录

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题或建议，请：
- 提交 [Issue](https://github.com/your-repo/issues)
- 联系开发团队

---

**EchoSoul AI Platform** - 构建下一代 AI 应用 🚀
