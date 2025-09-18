# EchoSoul-backend
EchoSoul AI Platform Backend Service

## 项目描述

这是一个基于Python的HTTP服务器应用程序，演示了基本的服务器功能。该项目使用Python内置的`http.server`模块创建一个基本的HTTP服务器，监听8080端口并在访问时返回"Hello World!"消息。

## 环境要求

该项目运行在Debian 12系统上，Python已预配置在Devbox环境中。您无需担心自己设置Python或系统依赖项，开发环境包含了构建和运行Python应用程序所需的所有必要工具。如果您需要根据特定要求进行调整，可以相应地修改配置文件。

## 项目执行

**开发模式：** 对于正常的开发环境，只需进入Devbox并在终端中运行`bash entrypoint.sh`。

**生产模式：** 发布后，项目将根据`entrypoint.sh`脚本自动打包成Docker镜像并部署。

## 技术栈

- Python 3.11
- HTTP Server
- Docker (生产环境)

DevBox: Code. Build. Deploy. We've Got the Rest.

通过DevBox，您可以完全专注于编写优秀的代码，而我们负责基础设施、扩展和部署。从开发到生产的无缝体验。
