<!--
Sync Impact Report:
Version change: N/A → 1.0.0
Modified principles: N/A (new constitution)
Added sections: Technology Stack Requirements, Development Workflow
Removed sections: N/A
Templates requiring updates:
  ✅ .specify/templates/plan-template.md (constitution check alignment)
  ✅ .specify/templates/spec-template.md (API-first requirements)
  ✅ .specify/templates/tasks-template.md (TDD enforcement)
  ⚠️ README.md (runtime guidance update pending)
Follow-up TODOs: Update README.md with constitution compliance guidance
-->

# EchoSoul AI Platform Constitution

## Core Principles

### I. API-First Architecture
所有功能必须通过RESTful API暴露；API设计遵循OpenAPI 3.0规范；每个端点必须有完整的文档和示例；API版本控制采用语义化版本管理；所有API响应必须包含适当的HTTP状态码和错误信息。

### II. Test-Driven Development (NON-NEGOTIABLE)
TDD强制要求：测试编写 → 用户批准 → 测试失败 → 然后实现；红-绿-重构循环严格执行；所有新功能必须包含单元测试、集成测试和API测试；测试覆盖率必须达到80%以上；所有测试必须在CI/CD流水线中通过。

### III. Security by Design
所有用户输入必须经过验证和清理；JWT认证是强制性的；所有API端点必须进行身份验证和授权检查；敏感数据必须加密存储；定期进行安全审计和漏洞扫描。

### IV. Performance & Scalability
API响应时间必须小于200ms（P95）；支持水平扩展；数据库查询必须优化；实现连接池和资源管理；监控系统性能和资源使用情况。

### V. Observability & Monitoring
所有服务必须实现结构化日志记录；关键操作必须记录审计日志；实现健康检查端点；监控系统指标和业务指标；错误必须被捕获、记录和报告；实现分布式追踪。

## Technology Stack Requirements

### Core Framework
- **FastAPI**: 主要Web框架，版本 >= 0.104.1
- **SQLAlchemy**: ORM框架，版本 >= 2.0.23
- **Pydantic**: 数据验证，版本 >= 2.5.0
- **Uvicorn**: ASGI服务器，版本 >= 0.24.0

### Database & Storage
- **MySQL**: 主数据库，版本 >= 8.0 本地、测试、生产环境都使用该数据库
  - 主机: `echosoul-mysql-mysql.ns-7rdhhsv1.svc` (生产环境)
  - 端口: `3306`
  - 用户: `root`
  - 密码: `kzmtbc6b`
  - 数据库名: `EchoSoul`
  - 连接字符串: `mysql+pymysql://root:kzmtbc6b@echosoul-mysql-mysql.ns-7rdhhsv1.svc:3306/EchoSoul`
  - 字符集: `utf8mb4`
  - 排序规则: `utf8mb4_unicode_ci`
- **Redis**: 缓存和会话存储，版本 >= 6.0 本地、测试、生产环境都使用该数据库
  - 主机: `echosoul-redis-redis.ns-7rdhhsv1.svc` (生产环境)
  - 端口: `6379`
  - 用户名: `default`
  - 密码: `ppdqrfdk`
  - 数据库: `0`
  - 连接字符串: `redis://default:ppdqrfdk@echosoul-redis-redis.ns-7rdhhsv1.svc:6379/0`
- **MinIO**: 对象存储服务，版本 >= 7.2.0

### Security & Authentication
- **JWT**: 身份认证令牌
- **bcrypt**: 密码加密
- **CORS**: 跨域资源共享配置

## Development Workflow

### Code Quality Standards
- 所有代码必须通过linting检查（flake8, black, mypy）
- 代码审查是强制性的，至少需要一名高级开发者批准
- 所有提交必须包含清晰的提交信息
- 使用类型提示和文档字符串

### Deployment & Operations
- 支持Docker容器化部署
- 使用环境变量进行配置管理
- 实现蓝绿部署策略
- 所有部署必须通过自动化测试

### Environment Configuration
- **生产环境**: https://ohciuodbxwdp.sealosbja.site (生产部署地址)
- **测试环境**: https://glbbvnrguhix.sealosbja.site (测试部署地址)
- **本地开发环境**: http://localhost:8080 (基于entrypoint.sh和README.md)
 

### Database Environment Variables
- `MYSQL_HOST`: MySQL服务器地址
- `MYSQL_PORT`: MySQL端口 (默认: 3306)
- `MYSQL_USER`: MySQL用户名 (默认: root)
- `MYSQL_PASSWORD`: MySQL密码
- `MYSQL_DATABASE`: 数据库名称 (默认: EchoSoul)
- `DB_POOL_SIZE`: 连接池大小 (默认: 10)
- `DB_MAX_OVERFLOW`: 最大溢出连接数 (默认: 20)
- `DB_POOL_RECYCLE`: 连接回收时间 (默认: 3600秒)
- `REDIS_HOST`: Redis服务器地址
- `REDIS_PORT`: Redis端口 (默认: 6379)
- `REDIS_USERNAME`: Redis用户名 (默认: default)
- `REDIS_PASSWORD`: Redis密码
- `REDIS_DB`: Redis数据库编号 (默认: 0)

### Documentation Requirements
- API文档必须保持最新
- 所有公共接口必须有文档字符串
- 部署和运维文档必须完整
- 架构决策必须记录在ADR中

## Governance

本宪法超越所有其他实践；所有PR/审查必须验证合规性；复杂性必须被证明合理；使用README.md进行运行时开发指导；所有团队成员必须遵守这些原则；违反原则的代码不得合并到主分支。

**Version**: 1.0.0 | **Ratified**: 2024-10-02 | **Last Amended**: 2024-10-02