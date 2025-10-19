# EchoSoul AI Platform - 系统架构图

## 🏗️ 整体系统架构

```mermaid
graph TB
    subgraph "用户端"
        A[Web前端] --> B[移动端App]
        A --> C[桌面应用]
    end
    
    subgraph "API网关层"
        D[负载均衡器] --> E[API网关]
        E --> F[认证服务]
        E --> G[限流服务]
    end
    
    subgraph "应用服务层"
        H[FastAPI应用] --> I[统一流程处理器]
        I --> J[四层三引擎架构]
    end
    
    subgraph "四层三引擎架构"
        K[输出适配层] --> L[LangGraph流程层]
        L --> M[核心能力模块层]
        M --> N[全局状态管理层]
    end
    
    subgraph "核心能力模块"
        O[角色认知引擎] --> P[交互动态引擎]
        P --> Q[表达规则引擎]
    end
    
    subgraph "数据存储层"
        R[MySQL主数据库] --> S[Neo4j图数据库]
        S --> T[Elasticsearch搜索引擎]
        T --> U[Redis缓存]
    end
    
    subgraph "外部服务"
        V[大模型API] --> W[MinIO对象存储]
        W --> X[监控服务]
    end
    
    subgraph "实时通信"
        Y[WebSocket管理器] --> Z[AI对话处理器]
        Z --> AA[用户聊天处理器]
    end
    
    A --> D
    B --> D
    C --> D
    H --> Y
    I --> O
    J --> R
    H --> V
    Y --> H
```

## 🔄 统一流程处理架构

```mermaid
graph LR
    A[用户输入] --> B[输入解析器]
    B --> C[状态管理器]
    C --> D[模块调用]
    D --> E[决策引擎]
    E --> F[输出适配器]
    F --> G[AI响应]
    
    subgraph "状态管理"
        H[用户状态] --> I[对话状态]
        I --> J[角色状态]
        J --> K[场景状态]
    end
    
    subgraph "模块调用"
        L[角色认知引擎] --> M[交互动态引擎]
        M --> N[表达规则引擎]
    end
    
    C --> H
    D --> L
```

## 🎭 角色关系数据库架构

```mermaid
graph TB
    subgraph "MySQL关系数据库"
        A[角色基础信息表] --> B[角色关系表]
        B --> C[对话场景表]
        C --> D[场景信息表]
    end
    
    subgraph "Neo4j图数据库"
        E[角色节点] --> F[关系边]
        F --> G[关系属性]
        G --> H[对话规则]
    end
    
    subgraph "Elasticsearch搜索引擎"
        I[对话内容索引] --> J[角色信息索引]
        J --> K[场景信息索引]
    end
    
    A --> E
    B --> F
    C --> I
    D --> K
```

## 🌐 WebSocket实时通信架构

```mermaid
graph TB
    subgraph "WebSocket连接管理"
        A[连接管理器] --> B[AI对话管理器]
        A --> C[用户聊天管理器]
    end
    
    subgraph "消息处理流程"
        D[消息接收] --> E[消息解析]
        E --> F[权限验证]
        F --> G[业务处理]
        G --> H[响应发送]
    end
    
    subgraph "流式处理"
        I[流式开始] --> J[流式数据块]
        J --> K[流式结束]
    end
    
    B --> D
    C --> D
    G --> I
```

## 📊 数据流架构

```mermaid
graph LR
    A[用户输入] --> B[API接口]
    B --> C[业务逻辑层]
    C --> D[数据访问层]
    D --> E[MySQL数据库]
    D --> F[Neo4j图数据库]
    D --> G[Redis缓存]
    D --> H[Elasticsearch]
    
    I[大模型API] --> C
    J[MinIO存储] --> C
    
    E --> K[数据同步服务]
    F --> K
    K --> L[数据一致性检查]
```

## 🔧 部署架构

```mermaid
graph TB
    subgraph "Docker容器"
        A[FastAPI应用容器] --> B[MySQL容器]
        A --> C[Redis容器]
        A --> D[Neo4j容器]
        A --> E[Elasticsearch容器]
    end
    
    subgraph "Kubernetes集群"
        F[应用Pod] --> G[数据库Pod]
        G --> H[缓存Pod]
        H --> I[搜索引擎Pod]
    end
    
    subgraph "监控和日志"
        J[Prometheus监控] --> K[Grafana仪表板]
        K --> L[ELK日志系统]
    end
    
    A --> F
    F --> J
```

## 🎯 核心组件交互图

```mermaid
sequenceDiagram
    participant U as 用户
    participant W as WebSocket
    participant F as 流程处理器
    participant C as 角色认知引擎
    participant I as 交互动态引擎
    participant E as 表达规则引擎
    participant L as 大模型服务
    participant D as 数据库
    
    U->>W: 发送消息
    W->>F: 处理用户输入
    F->>C: 分析角色上下文
    C->>D: 查询角色信息
    D-->>C: 返回角色数据
    C->>I: 处理交互动态
    I->>D: 查询关系规则
    D-->>I: 返回关系数据
    I->>E: 应用表达规则
    E->>L: 调用大模型
    L-->>E: 返回AI回复
    E-->>F: 返回最终响应
    F-->>W: 流式发送回复
    W-->>U: 显示AI回复
```

## 📈 性能优化架构

```mermaid
graph TB
    subgraph "缓存层"
        A[Redis缓存] --> B[内存缓存]
        B --> C[CDN缓存]
    end
    
    subgraph "负载均衡"
        D[负载均衡器] --> E[应用实例1]
        D --> F[应用实例2]
        D --> G[应用实例3]
    end
    
    subgraph "数据库优化"
        H[主数据库] --> I[从数据库]
        I --> J[读写分离]
    end
    
    subgraph "异步处理"
        K[消息队列] --> L[后台任务]
        L --> M[定时任务]
    end
    
    A --> D
    D --> H
    H --> K
```

这个架构图展示了EchoSoul AI Platform的完整系统设计，包括：

1. **整体系统架构**：从用户端到数据存储层的完整架构
2. **统一流程处理架构**：核心的AI对话处理流程
3. **角色关系数据库架构**：多数据库协同的存储架构
4. **WebSocket实时通信架构**：实时通信的处理流程
5. **数据流架构**：数据在系统中的流转过程
6. **部署架构**：容器化和集群部署方案
7. **核心组件交互图**：关键组件的交互时序
8. **性能优化架构**：系统性能优化的各个层面

每个架构图都清晰地展示了系统的不同方面，帮助理解整个系统的设计和实现方案。
