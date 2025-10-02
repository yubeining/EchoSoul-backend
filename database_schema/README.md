# 《超电磁炮》多角色图状关系角色数据库

## 项目概述

这是一个专为《某科学的超电磁炮》设计的**多角色图状关系角色数据库**，采用分层结构化存储和图状关系模型，旨在打破"单角色文本孤岛"，构建"人物-对话-关系-场景"的关联网络。

### 核心特性

- **分层结构化存储**：基础信息、对话上下文、关系网络三层分离
- **图状关系模型**：用Neo4j图数据库映射复杂的人物关系网络
- **场景驱动对话**：对话数据与具体场景、关系绑定，避免文本孤岛
- **原作还原度优先**：确保角色对话符合原作人物设定和关系逻辑

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   人物基础层     │    │   对话场景层     │    │   关系网络层     │
│   (MySQL)       │    │   (MySQL+ES)    │    │   (Neo4j)       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • 角色基础信息   │    │ • 场景信息       │    │ • 人物关系网络   │
│ • 性格特征       │    │ • 对话轮次       │    │ • 关系属性       │
│ • 语言特征       │    │ • 情绪标签       │    │ • 互动模式       │
│ • 能力设定       │    │ • 上下文摘要     │    │ • 对话规则       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   应用接口层     │
                    │   (Flask API)   │
                    ├─────────────────┤
                    │ • 角色查询       │
                    │ • 关系分析       │
                    │ • 对话生成       │
                    │ • 场景检索       │
                    └─────────────────┘
```

## 文件结构

```
database_schema/
├── README.md                           # 项目说明文档
├── 01_character_basic.sql              # 人物基础层数据库结构
├── 02_dialogue_scene.sql               # 对话场景层数据库结构
├── 03_neo4j_relationships.cypher       # 关系网络层图数据库结构
├── 04_query_examples.py                # 查询示例和API接口
├── 05_deployment_guide.md              # 部署指南
└── railgun_character_database_design.md # 详细设计方案
```

## 快速开始

### 1. 环境要求

- **MySQL 8.0+**
- **Neo4j 4.4+**
- **Elasticsearch 7.15+**
- **Redis 6.2+**
- **Python 3.8+**

### 2. 快速部署（Docker）

```bash
# 克隆项目
git clone <repository-url>
cd railgun-database

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 3. 手动部署

```bash
# 1. 导入MySQL数据
mysql -u root -p < 01_character_basic.sql
mysql -u root -p < 02_dialogue_scene.sql

# 2. 导入Neo4j数据
cypher-shell -u neo4j -p password -f 03_neo4j_relationships.cypher

# 3. 运行Python示例
python 04_query_examples.py
```

## 数据库设计

### 1. 人物基础层

存储角色的基础信息，包括：
- 角色身份和背景
- 性格特征标签
- 语言特征模式
- 能力设定描述

**核心表**：
- `character_basic` - 角色基础信息
- `character_abilities` - 角色能力等级
- `character_tags` - 角色标签索引

### 2. 对话场景层

存储多角色互动的对话数据，包括：
- 场景上下文信息
- 完整对话轮次
- 情绪和动作描述
- 数据来源标注

**核心表**：
- `scene_info` - 场景信息
- `dialogue_scene` - 对话场景
- `dialogue_turns` - 对话轮次
- `dialogue_relationships` - 对话关系

### 3. 关系网络层

使用Neo4j图数据库存储人物关系网络，包括：
- 人物节点和关系边
- 关系类型和强度
- 对话规则和禁忌
- 互动模式描述

**核心元素**：
- `Character` 节点 - 角色信息
- 关系类型：`ADMIRER`, `ROOMMATE`, `COLLEAGUE`, `FRIEND`, `SENIOR_JUNIOR`, `BEST_FRIEND`
- 关系属性：`intensity`, `speech_rule`, `taboo`, `typical_scene`

## 主要角色

### 御坂美琴 (misaka_mikoto)
- **身份**：Level 5电击使，常盘台中学2年级
- **性格**：傲娇，正义感强，对朋友温柔
- **语言特征**：结尾带"嘛"，吐槽时说"哈？"

### 白井黑子 (shirai_kuroko)
- **身份**：Level 4空间移动，风纪委员，美琴的室友
- **性格**：对美琴忠犬，对他人毒舌
- **语言特征**：称呼美琴为"美琴大人"，撒娇时拖长音

### 初春饰利 (hatsuharu_kurisu)
- **身份**：Level 1分析能力，风纪委员，栅川中学学生
- **性格**：内向，技术宅，对美琴有敬畏
- **语言特征**：称呼美琴为"美琴学姐"，说话正式

### 佐天泪子 (satake_kozoe)
- **身份**：Level 0无能力者，栅川中学学生
- **性格**：开朗，好奇心强，喜欢都市传说
- **语言特征**：说话随意，喜欢用"诶"开头

## 核心关系

### 黑子 → 美琴
- **ADMIRER** (强度: 10) - 崇拜关系
- **ROOMMATE** (强度: 9) - 室友关系
- **语言规则**：必须叫"美琴大人"，撒娇语气
- **禁忌**：不能说美琴"平胸"，不能擅自碰美琴的东西

### 初春 → 美琴
- **SENIOR_JUNIOR** (强度: 6) - 学姐学妹关系
- **语言规则**：敬畏称呼"美琴学姐"，求助时语气软
- **禁忌**：不能过于随意，不能质疑学姐

### 初春 ↔ 佐天
- **BEST_FRIEND** (强度: 9) - 最好的朋友关系
- **语言规则**：亲密称呼，互相支持，分享秘密
- **禁忌**：不能背叛信任，不能忽视对方

## API接口

### 角色查询
```python
# 获取角色基础信息
GET /api/characters/{char_id}

# 获取角色关系
GET /api/characters/{char_id}/relationships
```

### 对话生成
```python
# 获取对话上下文
POST /api/dialogue/context
{
    "char_id_1": "misaka_mikoto",
    "char_id_2": "shirai_kuroko",
    "scene_type": "dormitory"
}

# 获取对话建议
POST /api/dialogue/suggestions
{
    "char_id_1": "misaka_mikoto",
    "char_id_2": "shirai_kuroko",
    "scene_type": "dormitory"
}
```

### 搜索分析
```python
# 搜索对话内容
GET /api/search/dialogues?q=美琴大人&limit=10

# 关系网络分析
GET /api/analysis/network
```

## 使用示例

### 1. 查询角色关系
```python
from database_schema.query_examples import RailgunCharacterDatabase

db = RailgunCharacterDatabase(mysql_config, neo4j_config, es_config)

# 获取黑子和美琴的关系
relationships = db.get_relationship_rules('shirai_kuroko', 'misaka_mikoto')
for rel in relationships:
    print(f"关系类型: {rel['relationship_type']}")
    print(f"语言规则: {rel['speech_rule']}")
    print(f"禁忌: {rel['taboo']}")
```

### 2. 生成对话建议
```python
# 获取对话上下文
context = db.get_dialogue_context('misaka_mikoto', 'shirai_kuroko', 'dormitory')

# 生成对话建议
suggestions = db.generate_dialogue_suggestions('misaka_mikoto', 'shirai_kuroko', 'dormitory')
```

### 3. 关系网络分析
```python
# 获取关系网络分析
analysis = db.get_relationship_network_analysis()
print("关系类型统计:")
for stat in analysis['relationship_stats']:
    print(f"  {stat['relationship_type']}: {stat['count']}个关系")
```

## 数据采集

### 1. 原作对话提取
- 从动画、漫画、小说中提取完整对话
- 记录场景、参与者、情绪、动作描述
- 标注数据来源（第几季第几集，时间范围）

### 2. 关系标注
- 分析角色间的互动模式
- 标注关系类型和强度
- 提取对话规则和禁忌

### 3. 质量控制
- 对比原作对话，确保角色语言特征一致
- 验证关系设定符合原作逻辑
- 检查场景描述准确性

## 扩展计划

### 1. 数据扩展
- 添加更多角色（如固法美伟、婚后光子等）
- 增加更多对话场景和关系类型
- 支持多语言版本

### 2. 功能扩展
- 对话生成AI模型集成
- 实时对话分析
- 角色关系可视化

### 3. 性能优化
- 数据库查询优化
- 缓存策略改进
- 分布式部署支持

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目链接: [https://github.com/username/railgun-database](https://github.com/username/railgun-database)
- 问题反馈: [https://github.com/username/railgun-database/issues](https://github.com/username/railgun-database/issues)

## 致谢

感谢《某科学的超电磁炮》的创作者们为我们提供了如此精彩的作品和角色设定。
