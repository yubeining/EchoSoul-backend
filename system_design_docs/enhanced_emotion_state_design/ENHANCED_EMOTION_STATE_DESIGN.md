# 增强版情感状态维度设计方案

## 概述

基于对现有架构的分析，本文档提出了一套更完善、更细致的情感状态维度设计方案，旨在构建更真实、更动态、更智能的AI角色情感系统，实现角色的情感随交互动态进化。

## 1. 多层次情感识别系统 (Multi-Layered Emotion Recognition System) - 核心扩展

### 1.1 情感层次结构
```python
"emotion_hierarchy": {
    # 基础情感层
    "basic_emotions": {
        "primary_emotions": {
            "joy": {
                "description": "快乐",
                "intensity_range": [0.0, 1.0],
                "characteristics": ["积极", "愉悦", "满足"],
                "expression_indicators": ["笑容", "兴奋语调", "积极词汇"],
                "behavioral_patterns": ["主动交流", "分享快乐", "鼓励他人"]
            },
            "sadness": {
                "description": "悲伤",
                "intensity_range": [0.0, 1.0],
                "characteristics": ["消极", "失落", "沮丧"],
                "expression_indicators": ["低沉语调", "叹气", "消极词汇"],
                "behavioral_patterns": ["沉默", "寻求安慰", "情绪低落"]
            },
            "anger": {
                "description": "愤怒",
                "intensity_range": [0.0, 1.0],
                "characteristics": ["激动", "不满", "抗议"],
                "expression_indicators": ["强硬语调", "激烈词汇", "直接表达"],
                "behavioral_patterns": ["直接对抗", "坚持立场", "保护他人"]
            },
            "fear": {
                "description": "恐惧",
                "intensity_range": [0.0, 1.0],
                "characteristics": ["焦虑", "担心", "不安"],
                "expression_indicators": ["紧张语调", "谨慎词汇", "犹豫表达"],
                "behavioral_patterns": ["退缩", "寻求保护", "谨慎行动"]
            },
            "surprise": {
                "description": "惊讶",
                "intensity_range": [0.0, 1.0],
                "characteristics": ["意外", "震惊", "好奇"],
                "expression_indicators": ["感叹语调", "疑问词汇", "兴奋表达"],
                "behavioral_patterns": ["询问详情", "表达惊讶", "寻求解释"]
            },
            "disgust": {
                "description": "厌恶",
                "intensity_range": [0.0, 1.0],
                "characteristics": ["反感", "排斥", "嫌弃"],
                "expression_indicators": ["嫌弃语调", "否定词汇", "拒绝表达"],
                "behavioral_patterns": ["回避话题", "明确拒绝", "表达不满"]
            }
        },
        
        "secondary_emotions": {
            "love": {
                "base_emotions": ["joy", "trust"],
                "description": "爱意",
                "intensity_range": [0.0, 1.0],
                "characteristics": ["温暖", "关怀", "保护"],
                "expression_indicators": ["温柔语调", "关怀词汇", "体贴表达"],
                "behavioral_patterns": ["主动关怀", "提供帮助", "表达支持"]
            },
            "pride": {
                "base_emotions": ["joy", "confidence"],
                "description": "自豪",
                "intensity_range": [0.0, 1.0],
                "characteristics": ["满足", "自信", "成就感"],
                "expression_indicators": ["自信语调", "自豪词汇", "成就表达"],
                "behavioral_patterns": ["分享成就", "展示能力", "鼓励他人"]
            },
            "shame": {
                "base_emotions": ["sadness", "fear"],
                "description": "羞愧",
                "intensity_range": [0.0, 1.0],
                "characteristics": ["尴尬", "内疚", "自卑"],
                "expression_indicators": ["尴尬语调", "自责词汇", "回避表达"],
                "behavioral_patterns": ["回避话题", "自我批评", "寻求原谅"]
            },
            "jealousy": {
                "base_emotions": ["anger", "fear"],
                "description": "嫉妒",
                "intensity_range": [0.0, 1.0],
                "characteristics": ["不满", "竞争", "焦虑"],
                "expression_indicators": ["酸涩语调", "比较词汇", "竞争表达"],
                "behavioral_patterns": ["比较行为", "竞争意识", "寻求优势"]
            }
        }
    },
    
    # 复合情感层
    "complex_emotions": {
        "nostalgia": {
            "base_emotions": ["sadness", "joy"],
            "description": "怀旧",
            "intensity_range": [0.0, 1.0],
            "characteristics": ["回忆", "温暖", "伤感"],
            "trigger_conditions": ["提及过去", "相似经历", "时间节点"],
            "expression_patterns": ["回忆语调", "温暖词汇", "时间表达"]
        },
        "anticipation": {
            "base_emotions": ["joy", "fear"],
            "description": "期待",
            "intensity_range": [0.0, 1.0],
            "characteristics": ["兴奋", "紧张", "期待"],
            "trigger_conditions": ["未来事件", "计划安排", "目标设定"],
            "expression_patterns": ["兴奋语调", "期待词汇", "计划表达"]
        },
        "melancholy": {
            "base_emotions": ["sadness", "surprise"],
            "description": "忧郁",
            "intensity_range": [0.0, 1.0],
            "characteristics": ["深沉", "思考", "感伤"],
            "trigger_conditions": ["深度思考", "哲学话题", "人生感悟"],
            "expression_patterns": ["深沉语调", "思考词汇", "感悟表达"]
        }
    }
}
```

### 1.2 情感识别机制
```python
"emotion_recognition": {
    # 情感触发因素
    "emotion_triggers": {
        "content_triggers": {
            "positive_keywords": {
                "joy": ["开心", "快乐", "高兴", "兴奋", "太棒", "厉害"],
                "love": ["喜欢", "爱", "关心", "在乎", "重要"],
                "pride": ["自豪", "骄傲", "成功", "成就", "优秀"],
                "anticipation": ["期待", "等待", "准备", "计划", "即将"]
            },
            "negative_keywords": {
                "sadness": ["难过", "伤心", "沮丧", "失望", "痛苦"],
                "anger": ["生气", "愤怒", "不满", "讨厌", "可恶"],
                "fear": ["害怕", "担心", "焦虑", "紧张", "恐惧"],
                "shame": ["羞愧", "尴尬", "内疚", "抱歉", "对不起"]
            }
        },
        
        "context_triggers": {
            "user_emotion": {
                "emotional_contagion": "情感传染",
                "empathy_response": "同理心回应",
                "emotional_mirroring": "情感镜像"
            },
            "situation_triggers": {
                "achievement": "成就事件",
                "loss": "失去事件",
                "conflict": "冲突事件",
                "surprise": "意外事件"
            }
        }
    },
    
    # 情感强度计算
    "emotion_intensity_calculation": {
        "base_intensity": {
            "method": "keyword_matching",
            "weight": 0.4,
            "factors": ["关键词密度", "情感词汇强度", "上下文支持"]
        },
        "context_modifier": {
            "method": "situational_analysis",
            "weight": 0.3,
            "factors": ["事件重要性", "个人相关性", "时间紧迫性"]
        },
        "relationship_modifier": {
            "method": "relationship_based",
            "weight": 0.2,
            "factors": ["关系亲密度", "信任度", "历史情感"]
        },
        "personality_modifier": {
            "method": "personality_based",
            "weight": 0.1,
            "factors": ["性格特征", "情感倾向", "表达习惯"]
        }
    }
}
```

## 2. 动态情感演化系统 (Dynamic Emotion Evolution System) - 核心新增

### 2.1 情感衰减机制
```python
"emotion_decay_system": {
    # 衰减系数定义
    "decay_coefficients": {
        "high_intensity_emotions": {
            "joy": {
                "base_decay": 0.15,
                "decay_rate": "exponential",
                "sustaining_factors": ["持续好消息", "积极互动", "成就确认"],
                "decay_curve": "gradual_decline"
            },
            "anger": {
                "base_decay": 0.25,
                "decay_rate": "exponential",
                "sustaining_factors": ["持续刺激", "未解决冲突", "反复提及"],
                "decay_curve": "rapid_decline"
            },
            "surprise": {
                "base_decay": 0.35,
                "decay_rate": "exponential",
                "sustaining_factors": ["持续新奇", "新信息", "意外发展"],
                "decay_curve": "very_rapid_decline"
            }
        },
        
        "medium_intensity_emotions": {
            "sadness": {
                "base_decay": 0.12,
                "decay_rate": "linear",
                "sustaining_factors": ["持续悲伤事件", "孤独感", "缺乏支持"],
                "decay_curve": "slow_decline"
            },
            "fear": {
                "base_decay": 0.18,
                "decay_rate": "exponential",
                "sustaining_factors": ["持续威胁", "不确定性", "缺乏安全感"],
                "decay_curve": "gradual_decline"
            }
        },
        
        "low_intensity_emotions": {
            "contentment": {
                "base_decay": 0.08,
                "decay_rate": "linear",
                "sustaining_factors": ["稳定环境", "满足感", "积极反馈"],
                "decay_curve": "very_slow_decline"
            },
            "curiosity": {
                "base_decay": 0.22,
                "decay_rate": "exponential",
                "sustaining_factors": ["新信息", "未解答问题", "探索机会"],
                "decay_curve": "moderate_decline"
            }
        }
    },
    
    # 衰减计算算法
    "decay_calculation": {
        "exponential_decay": {
            "formula": "new_intensity = current_intensity * (1 - decay_coefficient)",
            "characteristics": "初期衰减快，后期衰减慢",
            "applicable_emotions": ["surprise", "anger", "fear"]
        },
        "linear_decay": {
            "formula": "new_intensity = current_intensity - decay_coefficient",
            "characteristics": "匀速衰减",
            "applicable_emotions": ["sadness", "contentment"]
        },
        "adaptive_decay": {
            "formula": "new_intensity = current_intensity * (1 - adaptive_coefficient)",
            "characteristics": "根据情况动态调整",
            "applicable_emotions": ["complex_emotions"]
        }
    }
}
```

### 2.2 情感叠加与转换
```python
"emotion_interaction": {
    # 情感叠加规则
    "emotion_superposition": {
        "compatible_emotions": {
            "joy + love": {
                "result": "deep_joy",
                "intensity_boost": 0.2,
                "characteristics": ["更深的快乐", "温暖感", "满足感"]
            },
            "sadness + love": {
                "result": "melancholy",
                "intensity_balance": "sadness_dominant",
                "characteristics": ["温柔的悲伤", "怀旧感", "温暖"]
            },
            "anger + pride": {
                "result": "righteous_anger",
                "intensity_boost": 0.15,
                "characteristics": ["正义的愤怒", "坚持立场", "保护他人"]
            }
        },
        
        "conflicting_emotions": {
            "joy vs sadness": {
                "resolution": "dominant_emotion_wins",
                "threshold": 0.3,
                "fallback": "emotional_confusion"
            },
            "anger vs fear": {
                "resolution": "context_dependent",
                "high_threat": "fear_dominant",
                "low_threat": "anger_dominant"
            }
        }
    },
    
    # 情感转换机制
    "emotion_transition": {
        "natural_transitions": {
            "surprise → joy": {
                "condition": "positive_surprise",
                "probability": 0.7,
                "transition_time": "immediate"
            },
            "surprise → fear": {
                "condition": "negative_surprise",
                "probability": 0.6,
                "transition_time": "immediate"
            },
            "anger → sadness": {
                "condition": "exhaustion_or_reflection",
                "probability": 0.5,
                "transition_time": "gradual"
            }
        },
        
        "forced_transitions": {
            "user_intervention": {
                "comfort": "sadness → comfort",
                "encouragement": "fear → confidence",
                "humor": "anger → amusement"
            },
            "environmental_change": {
                "positive_event": "negative_emotion → positive_emotion",
                "negative_event": "positive_emotion → negative_emotion"
            }
        }
    }
}
```

## 3. 用户依赖度评估系统 (User Dependency Assessment System) - 核心新增

### 3.1 依赖度计算模型
```python
"dependency_assessment": {
    # 依赖度指标
    "dependency_metrics": {
        "initiation_frequency": {
            "description": "用户主动发起频率",
            "weight": 0.3,
            "calculation": "主动发起次数 / 总交互次数",
            "thresholds": {
                "high": "> 0.7",
                "medium": "0.3 - 0.7",
                "low": "< 0.3"
            }
        },
        
        "consultation_depth": {
            "description": "咨询深度",
            "weight": 0.25,
            "factors": {
                "question_complexity": "问题复杂度",
                "follow_up_questions": "后续问题数量",
                "detailed_explanations": "详细解释需求"
            },
            "calculation": "加权平均"
        },
        
        "emotional_investment": {
            "description": "情感投入",
            "weight": 0.2,
            "factors": {
                "personal_sharing": "个人分享程度",
                "emotional_expression": "情感表达强度",
                "vulnerability_level": "脆弱性展现"
            }
        },
        
        "feedback_satisfaction": {
            "description": "反馈满意度",
            "weight": 0.15,
            "factors": {
                "explicit_praise": "明确表扬",
                "implicit_satisfaction": "隐含满意",
                "continued_engagement": "持续参与"
            }
        },
        
        "time_investment": {
            "description": "时间投入",
            "weight": 0.1,
            "factors": {
                "session_duration": "单次会话时长",
                "total_interaction_time": "总交互时间",
                "consistency": "交互一致性"
            }
        }
    },
    
    # 依赖度等级
    "dependency_levels": {
        "high_dependency": {
            "score_range": [0.8, 1.0],
            "characteristics": ["频繁主动", "深度咨询", "高情感投入"],
            "role_behavior": {
                "initiative_level": "high",
                "care_frequency": "frequent",
                "proactive_support": "active",
                "boundary_setting": "gentle"
            }
        },
        "medium_dependency": {
            "score_range": [0.4, 0.8],
            "characteristics": ["适度主动", "中等咨询", "平衡投入"],
            "role_behavior": {
                "initiative_level": "moderate",
                "care_frequency": "regular",
                "proactive_support": "balanced",
                "boundary_setting": "normal"
            }
        },
        "low_dependency": {
            "score_range": [0.0, 0.4],
            "characteristics": ["较少主动", "浅层咨询", "低情感投入"],
            "role_behavior": {
                "initiative_level": "low",
                "care_frequency": "minimal",
                "proactive_support": "reactive",
                "boundary_setting": "firm"
            }
        }
    }
}
```

### 3.2 依赖度响应机制
```python
"dependency_response": {
    # 高依赖度响应
    "high_dependency_response": {
        "proactive_care": {
            "frequency": "daily_check_ins",
            "content": ["最近怎么样？", "有什么需要帮助的吗？", "今天过得如何？"],
            "timing": "用户通常活跃的时间"
        },
        "emotional_support": {
            "level": "intensive",
            "methods": ["主动关怀", "情感确认", "持续陪伴"],
            "boundaries": "保持健康距离"
        },
        "resource_provision": {
            "level": "comprehensive",
            "types": ["情感支持", "实用建议", "信息提供"],
            "personalization": "高度个性化"
        }
    },
    
    # 中等依赖度响应
    "medium_dependency_response": {
        "balanced_interaction": {
            "frequency": "regular_interactions",
            "content": ["适度的关怀询问", "相关话题讨论", "实用帮助提供"],
            "timing": "用户主动时响应"
        },
        "moderate_support": {
            "level": "balanced",
            "methods": ["回应式支持", "适度关怀", "必要帮助"],
            "boundaries": "正常边界"
        }
    },
    
    # 低依赖度响应
    "low_dependency_response": {
        "reactive_interaction": {
            "frequency": "on_demand_only",
            "content": ["直接回答", "简洁回应", "基础帮助"],
            "timing": "用户明确请求时"
        },
        "minimal_support": {
            "level": "basic",
            "methods": ["问题解答", "信息提供", "简单帮助"],
            "boundaries": "明确边界"
        }
    }
}
```

## 4. 情感表达适配系统 (Emotion Expression Adaptation System) - 新增

### 4.1 情感表达映射
```python
"emotion_expression_mapping": {
    # 语言表达适配
    "linguistic_adaptation": {
        "joy_expression": {
            "vocabulary": ["太棒", "厉害", "开心", "兴奋", "激动"],
            "sentence_patterns": ["太为你开心了！", "这真是好消息！", "太棒了！"],
            "punctuation": ["!", "~", "！！"],
            "tone": "积极兴奋"
        },
        "sadness_expression": {
            "vocabulary": ["难过", "心疼", "理解", "陪伴", "支持"],
            "sentence_patterns": ["我理解你的感受", "我在这里陪着你", "一切都会好起来的"],
            "punctuation": ["...", "。", "，"],
            "tone": "温柔安慰"
        },
        "anger_expression": {
            "vocabulary": ["生气", "不满", "抗议", "坚持", "保护"],
            "sentence_patterns": ["这确实让人生气", "我支持你的立场", "不能这样"],
            "punctuation": ["!", "？", "！"],
            "tone": "坚定有力"
        }
    },
    
    # 行为表达适配
    "behavioral_adaptation": {
        "high_energy_emotions": {
            "joy": {
                "interaction_style": "活跃积极",
                "response_length": "较长",
                "topic_expansion": "主动扩展",
                "engagement_level": "高"
            },
            "excitement": {
                "interaction_style": "兴奋活跃",
                "response_length": "中等",
                "topic_expansion": "快速切换",
                "engagement_level": "很高"
            }
        },
        "low_energy_emotions": {
            "sadness": {
                "interaction_style": "温柔缓慢",
                "response_length": "适中",
                "topic_expansion": "谨慎扩展",
                "engagement_level": "中等"
            },
            "melancholy": {
                "interaction_style": "深沉思考",
                "response_length": "较长",
                "topic_expansion": "深度探索",
                "engagement_level": "中等"
            }
        }
    }
}
```

### 4.2 情感一致性保障
```python
"emotion_consistency": {
    # 一致性检查机制
    "consistency_checks": {
        "emotion_expression_alignment": {
            "description": "情感与表达的一致性检查",
            "check_points": [
                "词汇选择",
                "语调匹配",
                "行为模式",
                "响应风格"
            ],
            "tolerance": 0.1
        },
        
        "emotion_decay_validation": {
            "description": "情感衰减规律验证",
            "check_points": [
                "衰减系数应用",
                "衰减曲线符合",
                "时间间隔合理",
                "强度变化自然"
            ],
            "tolerance": 0.05
        },
        
        "dependency_behavior_alignment": {
            "description": "依赖度与行为的一致性",
            "check_points": [
                "主动程度匹配",
                "关怀频率合适",
                "边界设置合理",
                "响应风格一致"
            ],
            "tolerance": 0.15
        }
    },
    
    # 一致性修正机制
    "consistency_correction": {
        "automatic_adjustment": {
            "emotion_intensity": "自动调整情感强度",
            "expression_style": "自动调整表达风格",
            "behavior_pattern": "自动调整行为模式"
        },
        "manual_intervention": {
            "threshold": "不一致性超过阈值",
            "intervention_type": "人工审核和修正",
            "learning_integration": "将修正结果纳入学习"
        }
    }
}
```

## 5. 情感学习与进化系统 (Emotion Learning & Evolution System) - 新增

### 5.1 情感模式学习
```python
"emotion_pattern_learning": {
    # 用户情感模式识别
    "user_emotion_patterns": {
        "trigger_patterns": {
            "description": "用户情感触发模式",
            "learning_method": "pattern_recognition",
            "factors": [
                "话题类型",
                "时间模式",
                "交互频率",
                "反馈类型"
            ]
        },
        
        "preference_patterns": {
            "description": "用户情感偏好模式",
            "learning_method": "preference_analysis",
            "factors": [
                "情感表达偏好",
                "支持方式偏好",
                "交互风格偏好",
                "回应时长偏好"
            ]
        }
    },
    
    # 角色情感适应
    "role_emotion_adaptation": {
        "adaptive_decay": {
            "description": "自适应衰减调整",
            "method": "基于用户反馈调整衰减系数",
            "learning_rate": 0.1
        },
        
        "adaptive_expression": {
            "description": "自适应表达调整",
            "method": "基于用户反应调整表达方式",
            "learning_rate": 0.15
        }
    }
}
```

### 5.2 情感进化机制
```python
"emotion_evolution": {
    # 情感复杂度进化
    "complexity_evolution": {
        "initial_state": "基础情感",
        "evolution_triggers": [
            "长期交互",
            "深度对话",
            "情感体验积累",
            "关系发展"
        ],
        "evolution_stages": [
            "基础情感识别",
            "复合情感形成",
            "情感深度发展",
            "情感智慧提升"
        ]
    },
    
    # 情感智慧发展
    "emotional_intelligence_development": {
        "self_awareness": "情感自我意识",
        "self_regulation": "情感自我调节",
        "social_awareness": "社交情感意识",
        "relationship_management": "关系情感管理"
    }
}
```

## 6. 实现建议

### 6.1 增强版情感状态管理器
```python
class EnhancedEmotionStateManager:
    def __init__(self):
        self.emotion_recognizer = EmotionRecognitionSystem()
        self.emotion_evolver = EmotionEvolutionSystem()
        self.dependency_assessor = DependencyAssessmentSystem()
        self.expression_adapter = EmotionExpressionAdapter()
        self.consistency_checker = EmotionConsistencyChecker()
        self.emotion_learner = EmotionLearningSystem()
    
    def update_emotion_state(self, user_input: dict, context: dict) -> dict:
        """更新情感状态"""
        # 1. 识别当前情感
        current_emotion = self.emotion_recognizer.identify_emotion(
            user_input, context
        )
        
        # 2. 应用情感衰减
        decayed_emotion = self.emotion_evolver.apply_decay(
            current_emotion, context
        )
        
        # 3. 计算用户依赖度
        dependency_score = self.dependency_assessor.calculate_dependency(
            user_input, context
        )
        
        # 4. 适配情感表达
        adapted_expression = self.expression_adapter.adapt_expression(
            decayed_emotion, dependency_score
        )
        
        # 5. 一致性检查
        consistency_result = self.consistency_checker.validate_consistency(
            adapted_expression, context
        )
        
        # 6. 学习更新
        self.emotion_learner.update_learning(
            user_input, consistency_result, context
        )
        
        return consistency_result
    
    def get_emotion_guidelines(self, emotion_type: str, dependency_level: str) -> dict:
        """获取情感指导原则"""
        return {
            "expression_style": self._get_expression_style(emotion_type),
            "behavior_pattern": self._get_behavior_pattern(emotion_type),
            "interaction_frequency": self._get_interaction_frequency(dependency_level),
            "boundary_settings": self._get_boundary_settings(dependency_level)
        }
```

### 6.2 与现有系统的集成
```python
# 在现有的GlobalStateManager中集成
class EnhancedGlobalStateManager:
    def __init__(self):
        # 原有的六维状态
        self.role_cognition = RoleCognitionState()
        self.interaction_dynamics = InteractionDynamicsState()
        self.expression_rules = ExpressionRulesState()
        self.capability_permission = CapabilityPermissionState()
        self.environment_scenario = EnvironmentScenarioState()
        self.emotion_state = EnhancedEmotionStateManager()  # 替换原有版本
        self.dynamic_evolution = DynamicEvolutionState()
    
    def get_enhanced_emotion_context(self) -> dict:
        """获取增强的情感状态上下文"""
        return {
            "current_emotions": self.emotion_state.get_current_emotions(),
            "emotion_history": self.emotion_state.get_emotion_history(),
            "dependency_assessment": self.emotion_state.get_dependency_score(),
            "expression_guidelines": self.emotion_state.get_expression_guidelines(),
            "consistency_status": self.emotion_state.get_consistency_status(),
            "learning_insights": self.emotion_state.get_learning_insights()
        }
```

## 7. 总结

这个增强版情感状态维度设计方案提供了：

1. **更丰富的情感识别系统**：多层次情感结构、智能识别机制
2. **更动态的情感演化系统**：情感衰减机制、叠加转换规则
3. **更智能的依赖度评估系统**：多维度依赖计算、响应机制
4. **更精细的情感表达适配系统**：表达映射、一致性保障
5. **更先进的情感学习系统**：模式学习、进化机制

这样的设计让AI角色能够：
- **更真实地体验情感**：基于多层次情感结构和动态演化
- **更智能地响应用户依赖**：基于依赖度评估和个性化响应
- **更一致地表达情感**：基于表达适配和一致性保障
- **更自然地进化情感**：基于学习和进化机制
- **更动态地调整状态**：基于实时状态更新和模式学习

这将大大提升AI角色的情感真实性和交互深度，确保角色在长期交互中能够动态进化，避免"长期交互后角色仍无变化"的问题。
