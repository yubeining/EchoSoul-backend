-- 《超电磁炮》角色数据库 - 对话场景层
USE railgun_character_db;

-- 场景信息表
CREATE TABLE scene_info (
    scene_id VARCHAR(50) PRIMARY KEY COMMENT '场景唯一标识',
    scene_name VARCHAR(100) NOT NULL COMMENT '场景名称',
    scene_type ENUM('dormitory', 'school', 'office', 'street', 'cafe', 'other') NOT NULL COMMENT '场景类型',
    description TEXT COMMENT '场景详细描述',
    atmosphere JSON COMMENT '场景氛围标签',
    location_info JSON COMMENT '位置信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_scene_type (scene_type),
    INDEX idx_scene_name (scene_name)
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
    dialogue_type ENUM('daily', 'conflict', 'romantic', 'work', 'other') DEFAULT 'daily' COMMENT '对话类型',
    intensity_level INT DEFAULT 1 COMMENT '对话强度等级(1-10)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (scene_id) REFERENCES scene_info(scene_id) ON DELETE CASCADE,
    INDEX idx_scene_id (scene_id),
    INDEX idx_dialogue_type (dialogue_type),
    INDEX idx_intensity (intensity_level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话场景表';

-- 对话轮次表（用于复杂查询和分析）
CREATE TABLE dialogue_turns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dialogue_id VARCHAR(50) NOT NULL,
    turn_num INT NOT NULL,
    speaker_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    action_desc TEXT COMMENT '动作描述',
    emotion VARCHAR(50) COMMENT '情绪标签',
    speech_style VARCHAR(100) COMMENT '语言风格',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dialogue_id) REFERENCES dialogue_scene(dialogue_id) ON DELETE CASCADE,
    FOREIGN KEY (speaker_id) REFERENCES character_basic(char_id) ON DELETE CASCADE,
    INDEX idx_dialogue_turn (dialogue_id, turn_num),
    INDEX idx_speaker (speaker_id),
    INDEX idx_emotion (emotion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话轮次表';

-- 对话关系表（记录对话中体现的关系）
CREATE TABLE dialogue_relationships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dialogue_id VARCHAR(50) NOT NULL,
    char_id_1 VARCHAR(50) NOT NULL,
    char_id_2 VARCHAR(50) NOT NULL,
    relationship_type VARCHAR(50) NOT NULL COMMENT '关系类型',
    relationship_intensity INT DEFAULT 1 COMMENT '关系强度(1-10)',
    interaction_pattern VARCHAR(100) COMMENT '互动模式',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dialogue_id) REFERENCES dialogue_scene(dialogue_id) ON DELETE CASCADE,
    FOREIGN KEY (char_id_1) REFERENCES character_basic(char_id) ON DELETE CASCADE,
    FOREIGN KEY (char_id_2) REFERENCES character_basic(char_id) ON DELETE CASCADE,
    INDEX idx_dialogue_rel (dialogue_id),
    INDEX idx_char_rel (char_id_1, char_id_2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话关系表';

-- 插入场景信息
INSERT INTO scene_info VALUES 
('dormitory_misaka_room', '美琴宿舍', 'dormitory', 
 '常盘台中学宿舍，美琴和黑子的房间。书桌、床铺、衣柜等家具齐全，墙上贴着一些海报。房间整洁，有温馨的日常氛围。',
 '["温馨", "日常", "私密", "放松"]',
 '{"building": "常盘台中学宿舍", "floor": "3楼", "room": "301室", "area": "学园都市第7学区"}',
 NOW()),

('wind_judgment_office', '风纪委员办公室', 'office',
 '风纪委员177支部的办公室，有办公桌、电脑、文件柜等办公设备。墙上贴着各种规章制度和任务安排。',
 '["严肃", "工作", "正式", "忙碌"]',
 '{"building": "常盘台中学", "floor": "2楼", "room": "风纪委员办公室", "area": "学园都市第7学区"}',
 NOW()),

('school_corridor', '学校走廊', 'school',
 '常盘台中学的走廊，连接各个教室和办公室。阳光透过窗户洒在地板上，学生们经常在这里交流。',
 '["校园", "日常", "社交", "明亮"]',
 '{"building": "常盘台中学", "floor": "2楼", "area": "学园都市第7学区"}',
 NOW()),

('street_shopping', '商业街', 'street',
 '学园都市的商业街，有各种商店和餐厅，人来人往。霓虹灯闪烁，充满都市的活力。',
 '["热闹", "购物", "休闲", "繁华"]',
 '{"district": "学园都市第7学区", "street": "商业街", "area": "学园都市"}',
 NOW()),

('cafe_meeting', '咖啡厅', 'cafe',
 '学园都市的一家咖啡厅，环境安静舒适，适合朋友聚会和讨论。有温暖的灯光和轻柔的音乐。',
 '["安静", "温馨", "社交", "舒适"]',
 '{"district": "学园都市第7学区", "building": "商业街咖啡厅", "area": "学园都市"}',
 NOW()),

('school_rooftop', '学校天台', 'school',
 '常盘台中学的天台，视野开阔，可以看到学园都市的景色。学生们经常在这里休息和聊天。',
 '["开阔", "安静", "私密", "风景好"]',
 '{"building": "常盘台中学", "floor": "天台", "area": "学园都市第7学区"}',
 NOW());

-- 插入对话场景数据
INSERT INTO dialogue_scene VALUES 
('s01_e03_d05', 'dormitory_misaka_room', 
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
 '{"season": 1, "episode": 3, "time_range": "05:20-06:10", "title": "日常的宿舍时光"}',
 'daily', 3, NOW(), NOW()),

('s01_e05_d12', 'wind_judgment_office',
 '["shirai_kuroko", "hatsuharu_kurisu", "konori_mii"]',
 '[
     {
         "turn_num": 1,
         "speaker_id": "konori_mii",
         "content": "黑子，初春，今天下午有个紧急任务，需要你们去处理一下。",
         "action": "放下手中的文件，认真地看着两人",
         "emotion": "严肃"
     },
     {
         "turn_num": 2,
         "speaker_id": "shirai_kuroko",
         "content": "是！固法前辈，请告诉我们具体任务内容。",
         "action": "立即站直，表情认真",
         "emotion": "认真"
     },
     {
         "turn_num": 3,
         "speaker_id": "hatsuharu_kurisu",
         "content": "我...我也会努力的！",
         "action": "紧张地握紧拳头，声音有些颤抖",
         "emotion": "紧张"
     },
     {
         "turn_num": 4,
         "speaker_id": "konori_mii",
         "content": "初春，不用紧张，这次主要是信息收集工作，你的专长。",
         "action": "温和地笑着，拍拍初春的肩膀",
         "emotion": "温和"
     }
 ]',
 '["konori:严肃转温和", "kuroko:认真", "hatsuharu:紧张"]',
 '风纪委员办公室的工作任务分配对话',
 '番剧S1E5 12:30-13:15',
 '{"season": 1, "episode": 5, "time_range": "12:30-13:15", "title": "工作任务分配"}',
 'work', 5, NOW(), NOW()),

('s01_e08_d08', 'street_shopping',
 '["misaka_mikoto", "satake_kozoe"]',
 '[
     {
         "turn_num": 1,
         "speaker_id": "satake_kozoe",
         "content": "诶，美琴学姐！好巧啊，你也来买东西吗？",
         "action": "兴奋地挥手，快步走向美琴",
         "emotion": "兴奋"
     },
     {
         "turn_num": 2,
         "speaker_id": "misaka_mikoto",
         "content": "啊，是佐天啊。嗯，来买一些日用品。",
         "action": "有些意外地回头，礼貌地回应",
         "emotion": "礼貌"
     },
     {
         "turn_num": 3,
         "speaker_id": "satake_kozoe",
         "content": "太好了！我们一起逛吧，我正好想买一些东西。",
         "action": "开心地提议，眼睛闪闪发光",
         "emotion": "开心"
     },
     {
         "turn_num": 4,
         "speaker_id": "misaka_mikoto",
         "content": "嗯...好吧，不过不要买太多奇怪的东西哦。",
         "action": "无奈地笑着，但还是答应了",
         "emotion": "无奈+友善"
     }
 ]',
 '["misaka:礼貌转友善", "satake:兴奋转开心"]',
 '美琴和佐天在商业街偶遇的对话',
 '番剧S1E8 08:45-09:30',
 '{"season": 1, "episode": 8, "time_range": "08:45-09:30", "title": "商业街偶遇"}',
 'daily', 2, NOW(), NOW()),

('s01_e12_d15', 'school_rooftop',
 '["hatsuharu_kurisu", "satake_kozoe"]',
 '[
     {
         "turn_num": 1,
         "speaker_id": "satake_kozoe",
         "content": "初春，你最近工作很忙吗？看起来有点累的样子。",
         "action": "关心地看着初春，语气温柔",
         "emotion": "关心"
     },
     {
         "turn_num": 2,
         "speaker_id": "hatsuharu_kurisu",
         "content": "嗯...最近风纪委员的工作确实比较多，不过没关系，我能应付的。",
         "action": "有些疲惫地笑了笑，但努力保持积极",
         "emotion": "疲惫但坚强"
     },
     {
         "turn_num": 3,
         "speaker_id": "satake_kozoe",
         "content": "如果有什么需要帮助的，一定要告诉我哦。我们是好朋友嘛！",
         "action": "握住初春的手，认真地说",
         "emotion": "真诚"
     },
     {
         "turn_num": 4,
         "speaker_id": "hatsuharu_kurisu",
         "content": "谢谢你，佐天。有你在身边，我觉得很安心。",
         "action": "感动地回握佐天的手，眼中有些湿润",
         "emotion": "感动"
     }
 ]',
 '["hatsuharu:疲惫转感动", "satake:关心转真诚"]',
 '初春和佐天在天台的友情对话',
 '番剧S1E12 15:20-16:05',
 '{"season": 1, "episode": 12, "time_range": "15:20-16:05", "title": "天台的友情"}',
 'daily', 4, NOW(), NOW());

-- 插入对话轮次数据（从JSON中提取）
INSERT INTO dialogue_turns (dialogue_id, turn_num, speaker_id, content, action_desc, emotion, speech_style) VALUES 
-- 宿舍对话轮次
('s01_e03_d05', 1, 'shirai_kuroko', '美琴大人～我带了便利店刚买的草莓大福，要一起吃吗？', '瞬移到美琴身后，递出包装袋，眼睛亮晶晶', '兴奋', '撒娇+敬语'),
('s01_e03_d05', 2, 'misaka_mikoto', '哈？你又没敲门就瞬移进来了——还有，别用那种称呼叫我啊！', '手顿了一下，回头瞪黑子，耳朵尖有点红', '无奈+轻微羞恼', '吐槽+傲娇'),
('s01_e03_d05', 3, 'shirai_kuroko', '可是美琴大人的房间就是我的房间嘛～而且大福要趁新鲜吃哦～', '凑近美琴，把大福递到她嘴边', '撒娇', '撒娇+坚持'),
('s01_e03_d05', 4, 'misaka_mikoto', '真是的...不过既然你买了，那就一起吃吧。但是下次要敲门！', '接过大福，脸上带着无奈的笑容', '妥协+温柔', '妥协+关心'),

-- 办公室对话轮次
('s01_e05_d12', 1, 'konori_mii', '黑子，初春，今天下午有个紧急任务，需要你们去处理一下。', '放下手中的文件，认真地看着两人', '严肃', '正式+工作'),
('s01_e05_d12', 2, 'shirai_kuroko', '是！固法前辈，请告诉我们具体任务内容。', '立即站直，表情认真', '认真', '敬语+工作'),
('s01_e05_d12', 3, 'hatsuharu_kurisu', '我...我也会努力的！', '紧张地握紧拳头，声音有些颤抖', '紧张', '紧张+决心'),
('s01_e05_d12', 4, 'konori_mii', '初春，不用紧张，这次主要是信息收集工作，你的专长。', '温和地笑着，拍拍初春的肩膀', '温和', '安慰+鼓励'),

-- 商业街对话轮次
('s01_e08_d08', 1, 'satake_kozoe', '诶，美琴学姐！好巧啊，你也来买东西吗？', '兴奋地挥手，快步走向美琴', '兴奋', '随意+热情'),
('s01_e08_d08', 2, 'misaka_mikoto', '啊，是佐天啊。嗯，来买一些日用品。', '有些意外地回头，礼貌地回应', '礼貌', '礼貌+简洁'),
('s01_e08_d08', 3, 'satake_kozoe', '太好了！我们一起逛吧，我正好想买一些东西。', '开心地提议，眼睛闪闪发光', '开心', '热情+邀请'),
('s01_e08_d08', 4, 'misaka_mikoto', '嗯...好吧，不过不要买太多奇怪的东西哦。', '无奈地笑着，但还是答应了', '无奈+友善', '妥协+提醒'),

-- 天台对话轮次
('s01_e12_d15', 1, 'satake_kozoe', '初春，你最近工作很忙吗？看起来有点累的样子。', '关心地看着初春，语气温柔', '关心', '关心+观察'),
('s01_e12_d15', 2, 'hatsuharu_kurisu', '嗯...最近风纪委员的工作确实比较多，不过没关系，我能应付的。', '有些疲惫地笑了笑，但努力保持积极', '疲惫但坚强', '坚强+努力'),
('s01_e12_d15', 3, 'satake_kozoe', '如果有什么需要帮助的，一定要告诉我哦。我们是好朋友嘛！', '握住初春的手，认真地说', '真诚', '真诚+承诺'),
('s01_e12_d15', 4, 'hatsuharu_kurisu', '谢谢你，佐天。有你在身边，我觉得很安心。', '感动地回握佐天的手，眼中有些湿润', '感动', '感谢+依赖');

-- 插入对话关系数据
INSERT INTO dialogue_relationships VALUES 
(1, 's01_e03_d05', 'shirai_kuroko', 'misaka_mikoto', 'ADMIRER', 10, '崇拜+撒娇', NOW()),
(2, 's01_e03_d05', 'shirai_kuroko', 'misaka_mikoto', 'ROOMMATE', 9, '室友日常', NOW()),
(3, 's01_e05_d12', 'shirai_kuroko', 'konori_mii', 'SENIOR_JUNIOR', 8, '工作指导', NOW()),
(4, 's01_e05_d12', 'hatsuharu_kurisu', 'konori_mii', 'SENIOR_JUNIOR', 7, '工作指导', NOW()),
(5, 's01_e05_d12', 'shirai_kuroko', 'hatsuharu_kurisu', 'COLLEAGUE', 8, '工作配合', NOW()),
(6, 's01_e08_d08', 'misaka_mikoto', 'satake_kozoe', 'FRIEND', 7, '朋友交流', NOW()),
(7, 's01_e12_d15', 'hatsuharu_kurisu', 'satake_kozoe', 'BEST_FRIEND', 9, '友情支持', NOW());

-- 创建视图：对话完整信息
CREATE VIEW dialogue_full_info AS
SELECT 
    ds.dialogue_id,
    ds.scene_id,
    si.scene_name,
    si.scene_type,
    ds.participants,
    ds.dialogue_turn,
    ds.emotion_tag,
    ds.context_summary,
    ds.source,
    ds.episode_info,
    ds.dialogue_type,
    ds.intensity_level,
    ds.created_at
FROM dialogue_scene ds
JOIN scene_info si ON ds.scene_id = si.scene_id;

-- 创建视图：角色对话统计
CREATE VIEW character_dialogue_stats AS
SELECT 
    dt.speaker_id,
    cb.name_cn,
    COUNT(*) as dialogue_count,
    COUNT(DISTINCT ds.dialogue_id) as scene_count,
    COUNT(DISTINCT ds.scene_id) as location_count,
    AVG(ds.intensity_level) as avg_intensity,
    GROUP_CONCAT(DISTINCT dt.emotion SEPARATOR ', ') as emotions_used
FROM dialogue_turns dt
JOIN character_basic cb ON dt.speaker_id = cb.char_id
JOIN dialogue_scene ds ON dt.dialogue_id = ds.dialogue_id
GROUP BY dt.speaker_id, cb.name_cn;

-- 创建存储过程：根据场景和角色查询对话
DELIMITER //
CREATE PROCEDURE GetDialoguesBySceneAndCharacters(
    IN scene_type VARCHAR(20), 
    IN char_ids JSON
)
BEGIN
    SELECT ds.*, si.scene_name, si.description
    FROM dialogue_scene ds
    JOIN scene_info si ON ds.scene_id = si.scene_id
    WHERE si.scene_type = scene_type
    AND JSON_CONTAINS(ds.participants, char_ids);
END //
DELIMITER ;

-- 创建存储过程：获取角色的对话风格分析
DELIMITER //
CREATE PROCEDURE AnalyzeCharacterSpeechStyle(IN char_id VARCHAR(50))
BEGIN
    SELECT 
        emotion,
        speech_style,
        COUNT(*) as frequency,
        AVG(LENGTH(content)) as avg_length
    FROM dialogue_turns
    WHERE speaker_id = char_id
    GROUP BY emotion, speech_style
    ORDER BY frequency DESC;
END //
DELIMITER ;
