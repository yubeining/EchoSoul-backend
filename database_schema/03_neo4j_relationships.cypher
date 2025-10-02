// 《超电磁炮》角色数据库 - 关系网络层 (Neo4j)
// 创建角色节点和关系网络

// 1. 创建角色节点
CREATE (misaka:Character {
    char_id: "misaka_mikoto",
    name_cn: "御坂美琴",
    name_jp: "みさか みこと",
    name_en: "Misaka Mikoto",
    identity: ["Level 5电击使", "常盘台2年级", "学园都市第三位"],
    personality: ["傲娇", "正义感强", "讨厌被摸头", "对朋友很温柔", "容易害羞"],
    speech_feature: ["结尾偶尔带"嘛"", "吐槽时会"哈？"", "激动时会说"你这家伙"", "避免柔弱表达"],
    abilities: ["电击使", "电磁力操控", "铁砂之剑", "超电磁炮"],
    created_at: datetime()
})

CREATE (kuroko:Character {
    char_id: "shirai_kuroko", 
    name_cn: "白井黑子",
    name_jp: "しらい くろこ",
    name_en: "Shirai Kuroko",
    identity: ["Level 4空间移动", "风纪委员", "常盘台1年级"],
    personality: ["忠犬（对美琴）", "毒舌（对他人）", "严谨（执行任务）", "喜欢用敬称"],
    speech_feature: ["称呼美琴为"美琴大人"", "执行任务说"风纪委员在此"", "撒娇时拖长音", "瞬移前会说"空间移动""],
    abilities: ["空间移动", "Level 4能力者", "风纪委员技能"],
    created_at: datetime()
})

CREATE (hatsuharu:Character {
    char_id: "hatsuharu_kurisu",
    name_cn: "初春饰利", 
    name_jp: "はつはる かざり",
    name_en: "Hatsuharu Kazari",
    identity: ["Level 1分析能力", "风纪委员", "栅川中学学生"],
    personality: ["内向", "技术宅", "对美琴有敬畏", "认真负责", "容易紧张"],
    speech_feature: ["称呼美琴为"美琴学姐"", "说话比较正式", "紧张时会结巴", "技术术语较多"],
    abilities: ["Level 1分析能力", "计算机技术", "信息处理"],
    created_at: datetime()
})

CREATE (satake:Character {
    char_id: "satake_kozoe",
    name_cn: "佐天泪子",
    name_jp: "さたけ るいこ",
    name_en: "Satake Ruiko",
    identity: ["无能力者", "栅川中学学生", "Level 0"],
    personality: ["开朗", "好奇心强", "喜欢都市传说", "对能力者感兴趣", "乐观积极"],
    speech_feature: ["说话比较随意", "喜欢用"诶"开头", "对超能力很感兴趣", "语气比较轻松"],
    abilities: ["无特殊能力", "Level 0", "普通学生"],
    created_at: datetime()
})

CREATE (konori:Character {
    char_id: "konori_mii",
    name_cn: "固法美伟",
    name_jp: "このはり みい",
    name_en: "Konori Mii",
    identity: ["Level 1透视能力", "风纪委员177支部长", "常盘台3年级"],
    personality: ["成熟", "负责", "关心后辈", "工作能力强", "温柔"],
    speech_feature: ["说话比较正式", "经常关心后辈", "工作用语较多", "语气温和"],
    abilities: ["Level 1透视能力", "风纪委员管理", "格斗术"],
    created_at: datetime()
});

// 2. 创建关系（带属性）
// 黑子对美琴的崇拜关系
CREATE (kuroko)-[:ADMIRER {
    intensity: 10,
    speech_rule: ["必须叫美琴大人", "撒娇语气", "提空间移动", "用敬语"],
    typical_scene: ["美琴宿舍", "风纪委员办公室", "街头抓违规"],
    taboo: ["不能说美琴平胸", "不能擅自碰美琴的东西", "不能质疑美琴的能力"],
    relationship_desc: "黑子对美琴的崇拜和特殊感情",
    interaction_pattern: "崇拜+撒娇+保护",
    created_at: datetime()
}]->(misaka)

// 黑子和美琴的室友关系
CREATE (kuroko)-[:ROOMMATE {
    intensity: 9,
    speech_rule: ["日常吐槽", "提醒校规", "关心生活", "分享日常"],
    typical_scene: ["宿舍", "学校", "日常生活"],
    taboo: ["不能过度干涉私生活", "不能偷看日记"],
    relationship_desc: "室友关系，日常相处",
    interaction_pattern: "日常+关心+吐槽",
    created_at: datetime()
}]->(misaka)

// 黑子和初春的同事关系
CREATE (kuroko)-[:COLLEAGUE {
    intensity: 8,
    speech_rule: ["严肃执行任务", "称呼初春", "工作配合", "互相支持"],
    typical_scene: ["风纪委员办公室", "执行任务现场", "工作会议"],
    taboo: ["不能在工作时开玩笑", "不能泄露工作机密"],
    relationship_desc: "风纪委员同事关系",
    interaction_pattern: "工作+配合+支持",
    created_at: datetime()
}]->(hatsuharu)

// 美琴和佐天的朋友关系
CREATE (misaka)-[:FRIEND {
    intensity: 7,
    speech_rule: ["随意吐槽", "帮她解围", "平等交流", "互相帮助"],
    typical_scene: ["街头", "学校", "咖啡厅", "购物"],
    taboo: ["不能因为能力差异而歧视", "不能忽视她的感受"],
    relationship_desc: "朋友关系，互相帮助",
    interaction_pattern: "平等+帮助+交流",
    created_at: datetime()
}]->(satake)

// 初春对美琴的学姐学妹关系
CREATE (hatsuharu)-[:SENIOR_JUNIOR {
    intensity: 6,
    speech_rule: ["敬畏称呼美琴学姐", "求助时语气软", "保持距离", "表示尊敬"],
    typical_scene: ["学校", "风纪委员办公室", "偶遇"],
    taboo: ["不能过于随意", "不能质疑学姐"],
    relationship_desc: "学姐学妹关系，初春对美琴的敬畏",
    interaction_pattern: "敬畏+求助+尊敬",
    created_at: datetime()
}]->(misaka)

// 初春和佐天的最好朋友关系
CREATE (hatsuharu)-[:BEST_FRIEND {
    intensity: 9,
    speech_rule: ["亲密称呼", "互相支持", "分享秘密", "关心对方"],
    typical_scene: ["学校", "咖啡厅", "宿舍", "天台"],
    taboo: ["不能背叛信任", "不能忽视对方"],
    relationship_desc: "最好的朋友关系",
    interaction_pattern: "亲密+支持+分享",
    created_at: datetime()
}]->(satake)

// 固法对黑子的前辈关系
CREATE (konori)-[:SENIOR_JUNIOR {
    intensity: 8,
    speech_rule: ["指导工作", "关心后辈", "传授经验", "给予建议"],
    typical_scene: ["风纪委员办公室", "工作现场", "会议"],
    taboo: ["不能过度严厉", "不能忽视后辈感受"],
    relationship_desc: "前辈后辈关系，工作指导",
    interaction_pattern: "指导+关心+传授",
    created_at: datetime()
}]->(kuroko)

// 固法对初春的前辈关系
CREATE (konori)-[:SENIOR_JUNIOR {
    intensity: 7,
    speech_rule: ["指导工作", "关心后辈", "传授经验", "给予建议"],
    typical_scene: ["风纪委员办公室", "工作现场", "会议"],
    taboo: ["不能过度严厉", "不能忽视后辈感受"],
    relationship_desc: "前辈后辈关系，工作指导",
    interaction_pattern: "指导+关心+传授",
    created_at: datetime()
}]->(hatsuharu)

// 美琴和固法的同事关系（通过风纪委员工作）
CREATE (misaka)-[:COLLEAGUE {
    intensity: 5,
    speech_rule: ["工作配合", "互相尊重", "专业交流"],
    typical_scene: ["风纪委员办公室", "工作现场"],
    taboo: ["不能干扰工作", "不能违反规定"],
    relationship_desc: "通过风纪委员工作的同事关系",
    interaction_pattern: "工作+配合+尊重",
    created_at: datetime()
}]->(konori);

// 3. 创建关系类型索引
CREATE INDEX relationship_type_index FOR ()-[r:ADMIRER]-() ON (r.intensity);
CREATE INDEX relationship_type_index2 FOR ()-[r:ROOMMATE]-() ON (r.intensity);
CREATE INDEX relationship_type_index3 FOR ()-[r:COLLEAGUE]-() ON (r.intensity);
CREATE INDEX relationship_type_index4 FOR ()-[r:FRIEND]-() ON (r.intensity);
CREATE INDEX relationship_type_index5 FOR ()-[r:SENIOR_JUNIOR]-() ON (r.intensity);
CREATE INDEX relationship_type_index6 FOR ()-[r:BEST_FRIEND]-() ON (r.intensity);

// 4. 创建角色节点索引
CREATE INDEX character_id_index FOR (c:Character) ON (c.char_id);
CREATE INDEX character_name_index FOR (c:Character) ON (c.name_cn);

// 5. 查询示例和测试
// 查询黑子对美琴的所有关系
MATCH (kuroko:Character {char_id: "shirai_kuroko"})-[r]->(misaka:Character {char_id: "misaka_mikoto"})
RETURN r.speech_rule, r.taboo, r.typical_scene, r.intensity, r.relationship_desc;

// 查询美琴的所有关系
MATCH (misaka:Character {char_id: "misaka_mikoto"})-[r]-(other:Character)
RETURN other.name_cn, type(r) as relationship_type, r.intensity, r.relationship_desc
ORDER BY r.intensity DESC;

// 查询风纪委员之间的关系网络
MATCH (c:Character)-[r]-(other:Character)
WHERE c.identity CONTAINS "风纪委员" AND other.identity CONTAINS "风纪委员"
RETURN c.name_cn, other.name_cn, type(r) as relationship_type, r.intensity;

// 查询高强度的关系（intensity >= 8）
MATCH (c1:Character)-[r]-(c2:Character)
WHERE r.intensity >= 8
RETURN c1.name_cn, c2.name_cn, type(r) as relationship_type, r.intensity, r.relationship_desc
ORDER BY r.intensity DESC;

// 查询特定关系类型的规则
MATCH (c1:Character)-[r:ADMIRER]->(c2:Character)
RETURN c1.name_cn, c2.name_cn, r.speech_rule, r.taboo;

// 查询角色的所有关系强度分布
MATCH (c:Character {char_id: "misaka_mikoto"})-[r]-(other:Character)
RETURN 
    c.name_cn as character,
    type(r) as relationship_type,
    r.intensity,
    other.name_cn as related_character,
    r.relationship_desc
ORDER BY r.intensity DESC;

// 查询关系网络中的关键节点（连接度最高的角色）
MATCH (c:Character)-[r]-(other:Character)
WITH c, count(r) as connection_count
RETURN c.name_cn, c.char_id, connection_count
ORDER BY connection_count DESC;

// 查询特定场景下的关系互动
MATCH (c1:Character)-[r]-(c2:Character)
WHERE "美琴宿舍" IN r.typical_scene
RETURN c1.name_cn, c2.name_cn, type(r) as relationship_type, r.interaction_pattern;

// 查询关系禁忌和规则
MATCH (c1:Character)-[r]-(c2:Character)
WHERE r.taboo IS NOT NULL
RETURN c1.name_cn, c2.name_cn, type(r) as relationship_type, r.taboo, r.speech_rule;

// 创建关系统计视图
MATCH (c:Character)
OPTIONAL MATCH (c)-[r]-(other:Character)
WITH c, count(r) as total_relationships, 
     collect(DISTINCT type(r)) as relationship_types,
     avg(r.intensity) as avg_intensity
RETURN c.name_cn, c.char_id, total_relationships, relationship_types, avg_intensity
ORDER BY total_relationships DESC;
