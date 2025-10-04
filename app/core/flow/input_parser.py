"""
输入解析器 (InputParser)
解析用户输入，提取意图、实体、情感等信息
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from app.core.management.logging_manager import log_operation_start, log_operation_success, log_operation_error, log_info
from app.core.flow.models import UserInput, ParsedInput, ParsedEntity

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """意图类型枚举"""
    GREETING = "greeting"
    QUESTION = "question"
    REQUEST = "request"
    COMPLAINT = "complaint"
    PRAISE = "praise"
    STORY_REQUEST = "story_request"
    CREATIVE_REQUEST = "creative_request"
    INFORMATION_REQUEST = "information_request"
    EMOTIONAL_SUPPORT = "emotional_support"
    TOPIC_CHANGE = "topic_change"
    FAREWELL = "farewell"
    UNKNOWN = "unknown"

class SentimentType(Enum):
    """情感类型枚举"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    SAD = "sad"
    HAPPY = "happy"
    ANGRY = "angry"

# ParsedEntity已移至 app.core.models

# ParsedInput已移至 app.core.models

class InputParser:
    """输入解析器"""
    
    def __init__(self):
        # 意图识别模式
        self.intent_patterns = {
            IntentType.GREETING: [
                r'你好', r'hello', r'hi', r'嗨', r'早上好', r'下午好', r'晚上好',
                r'你好吗', r'how are you', r'hey', r'喂'
            ],
            IntentType.QUESTION: [
                r'什么', r'怎么', r'为什么', r'哪里', r'什么时候', r'who', r'what', r'how', r'why', r'where', r'when',
                r'？', r'\?', r'吗\?', r'呢\?'
            ],
            IntentType.REQUEST: [
                r'请', r'帮我', r'可以', r'能否', r'please', r'help me', r'can you', r'could you',
                r'告诉我', r'告诉我', r'tell me', r'give me'
            ],
            IntentType.COMPLAINT: [
                r'不好', r'讨厌', r'烦', r'生气', r'抱怨', r'bad', r'hate', r'annoying', r'angry',
                r'问题', r'错误', r'bug', r'issue', r'problem'
            ],
            IntentType.PRAISE: [
                r'好', r'棒', r'赞', r'厉害', r'优秀', r'good', r'great', r'excellent', r'awesome',
                r'喜欢', r'love', r'like', r'amazing'
            ],
            IntentType.STORY_REQUEST: [
                r'故事', r'讲个', r'编个', r'story', r'tell a story', r'create a story',
                r'小说', r'novel', r'fiction'
            ],
            IntentType.CREATIVE_REQUEST: [
                r'创作', r'创意', r'想象', r'creative', r'imagine', r'create', r'design',
                r'写诗', r'poem', r'诗歌', r'画画', r'draw', r'画'
            ],
            IntentType.INFORMATION_REQUEST: [
                r'信息', r'资料', r'数据', r'information', r'data', r'knowledge',
                r'解释', r'explain', r'describe', r'介绍', r'introduce'
            ],
            IntentType.EMOTIONAL_SUPPORT: [
                r'难过', r'伤心', r'沮丧', r'sad', r'depressed', r'upset',
                r'安慰', r'comfort', r'support', r'帮助', r'help'
            ],
            IntentType.TOPIC_CHANGE: [
                r'换个', r'换个话题', r'说点别的', r'change topic', r'another subject',
                r'我们聊聊', r'let\'s talk about', r'说说'
            ],
            IntentType.FAREWELL: [
                r'再见', r'拜拜', r'bye', r'goodbye', r'see you', r'下次聊',
                r'结束', r'end', r'finish', r'停止', r'stop'
            ]
        }
        
        # 情感识别模式
        self.sentiment_patterns = {
            SentimentType.POSITIVE: [
                r'好', r'棒', r'赞', r'喜欢', r'爱', r'开心', r'高兴', r'满意',
                r'good', r'great', r'love', r'like', r'happy', r'joy', r'pleased'
            ],
            SentimentType.NEGATIVE: [
                r'不好', r'坏', r'讨厌', r'烦', r'生气', r'难过', r'沮丧', r'失望',
                r'bad', r'hate', r'annoying', r'angry', r'sad', r'upset', r'disappointed'
            ],
            SentimentType.EXCITED: [
                r'兴奋', r'激动', r'太棒了', r'哇', r'awesome', r'excited', r'thrilled',
                r'wow', r'amazing', r'incredible'
            ],
            SentimentType.FRUSTRATED: [
                r'沮丧', r'烦躁', r'无奈', r'frustrated', r'irritated', r'furious'
            ],
            SentimentType.SAD: [
                r'难过', r'伤心', r'泪', r'哭', r'sad', r'crying', r'tears'
            ],
            SentimentType.HAPPY: [
                r'开心', r'快乐', r'高兴', r'笑', r'happy', r'joyful', r'smiling'
            ],
            SentimentType.ANGRY: [
                r'生气', r'愤怒', r'恼火', r'angry', r'mad', r'furious'
            ]
        }
        
        # 实体识别模式
        self.entity_patterns = {
            'time': [
                r'\d{1,2}点', r'\d{1,2}:\d{2}', r'今天', r'明天', r'昨天', r'now', r'today', r'tomorrow', r'yesterday',
                r'上午', r'下午', r'晚上', r'morning', r'afternoon', r'evening', r'night'
            ],
            'location': [
                r'在.*?地方', r'哪里', r'where', r'北京', r'上海', r'广州', r'beijing', r'shanghai'
            ],
            'person': [
                r'我', r'你', r'他', r'她', r'我们', r'你们', r'他们', r'i', r'you', r'he', r'she', r'we', r'they'
            ],
            'number': [
                r'\d+', r'一', r'二', r'三', r'四', r'五', r'one', r'two', r'three', r'four', r'five'
            ],
            'emotion': [
                r'开心', r'难过', r'生气', r'高兴', r'happy', r'sad', r'angry', r'joy'
            ]
        }
        
        # 处理统计
        self.stats = {
            "total_parsed": 0,
            "successful_parsed": 0,
            "failed_parsed": 0,
            "intent_distribution": {},
            "sentiment_distribution": {}
        }
    
    async def parse(self, user_input) -> ParsedInput:
        """
        解析用户输入
        
        Args:
            user_input: 用户输入对象
            
        Returns:
            ParsedInput: 解析结果
        """
        log_operation_start("解析用户输入", user_id=user_input.user_id)
        
        try:
            original_text = user_input.content or ""
            
            # 1. 文本预处理
            processed_text = await self._preprocess_text(original_text)
            
            # 2. 意图识别
            intent, intent_confidence = await self._recognize_intent(processed_text)
            
            # 3. 实体识别
            entities = await self._recognize_entities(processed_text)
            
            # 4. 情感分析
            sentiment, sentiment_confidence = await self._analyze_sentiment(processed_text)
            
            # 5. 语言检测
            language = await self._detect_language(processed_text)
            
            # 6. 计算总体置信度
            overall_confidence = await self._calculate_overall_confidence(
                intent_confidence, sentiment_confidence, entities
            )
            
            # 7. 构建处理元数据
            processing_metadata = {
                'processing_time': datetime.utcnow().isoformat(),
                'text_length': len(original_text),
                'language': language,
                'intent_confidence': intent_confidence,
                'sentiment_confidence': sentiment_confidence,
                'entity_count': len(entities)
            }
            
            # 构建解析结果
            parsed_input = ParsedInput(
                original_text=original_text,
                intent=intent.value if isinstance(intent, IntentType) else intent,
                entities=entities,
                sentiment=sentiment.value if isinstance(sentiment, SentimentType) else sentiment,
                confidence=overall_confidence,
                language=language,
                processing_metadata=processing_metadata
            )
            
            # 更新统计信息
            self._update_stats(parsed_input)
            
            log_operation_success("解析用户输入", user_id=user_input.user_id, 
                                intent=intent.value, sentiment=sentiment.value if sentiment else None)
            
            return parsed_input
            
        except Exception as e:
            log_operation_error("解析用户输入", str(e), user_id=user_input.user_id)
            
            # 返回默认解析结果
            return ParsedInput(
                original_text=user_input.content or "",
                intent="unknown",
                entities=[],
                sentiment="neutral",
                confidence=0.3,
                language="unknown",
                processing_metadata={'error': str(e)}
            )
    
    async def _preprocess_text(self, text: str) -> str:
        """文本预处理"""
        if not text:
            return ""
        
        # 转换为小写
        text = text.lower()
        
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 移除特殊字符（保留中文、英文、数字、基本标点）
        text = re.sub(r'[^\u4e00-\u9fff\w\s.,!?;:()（）]', '', text)
        
        return text
    
    async def _recognize_intent(self, text: str) -> Tuple[IntentType, float]:
        """意图识别"""
        if not text:
            return IntentType.UNKNOWN, 0.0
        
        intent_scores = {}
        
        # 计算每个意图的匹配分数
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches += 1
                    # 根据匹配长度和位置计算分数
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        match_length = len(match.group())
                        score += match_length / len(text)  # 匹配长度占比
            
            if matches > 0:
                intent_scores[intent_type] = score / len(patterns)  # 平均分数
        
        # 选择分数最高的意图
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[best_intent], 1.0)
            return best_intent, confidence
        
        return IntentType.UNKNOWN, 0.1
    
    async def _recognize_entities(self, text: str) -> List[ParsedEntity]:
        """实体识别"""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = ParsedEntity(
                        entity_type=entity_type,
                        value=match.group(),
                        confidence=0.8,  # 简单的置信度
                        position=(match.start(), match.end())
                    )
                    entities.append(entity)
        
        # 去重（保留置信度最高的）
        unique_entities = {}
        for entity in entities:
            key = (entity.entity_type, entity.value)
            if key not in unique_entities or entity.confidence > unique_entities[key].confidence:
                unique_entities[key] = entity
        
        return list(unique_entities.values())
    
    async def _analyze_sentiment(self, text: str) -> Tuple[Optional[SentimentType], float]:
        """情感分析"""
        if not text:
            return SentimentType.NEUTRAL, 0.5
        
        sentiment_scores = {}
        
        # 计算每个情感的匹配分数
        for sentiment_type, patterns in self.sentiment_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches += 1
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        match_length = len(match.group())
                        score += match_length / len(text)
            
            if matches > 0:
                sentiment_scores[sentiment_type] = score / len(patterns)
        
        # 选择分数最高的情感
        if sentiment_scores:
            best_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            confidence = min(sentiment_scores[best_sentiment], 1.0)
            return best_sentiment, confidence
        
        return SentimentType.NEUTRAL, 0.5
    
    async def _detect_language(self, text: str) -> str:
        """语言检测"""
        if not text:
            return "unknown"
        
        # 简单的语言检测
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if chinese_chars > english_chars:
            return "chinese"
        elif english_chars > 0:
            return "english"
        else:
            return "unknown"
    
    async def _calculate_overall_confidence(self, intent_confidence: float, 
                                          sentiment_confidence: float, 
                                          entities: List[ParsedEntity]) -> float:
        """计算总体置信度"""
        # 基础置信度
        base_confidence = (intent_confidence + sentiment_confidence) / 2
        
        # 实体匹配加分
        entity_bonus = min(len(entities) * 0.05, 0.2)
        
        # 最终置信度
        overall_confidence = min(base_confidence + entity_bonus, 1.0)
        
        return max(overall_confidence, 0.1)  # 最低置信度
    
    def _update_stats(self, parsed_input: ParsedInput):
        """更新统计信息"""
        self.stats["total_parsed"] += 1
        
        if parsed_input.confidence > 0.5:
            self.stats["successful_parsed"] += 1
        else:
            self.stats["failed_parsed"] += 1
        
        # 更新意图分布
        intent = parsed_input.intent
        if intent not in self.stats["intent_distribution"]:
            self.stats["intent_distribution"][intent] = 0
        self.stats["intent_distribution"][intent] += 1
        
        # 更新情感分布
        sentiment = parsed_input.sentiment
        if sentiment and sentiment not in self.stats["sentiment_distribution"]:
            self.stats["sentiment_distribution"][sentiment] = 0
        self.stats["sentiment_distribution"][sentiment] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取解析统计信息"""
        stats = self.stats.copy()
        
        # 计算成功率
        if stats["total_parsed"] > 0:
            stats["success_rate"] = stats["successful_parsed"] / stats["total_parsed"]
        else:
            stats["success_rate"] = 0.0
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试解析功能
            test_input = type('TestInput', (), {
                'user_id': 0,
                'content': '你好，今天天气怎么样？'
            })()
            
            result = await self.parse(test_input)
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "test_result": {
                    "intent": result.intent,
                    "sentiment": result.sentiment,
                    "confidence": result.confidence,
                    "entity_count": len(result.entities)
                },
                "stats": self.get_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
