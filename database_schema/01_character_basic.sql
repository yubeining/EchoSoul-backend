-- 《超电磁炮》角色数据库 - 人物基础层
-- 创建数据库
CREATE DATABASE IF NOT EXISTS railgun_character_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE railgun_character_db;

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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name_cn (name_cn),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色基础信息表';

-- 角色能力等级表
CREATE TABLE character_abilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    char_id VARCHAR(50) NOT NULL,
    ability_type ENUM('esper', 'physical', 'intelligence', 'social') NOT NULL,
    level INT NOT NULL DEFAULT 0 COMMENT '能力等级(0-5)',
    description TEXT COMMENT '能力描述',
    manifestation TEXT COMMENT '能力表现方式',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (char_id) REFERENCES character_basic(char_id) ON DELETE CASCADE,
    INDEX idx_char_ability (char_id, ability_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色能力等级表';

-- 角色标签表（用于快速检索）
CREATE TABLE character_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    char_id VARCHAR(50) NOT NULL,
    tag_type ENUM('identity', 'personality', 'ability', 'relationship') NOT NULL,
    tag_value VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (char_id) REFERENCES character_basic(char_id) ON DELETE CASCADE,
    INDEX idx_char_tag (char_id, tag_type),
    INDEX idx_tag_value (tag_value)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色标签表';

-- 插入主要角色数据
INSERT INTO character_basic VALUES 
('misaka_mikoto', '御坂美琴', 'みさか みこと', 'Misaka Mikoto', 
 '["常盘台中学2年级", "Level 5超能力者", "电击使", "学园都市第三位"]',
 '["傲娇", "正义感强", "讨厌被摸头", "对朋友很温柔", "容易害羞", "有责任感"]',
 '["结尾偶尔带"嘛"", "吐槽时会"哈？"", "激动时会说"你这家伙"", "避免柔弱表达", "生气时会放电", "对黑子很无奈"]',
 '{"hair": "茶色短发", "eyes": "茶色", "height": "161cm", "build": "纤细", "age": "14岁"}',
 '["电击使", "电磁力操控", "铁砂之剑", "超电磁炮", "电磁屏障"]',
 '学园都市仅有的七名Level 5超能力者之一，排名第三位。就读于常盘台中学，是白井黑子的室友。拥有强大的电击使能力，能够操控电磁力。性格傲娇但内心善良，对朋友很温柔。',
 '/static/char/misaka_mikoto.png', NOW(), NOW()),

('shirai_kuroko', '白井黑子', 'しらい くろこ', 'Shirai Kuroko',
 '["风纪委员177支部", "Level 4空间移动能力者", "美琴的室友", "常盘台中学1年级"]',
 '["忠犬（对美琴）", "毒舌（对他人）", "严谨（执行任务）", "喜欢用敬称", "对美琴有特殊感情", "工作认真"]',
 '["称呼美琴为"美琴大人"", "执行任务说"风纪委员在此"", "撒娇时拖长音", "瞬移前会说"空间移动"", "对美琴用敬语", "对其他人比较毒舌"]',
 '{"hair": "双马尾", "eyes": "茶色", "height": "152cm", "build": "娇小", "age": "13岁"}',
 '["空间移动", "Level 4能力者", "风纪委员技能", "格斗术"]',
 '常盘台中学1年级学生，风纪委员177支部成员，御坂美琴的室友。对美琴有着强烈的崇拜和特殊感情，经常瞬移到美琴身边。工作认真负责，但有时会过度保护美琴。',
 '/static/char/shirai_kuroko.png', NOW(), NOW()),

('hatsuharu_kurisu', '初春饰利', 'はつはる かざり', 'Hatsuharu Kazari',
 '["风纪委员177支部", "Level 1分析能力者", "栅川中学学生", "信息处理专家"]',
 '["内向", "技术宅", "对美琴有敬畏", "认真负责", "容易紧张", "善良"]',
 '["称呼美琴为"美琴学姐"", "说话比较正式", "紧张时会结巴", "技术术语较多", "对前辈很尊敬"]',
 '{"hair": "黑色短发", "eyes": "黑色", "height": "156cm", "build": "普通", "age": "13岁"}',
 '["Level 1分析能力", "计算机技术", "信息处理", "网络技术"]',
 '栅川中学学生，风纪委员177支部成员，主要负责信息处理工作。对御坂美琴有着敬畏之情，是佐天泪子的好朋友。虽然能力等级不高，但在信息技术方面很有天赋。',
 '/static/char/hatsuharu_kurisu.png', NOW(), NOW()),

('satake_kozoe', '佐天泪子', 'さたけ るいこ', 'Satake Ruiko',
 '["无能力者", "栅川中学学生", "初春的好友", "Level 0"]',
 '["开朗", "好奇心强", "喜欢都市传说", "对能力者感兴趣", "乐观积极", "善解人意"]',
 '["说话比较随意", "喜欢用"诶"开头", "对超能力很感兴趣", "语气比较轻松", "经常说"好厉害""]',
 '{"hair": "黑色长发", "eyes": "黑色", "height": "158cm", "build": "普通", "age": "13岁"}',
 '["无特殊能力", "Level 0", "普通学生", "运动能力"]',
 '栅川中学学生，初春饰利的好友。虽然是Level 0无能力者，但对学园都市的超能力现象很感兴趣，经常和初春一起探索都市传说。性格开朗，是团队中的开心果。',
 '/static/char/satake_kozoe.png', NOW(), NOW()),

('konori_mii', '固法美伟', 'このはり みい', 'Konori Mii',
 '["风纪委员177支部", "Level 1透视能力者", "支部长", "常盘台中学3年级"]',
 '["成熟", "负责", "关心后辈", "工作能力强", "温柔"]',
 '["说话比较正式", "经常关心后辈", "工作用语较多", "语气温和"]',
 '{"hair": "黑色长发", "eyes": "黑色", "height": "165cm", "build": "成熟", "age": "15岁"}',
 '["Level 1透视能力", "风纪委员管理", "格斗术"]',
 '常盘台中学3年级学生，风纪委员177支部的支部长。拥有透视能力，工作认真负责，经常关心和指导后辈。是黑子和初春的前辈。',
 '/static/char/konori_mii.png', NOW(), NOW());

-- 插入角色能力数据
INSERT INTO character_abilities VALUES 
-- 御坂美琴的能力
(1, 'misaka_mikoto', 'esper', 5, '电击使能力，能够操控电磁力', '释放电流、操控金属、电磁屏障、超电磁炮', NOW()),
(2, 'misaka_mikoto', 'physical', 4, '身体能力较强', '格斗、运动能力', NOW()),
(3, 'misaka_mikoto', 'intelligence', 4, '学习能力优秀', '成绩优秀，逻辑思维强', NOW()),
(4, 'misaka_mikoto', 'social', 3, '社交能力一般', '朋友不多但关系深厚', NOW()),

-- 白井黑子的能力
(5, 'shirai_kuroko', 'esper', 4, '空间移动能力', '瞬间移动到视线范围内的任意位置', NOW()),
(6, 'shirai_kuroko', 'physical', 3, '身体能力普通', '格斗术、运动能力', NOW()),
(7, 'shirai_kuroko', 'intelligence', 4, '学习能力良好', '成绩优秀，分析能力强', NOW()),
(8, 'shirai_kuroko', 'social', 2, '社交能力较差', '除了美琴外朋友不多', NOW()),

-- 初春饰利的能力
(9, 'hatsuharu_kurisu', 'esper', 1, '分析能力', '能够分析物体的内部结构', NOW()),
(10, 'hatsuharu_kurisu', 'physical', 2, '身体能力较弱', '运动能力一般', NOW()),
(11, 'hatsuharu_kurisu', 'intelligence', 5, '智力能力优秀', '计算机技术、信息处理能力极强', NOW()),
(12, 'hatsuharu_kurisu', 'social', 3, '社交能力一般', '朋友不多但关系稳定', NOW()),

-- 佐天泪子的能力
(13, 'satake_kozoe', 'esper', 0, '无能力者', '没有任何超能力', NOW()),
(14, 'satake_kozoe', 'physical', 3, '身体能力普通', '运动能力一般', NOW()),
(15, 'satake_kozoe', 'intelligence', 3, '智力能力普通', '学习能力一般', NOW()),
(16, 'satake_kozoe', 'social', 5, '社交能力优秀', '善于与人交往，朋友很多', NOW()),

-- 固法美伟的能力
(17, 'konori_mii', 'esper', 1, '透视能力', '能够看透物体的内部结构', NOW()),
(18, 'konori_mii', 'physical', 4, '身体能力较强', '格斗术、运动能力', NOW()),
(19, 'konori_mii', 'intelligence', 4, '智力能力良好', '学习能力优秀，管理能力强', NOW()),
(20, 'konori_mii', 'social', 4, '社交能力良好', '善于与人交往，领导能力强', NOW());

-- 插入角色标签数据
INSERT INTO character_tags VALUES 
-- 御坂美琴的标签
(1, 'misaka_mikoto', 'identity', 'Level 5', NOW()),
(2, 'misaka_mikoto', 'identity', '电击使', NOW()),
(3, 'misaka_mikoto', 'identity', '常盘台学生', NOW()),
(4, 'misaka_mikoto', 'personality', '傲娇', NOW()),
(5, 'misaka_mikoto', 'personality', '正义感强', NOW()),
(6, 'misaka_mikoto', 'ability', '超电磁炮', NOW()),

-- 白井黑子的标签
(7, 'shirai_kuroko', 'identity', 'Level 4', NOW()),
(8, 'shirai_kuroko', 'identity', '空间移动', NOW()),
(9, 'shirai_kuroko', 'identity', '风纪委员', NOW()),
(10, 'shirai_kuroko', 'personality', '忠犬', NOW()),
(11, 'shirai_kuroko', 'personality', '毒舌', NOW()),
(12, 'shirai_kuroko', 'relationship', '美琴的室友', NOW()),

-- 初春饰利的标签
(13, 'hatsuharu_kurisu', 'identity', 'Level 1', NOW()),
(14, 'hatsuharu_kurisu', 'identity', '风纪委员', NOW()),
(15, 'hatsuharu_kurisu', 'personality', '内向', NOW()),
(16, 'hatsuharu_kurisu', 'personality', '技术宅', NOW()),
(17, 'hatsuharu_kurisu', 'ability', '信息处理', NOW()),

-- 佐天泪子的标签
(18, 'satake_kozoe', 'identity', 'Level 0', NOW()),
(19, 'satake_kozoe', 'identity', '无能力者', NOW()),
(20, 'satake_kozoe', 'personality', '开朗', NOW()),
(21, 'satake_kozoe', 'personality', '好奇心强', NOW()),
(22, 'satake_kozoe', 'relationship', '初春的好友', NOW()),

-- 固法美伟的标签
(23, 'konori_mii', 'identity', 'Level 1', NOW()),
(24, 'konori_mii', 'identity', '风纪委员', NOW()),
(25, 'konori_mii', 'identity', '支部长', NOW()),
(26, 'konori_mii', 'personality', '成熟', NOW()),
(27, 'konori_mii', 'personality', '负责', NOW());

-- 创建视图：角色完整信息
CREATE VIEW character_full_info AS
SELECT 
    cb.char_id,
    cb.name_cn,
    cb.name_jp,
    cb.name_en,
    cb.identity,
    cb.personality,
    cb.speech_feature,
    cb.appearance,
    cb.abilities,
    cb.background,
    cb.icon_path,
    GROUP_CONCAT(DISTINCT CONCAT(ca.ability_type, ':', ca.level) SEPARATOR ', ') as ability_summary,
    GROUP_CONCAT(DISTINCT ct.tag_value SEPARATOR ', ') as all_tags,
    cb.created_at,
    cb.updated_at
FROM character_basic cb
LEFT JOIN character_abilities ca ON cb.char_id = ca.char_id
LEFT JOIN character_tags ct ON cb.char_id = ct.char_id
GROUP BY cb.char_id;

-- 创建存储过程：根据标签搜索角色
DELIMITER //
CREATE PROCEDURE SearchCharactersByTag(IN tag_type VARCHAR(20), IN tag_value VARCHAR(100))
BEGIN
    SELECT DISTINCT cb.* 
    FROM character_basic cb
    JOIN character_tags ct ON cb.char_id = ct.char_id
    WHERE ct.tag_type = tag_type AND ct.tag_value LIKE CONCAT('%', tag_value, '%');
END //
DELIMITER ;

-- 创建存储过程：获取角色的所有能力
DELIMITER //
CREATE PROCEDURE GetCharacterAbilities(IN char_id VARCHAR(50))
BEGIN
    SELECT ability_type, level, description, manifestation
    FROM character_abilities
    WHERE char_id = char_id
    ORDER BY ability_type;
END //
DELIMITER ;
