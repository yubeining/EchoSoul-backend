# EchoSoul-backend
EchoSoul AI Platform Backend Service

## 项目描述

这是一个基于FastAPI的现代Web API服务器，为EchoSoul AI平台提供后端服务。该项目使用FastAPI框架构建高性能的异步API服务，支持自动API文档生成、数据验证和类型提示。

### 主要功能
- 🚀 **FastAPI框架** - 现代、快速的Web框架
- 📚 **自动API文档** - Swagger UI和ReDoc文档
- 🔍 **健康检查** - 服务监控端点
- 🎯 **Echo服务** - 测试API功能
- 🌐 **CORS支持** - 跨域请求支持

## 环境要求

该项目运行在Debian 12系统上，Python已预配置在Devbox环境中。您无需担心自己设置Python或系统依赖项，开发环境包含了构建和运行Python应用程序所需的所有必要工具。如果您需要根据特定要求进行调整，可以相应地修改配置文件。

## 项目执行

**开发模式：** 对于正常的开发环境，只需进入Devbox并在终端中运行`bash entrypoint.sh`。

**生产模式：** 发布后，项目将根据`entrypoint.sh`脚本自动打包成Docker镜像并部署。

## API端点

- `GET /` - 主页面（HTML）
- `GET /health` - 健康检查
- `POST /echo` - Echo服务
- `GET /hello` - 简单问候
- `GET /api/info` - API信息
- `GET /docs` - Swagger UI文档
- `GET /redoc` - ReDoc文档

## 技术栈

- **Python 3.11** - 编程语言
- **FastAPI** - Web框架
- **Uvicorn** - ASGI服务器
- **Pydantic** - 数据验证
- **Docker** - 容器化部署

DevBox: Code. Build. Deploy. We've Got the Rest.

通过DevBox，您可以完全专注于编写优秀的代码，而我们负责基础设施、扩展和部署。从开发到生产的无缝体验。
