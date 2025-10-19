# 《超电磁炮》多角色图状关系角色数据库设计方案

## 一、系统架构概述

### 核心设计理念
- **分层结构化存储**：基础信息、对话上下文、关系网络三层分离
- **图状关系模型**：用图数据库映射复杂的人物关系网络
- **场景驱动对话**：对话数据与具体场景、关系绑定，避免文本孤岛
- **原作还原度优先**：确保角色对话符合原作人物设定和关系逻辑

### 技术栈选择
- **关系型数据库**：MySQL/PostgreSQL（存储结构化基础数据）
- **图数据库**：Neo4j（存储人物关系网络）
- **搜索引擎**：Elasticsearch（对话内容检索和语义搜索）
- **缓存层**：Redis（高频查询缓存）

## 二、三层数据库架构设计

### 1. 人物基础层（Character Basic Layer）

#### 1.1 核心表结构

```sql
-- 角色基础信息表
CREATE TABLE character_basic (
    char_id VARCHAR(50) PRIMARY KEY COMMENT '角色唯一标识',
    name_cn VARCHAR(100) NOT NULL COMMENT '中文名称',
    name_jp VARCHAR(100) COMMENT '日文名称',
    name_en VARCHAR(100) COMMENT '英文名称',
    identity JSON COMMENT '身份标签数组',
    personality JSON COMMENT '性格特征数组',
    speech_feature JSON COMMENT '语言特征数组',
    appearance JSON COMMENT '外貌描述',
    abilities JSON COMMENT '能力设定',
    background TEXT COMMENT '背景故事',
    icon_path VARCHAR(255) COMMENT '头像路径',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色基础信息表';

-- 角色能力等级表
CREATE TABLE character_abilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    char_id VARCHAR(50) NOT NULL,
    ability_type ENUM('esper', 'physical', 'intelligence', 'social') NOT NULL,
    level INT NOT NULL DEFAULT 0 COMMENT '能力等级(0-5)',
    description TEXT COMMENT '能力描述',
    manifestation TEXT COMMENT '能力表现方式',
    FOREIGN KEY (char_id) REFERENCES character_basic(char_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色能力等级表';
```

#### 1.2 示例数据插入

```sql
-- 御坂美琴基础信息
INSERT INTO character_basic VALUES (
    'misaka_mikoto',
    '御坂美琴',
    'みさか みこと',
    'Misaka Mikoto',
    '["常盘台中学2年级", "Level 5超能力者", "电击使", "学园都市第三位"]',
    '["傲娇", "正义感强", "讨厌被摸头", "对朋友很温柔", "容易害羞"]',
    '["结尾偶尔带"嘛"", "吐槽时会"哈？"", "激动时会说"你这家伙"", "避免柔弱表达", "生气时会放电"]',
    '{"hair": "茶色短发", "eyes": "茶色", "height": "161cm", "build": "纤细"}',
    '["电击使", "电磁力操控", "铁砂之剑", "超电磁炮"]',
    '学园都市仅有的七名Level 5超能力者之一，排名第三位。就读于常盘台中学，是白井黑子的室友。',
    '/static/char/misaka_mikoto.png',
    NOW(),
    NOW()
);

-- 白井黑子基础信息
INSERT INTO character_basic VALUES (
    'shirai_kuroko',
    '白井黑子',
    'しらい くろこ',
    'Shirai Kuroko',
    '["风纪委员177支部", "Level 4空间移动能力者", "美琴的室友", "常盘台中学1年级"]',
    '["忠犬（对美琴）", "毒舌（对他人）", "严谨（执行任务）", "喜欢用敬称", "对美琴有特殊感情"]',
    '["称呼美琴为"美琴大人"", "执行任务说"风纪委员在此"", "撒娇时拖长音", "瞬移前会说"空间移动"", "对美琴用敬语"]',
    '{"hair": "双马尾", "eyes": "茶色", "height": "152cm", "build": "娇小"}',
    '["空间移动", "Level 4能力者", "风纪委员技能"]',
    '常盘台中学1年级学生，风纪委员177支部成员，御坂美琴的室友。对美琴有着强烈的崇拜和特殊感情。',
    '/static/char/shirai_kuroko.png',
    NOW(),
    NOW()
);

-- 初春饰利基础信息
INSERT INTO character_basic VALUES (
    'hatsuharu_kurisu',
    '初春饰利',
    'はつはる かざり',
    'Hatsuharu Kazari',
    '["风纪委员177支部", "Level 1分析能力者", "栅川中学学生", "信息处理专家"]',
    '["内向", "技术宅", "对美琴有敬畏", "认真负责", "容易紧张"]',
    '["称呼美琴为"美琴学姐"", "说话比较正式", "紧张时会结巴", "技术术语较多"]',
    '{"hair": "黑色短发", "eyes": "黑色", "height": "156cm", "build": "普通"}',
    '["Level 1分析能力", "计算机技术", "信息处理"]',
    '栅川中学学生，风纪委员177支部成员，主要负责信息处理工作。对御坂美琴有着敬畏之情。',
    '/static/char/hatsuharu_kurisu.png',
    NOW(),
    NOW()
);

-- 佐天泪子基础信息
INSERT INTO character_basic VALUES (
    'satake_kozoe',
    '佐天泪子',
    'さたけ るいこ',
    'Satake Ruiko',
    '["无能力者", "栅川中学学生", "初春的好友", "Level 0"]',
    '["开朗", "好奇心强", "喜欢都市传说", "对能力者感兴趣", "乐观积极"]',
    '["说话比较随意", "喜欢用"诶"开头", "对超能力很感兴趣", "语气比较轻松"]',
    '{"hair": "黑色长发", "eyes": "黑色", "height": "158cm", "build": "普通"}',
    '["无特殊能力", "Level 0", "普通学生"]',
    '栅川中学学生，初春饰利的好友。虽然是Level 0无能力者，但对学园都市的超能力现象很感兴趣。',
    '/static/char/satake_kozoe.png',
    NOW(),
    NOW()
);
```

### 2. 对话场景层（Dialogue Scene Layer）

#### 2.1 核心表结构

```sql
-- 场景信息表
CREATE TABLE scene_info (
    scene_id VARCHAR(50) PRIMARY KEY COMMENT '场景唯一标识',
    scene_name VARCHAR(100) NOT NULL COMMENT '场景名称',
    scene_type ENUM('dormitory', 'school', 'office', 'street', 'cafe', 'other') NOT NULL COMMENT '场景类型',
    description TEXT COMMENT '场景详细描述',
    atmosphere JSON COMMENT '场景氛围标签',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='场景信息表';

-- 对话场景表
CREATE TABLE dialogue_scene (
    dialogue_id VARCHAR(50) PRIMARY KEY COMMENT '对话唯一标识',
    scene_id VARCHAR(50) NOT NULL COMMENT '场景ID',
    participants JSON NOT NULL COMMENT '参与角色ID数组',
    dialogue_turn JSON NOT NULL COMMENT '对话轮次数据',
    emotion_tag JSON COMMENT '情绪标签',
    context_summary TEXT COMMENT '对话上下文摘要',
    source VARCHAR(255) COMMENT '数据来源',
    episode_info JSON COMMENT '剧集信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scene_id) REFERENCES scene_info(scene_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话场景表';

-- 对话轮次表（用于复杂查询）
CREATE TABLE dialogue_turns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dialogue_id VARCHAR(50) NOT NULL,
    turn_num INT NOT NULL,
    speaker_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    action_desc TEXT COMMENT '动作描述',
    emotion VARCHAR(50) COMMENT '情绪标签',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dialogue_id) REFERENCES dialogue_scene(dialogue_id) ON DELETE CASCADE,
    FOREIGN KEY (speaker_id) REFERENCES character_basic(char_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话轮次表';
```

#### 2.2 场景数据插入

```sql
-- 插入场景信息
INSERT INTO scene_info VALUES 
('dormitory_misaka_room', '美琴宿舍', 'dormitory', '常盘台中学宿舍，美琴和黑子的房间。书桌、床铺、衣柜等家具齐全，墙上贴着一些海报。', '["温馨", "日常", "私密"]', NOW()),
('wind_judgment_office', '风纪委员办公室', 'office', '风纪委员177支部的办公室，有办公桌、电脑、文件柜等办公设备。', '["严肃", "工作", "正式"]', NOW()),
('school_corridor', '学校走廊', 'school', '常盘台中学的走廊，连接各个教室和办公室。', '["校园", "日常", "社交"]', NOW()),
('street_shopping', '商业街', 'street', '学园都市的商业街，有各种商店和餐厅，人来人往。', '["热闹", "购物", "休闲"]', NOW());
```

#### 2.3 对话数据示例

```sql
-- 美琴和黑子的宿舍对话
INSERT INTO dialogue_scene VALUES (
    's01_e03_d05',
    'dormitory_misaka_room',
    '["misaka_mikoto", "shirai_kuroko"]',
    '[
        {
            "turn_num": 1,
            "speaker_id": "shirai_kuroko",
            "content": "美琴大人～我带了便利店刚买的草莓大福，要一起吃吗？",
            "action": "瞬移到美琴身后，递出包装袋，眼睛亮晶晶",
            "emotion": "兴奋"
        },
        {
            "turn_num": 2,
            "speaker_id": "misaka_mikoto",
            "content": "哈？你又没敲门就瞬移进来了——还有，别用那种称呼叫我啊！",
            "action": "手顿了一下，回头瞪黑子，耳朵尖有点红",
            "emotion": "无奈+轻微羞恼"
        },
        {
            "turn_num": 3,
            "speaker_id": "shirai_kuroko",
            "content": "可是美琴大人的房间就是我的房间嘛～而且大福要趁新鲜吃哦～",
            "action": "凑近美琴，把大福递到她嘴边",
            "emotion": "撒娇"
        },
        {
            "turn_num": 4,
            "speaker_id": "misaka_mikoto",
            "content": "真是的...不过既然你买了，那就一起吃吧。但是下次要敲门！",
            "action": "接过大福，脸上带着无奈的笑容",
            "emotion": "妥协+温柔"
        }
    ]',
    '["misaka:无奈转温柔", "kuroko:兴奋转撒娇"]',
    '美琴在宿舍写作业时，黑子瞬移进来分享零食的日常对话',
    '番剧S1E3 05:20-06:10',
    '{"season": 1, "episode": 3, "time_range": "05:20-06:10"}',
    NOW()
);
```

### 3. 关系网络层（Relationship Network Layer）

#### 3.1 Neo4j图数据库设计

```cypher
// 创建角色节点
CREATE (misaka:Character {
    char_id: "misaka_mikoto",
    name_cn: "御坂美琴",
    identity: ["Level 5电击使", "常盘台2年级"],
    personality: ["傲娇", "正义感强"],
    created_at: datetime()
})

CREATE (kuroko:Character {
    char_id: "shirai_kuroko", 
    name_cn: "白井黑子",
    identity: ["Level 4空间移动", "风纪委员"],
    personality: ["忠犬", "毒舌"],
    created_at: datetime()
})

CREATE (hatsuharu:Character {
    char_id: "hatsuharu_kurisu",
    name_cn: "初春饰利", 
    identity: ["Level 1分析能力", "风纪委员"],
    personality: ["内向", "技术宅"],
    created_at: datetime()
})

CREATE (satake:Character {
    char_id: "satake_kozoe",
    name_cn: "佐天泪子",
    identity: ["无能力者", "栅川中学学生"],
    personality: ["开朗", "好奇心强"],
    created_at: datetime()
});

// 创建关系（带属性）
CREATE (kuroko)-[:ADMIRER {
    intensity: 10,
    speech_rule: ["必须叫美琴大人", "撒娇语气", "提空间移动"],
    typical_scene: ["美琴宿舍", "风纪委员办公室", "街头抓违规"],
    taboo: ["不能说美琴平胸", "不能擅自碰美琴的东西"],
    relationship_desc: "黑子对美琴的崇拜和特殊感情",
    created_at: datetime()
}]->(misaka)

CREATE (kuroko)-[:ROOMMATE {
    intensity: 9,
    speech_rule: ["日常吐槽", "提醒校规", "关心生活"],
    typical_scene: ["宿舍", "学校"],
    taboo: ["不能过度干涉私生活"],
    relationship_desc: "室友关系，日常相处",
    created_at: datetime()
}]->(misaka)

CREATE (kuroko)-[:COLLEAGUE {
    intensity: 8,
    speech_rule: ["严肃执行任务", "称呼初春", "工作配合"],
    typical_scene: ["风纪委员办公室", "执行任务现场"],
    taboo: ["不能在工作时开玩笑"],
    relationship_desc: "风纪委员同事关系",
    created_at: datetime()
}]->(hatsuharu)

CREATE (misaka)-[:FRIEND {
    intensity: 7,
    speech_rule: ["随意吐槽", "帮她解围", "平等交流"],
    typical_scene: ["街头", "学校", "咖啡厅"],
    taboo: ["不能因为能力差异而歧视"],
    relationship_desc: "朋友关系，互相帮助",
    created_at: datetime()
}]->(satake)

CREATE (hatsuharu)-[:SENIOR_JUNIOR {
    intensity: 6,
    speech_rule: ["敬畏称呼美琴学姐", "求助时语气软", "保持距离"],
    typical_scene: ["学校", "风纪委员办公室"],
    taboo: ["不能过于随意"],
    relationship_desc: "学姐学妹关系，初春对美琴的敬畏",
    created_at: datetime()
}]->(misaka)

CREATE (hatsuharu)-[:BEST_FRIEND {
    intensity: 9,
    speech_rule: ["亲密称呼", "互相支持", "分享秘密"],
    typical_scene: ["学校", "咖啡厅", "宿舍"],
    taboo: ["不能背叛信任"],
    relationship_desc: "最好的朋友关系",
    created_at: datetime()
}]->(satake);
```

## 三、数据查询和API设计

### 3.1 核心查询接口

```python
# 查询角色关系规则
def get_character_relationship_rules(char_id_1, char_id_2):
    """
    获取两个角色之间的所有关系规则
    """
    query = """
    MATCH (c1:Character {char_id: $char_id_1})-[r]-(c2:Character {char_id: $char_id_2})
    RETURN r.speech_rule, r.taboo, r.typical_scene, r.intensity, r.relationship_desc
    """
    return neo4j_session.run(query, char_id_1=char_id_1, char_id_2=char_id_2)

# 查询角色的所有关系
def get_character_all_relationships(char_id):
    """
    获取某个角色的所有关系
    """
    query = """
    MATCH (c:Character {char_id: $char_id})-[r]-(other:Character)
    RETURN other.char_id, other.name_cn, r.speech_rule, r.intensity, 
           type(r) as relationship_type
    ORDER BY r.intensity DESC
    """
    return neo4j_session.run(query, char_id=char_id)

# 查询场景相关对话
def get_scene_dialogues(scene_id, participants=None):
    """
    查询特定场景的对话数据
    """
    if participants:
        query = """
        SELECT * FROM dialogue_scene 
        WHERE scene_id = %s AND JSON_CONTAINS(participants, %s)
        ORDER BY created_at DESC
        """
        return mysql_cursor.execute(query, (scene_id, json.dumps(participants)))
    else:
        query = """
        SELECT * FROM dialogue_scene 
        WHERE scene_id = %s 
        ORDER BY created_at DESC
        """
        return mysql_cursor.execute(query, (scene_id,))
```

### 3.2 对话生成辅助查询

```python
def get_dialogue_context(char_id_1, char_id_2, scene_type=None):
    """
    获取对话生成所需的上下文信息
    """
    # 1. 获取角色基础信息
    char_info = get_character_basic_info([char_id_1, char_id_2])
    
    # 2. 获取关系规则
    relationship_rules = get_character_relationship_rules(char_id_1, char_id_2)
    
    # 3. 获取相似场景的对话示例
    similar_dialogues = get_similar_dialogues(char_id_1, char_id_2, scene_type)
    
    return {
        'characters': char_info,
        'relationship_rules': relationship_rules,
        'dialogue_examples': similar_dialogues
    }
```

## 四、数据采集和标注流程

### 4.1 数据采集策略

1. **原作对话提取**
   - 从动画、漫画、小说中提取完整对话
   - 记录场景、参与者、情绪、动作描述
   - 标注数据来源（第几季第几集，时间范围）

2. **关系标注**
   - 分析角色间的互动模式
   - 标注关系类型和强度
   - 提取对话规则和禁忌

3. **场景分类**
   - 按场景类型分类（宿舍、学校、办公室等）
   - 标注场景氛围和特点
   - 关联典型对话模式

### 4.2 质量控制

1. **原作还原度检查**
   - 对比原作对话，确保角色语言特征一致
   - 验证关系设定符合原作逻辑
   - 检查场景描述准确性

2. **数据完整性验证**
   - 确保所有角色都有基础信息
   - 验证关系网络的连通性
   - 检查对话数据的完整性

## 五、部署和运维

### 5.1 数据库部署

```yaml
# docker-compose.yml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: railgun_chars
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql

  neo4j:
    image: neo4j:4.4
    environment:
      NEO4J_AUTH: neo4j/password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  elasticsearch:
    image: elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data

  redis:
    image: redis:6.2
    ports:
      - "6379:6379"

volumes:
  mysql_data:
  neo4j_data:
  es_data:
```

### 5.2 数据同步策略

```python
# 数据同步脚本
def sync_character_data():
    """
    同步角色基础数据到各个数据库
    """
    # 1. 从MySQL读取角色基础信息
    characters = get_all_characters_from_mysql()
    
    # 2. 同步到Neo4j
    for char in characters:
        create_or_update_character_node(char)
    
    # 3. 同步到Elasticsearch
    index_characters_to_elasticsearch(characters)

def sync_dialogue_data():
    """
    同步对话数据到Elasticsearch
    """
    dialogues = get_all_dialogues_from_mysql()
    index_dialogues_to_elasticsearch(dialogues)
```

## 六、扩展和维护

### 6.1 数据扩展

1. **新角色添加**
   - 在character_basic表中添加基础信息
   - 在Neo4j中创建节点和关系
   - 更新相关对话数据

2. **新关系类型**
   - 在Neo4j中定义新的关系类型
   - 更新查询接口和业务逻辑
   - 重新标注相关对话数据

### 6.2 性能优化

1. **索引优化**
   - 为常用查询字段创建索引
   - 优化Neo4j查询语句
   - 使用Elasticsearch进行全文搜索

2. **缓存策略**
   - 缓存频繁查询的关系数据
   - 缓存角色基础信息
   - 使用Redis进行会话缓存

这个设计方案实现了您要求的"分层结构化存储"和"图状关系模型"，能够有效支持《超电磁炮》角色的对话生成，确保原作还原度和后续调用的灵活性。
