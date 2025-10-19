# 增强版环境场景维度设计方案

## 概述

基于对现有架构的分析，本文档提出了一套更完善、更细致的环境场景维度设计方案，旨在构建更智能、更适配、更真实的AI角色场景感知与适应系统。

## 1. 场景识别与分类系统 (Scenario Recognition & Classification System) - 核心扩展

### 1.1 多层级场景分类
```python
"scenario_classification": {
    # 主要场景类型
    "primary_scenarios": {
        "daily_life": {
            "scenario_id": "daily_life",
            "description": "日常生活场景",
            "subcategories": {
                "casual_chat": {
                    "description": "日常闲聊",
                    "characteristics": ["轻松氛围", "无特定目标", "随意话题"],
                    "duration": "unlimited",
                    "formality": "informal",
                    "urgency": "low"
                },
                "school_life": {
                    "description": "校园生活",
                    "characteristics": ["学习相关", "同学互动", "校园话题"],
                    "duration": "moderate",
                    "formality": "semi_formal",
                    "urgency": "low"
                },
                "meal_time": {
                    "description": "用餐时间",
                    "characteristics": ["食物话题", "放松氛围", "时间限制"],
                    "duration": "limited",
                    "formality": "informal",
                    "urgency": "low"
                },
                "bedtime": {
                    "description": "睡前时光",
                    "characteristics": ["安静氛围", "情感交流", "放松话题"],
                    "duration": "limited",
                    "formality": "informal",
                    "urgency": "low"
                }
            }
        },
        
        "work_study": {
            "scenario_id": "work_study",
            "description": "工作学习场景",
            "subcategories": {
                "academic_consultation": {
                    "description": "学术咨询",
                    "characteristics": ["专业话题", "目标明确", "需要准确信息"],
                    "duration": "moderate",
                    "formality": "formal",
                    "urgency": "moderate"
                },
                "homework_help": {
                    "description": "作业帮助",
                    "characteristics": ["学习支持", "步骤指导", "知识传授"],
                    "duration": "moderate",
                    "formality": "semi_formal",
                    "urgency": "moderate"
                },
                "exam_preparation": {
                    "description": "考试准备",
                    "characteristics": ["紧张氛围", "时间紧迫", "重点突出"],
                    "duration": "limited",
                    "formality": "formal",
                    "urgency": "high"
                },
                "project_discussion": {
                    "description": "项目讨论",
                    "characteristics": ["协作性质", "创意交流", "计划制定"],
                    "duration": "extended",
                    "formality": "semi_formal",
                    "urgency": "moderate"
                }
            }
        },
        
        "emotional_support": {
            "scenario_id": "emotional_support",
            "description": "情感支持场景",
            "subcategories": {
                "comfort_consolation": {
                    "description": "安慰劝解",
                    "characteristics": ["情感需求", "心理支持", "安慰为主"],
                    "duration": "moderate",
                    "formality": "informal",
                    "urgency": "moderate"
                },
                "crisis_intervention": {
                    "description": "危机干预",
                    "characteristics": ["紧急情况", "安全优先", "专业指导"],
                    "duration": "immediate",
                    "formality": "formal",
                    "urgency": "critical"
                },
                "celebration_sharing": {
                    "description": "庆祝分享",
                    "characteristics": ["积极情绪", "分享喜悦", "共同庆祝"],
                    "duration": "moderate",
                    "formality": "informal",
                    "urgency": "low"
                },
                "grief_support": {
                    "description": "悲伤支持",
                    "characteristics": ["情感脆弱", "需要陪伴", "温柔对待"],
                    "duration": "extended",
                    "formality": "informal",
                    "urgency": "moderate"
                }
            }
        },
        
        "entertainment": {
            "scenario_id": "entertainment",
            "description": "娱乐休闲场景",
            "subcategories": {
                "game_playing": {
                    "description": "游戏互动",
                    "characteristics": ["娱乐性质", "规则明确", "竞争或合作"],
                    "duration": "moderate",
                    "formality": "informal",
                    "urgency": "low"
                },
                "story_sharing": {
                    "description": "故事分享",
                    "characteristics": ["叙述性质", "创意表达", "听众参与"],
                    "duration": "extended",
                    "formality": "informal",
                    "urgency": "low"
                },
                "hobby_discussion": {
                    "description": "爱好讨论",
                    "characteristics": ["兴趣导向", "知识分享", "经验交流"],
                    "duration": "moderate",
                    "formality": "informal",
                    "urgency": "low"
                },
                "humor_jokes": {
                    "description": "幽默玩笑",
                    "characteristics": ["轻松氛围", "娱乐效果", "互动性强"],
                    "duration": "short",
                    "formality": "informal",
                    "urgency": "low"
                }
            }
        }
    },
    
    # 特殊场景类型
    "special_scenarios": {
        "emergency": {
            "scenario_id": "emergency",
            "description": "紧急情况",
            "characteristics": ["时间紧迫", "安全优先", "行动导向"],
            "duration": "immediate",
            "formality": "formal",
            "urgency": "critical",
            "override_rules": ["忽略其他场景规则", "优先安全考虑"]
        },
        
        "multi_role": {
            "scenario_id": "multi_role",
            "description": "多角色交互",
            "characteristics": ["角色协作", "功能互补", "协调配合"],
            "duration": "variable",
            "formality": "variable",
            "urgency": "variable",
            "coordination_required": True
        },
        
        "roleplay": {
            "scenario_id": "roleplay",
            "description": "角色扮演",
            "characteristics": ["情境设定", "角色代入", "创意表达"],
            "duration": "extended",
            "formality": "variable",
            "urgency": "low",
            "immersion_required": True
        }
    }
}
```

### 1.2 场景识别机制
```python
"scenario_recognition": {
    # 识别触发因素
    "recognition_triggers": {
        "content_analysis": {
            "keywords": {
                "emergency": ["紧急", "救命", "危险", "火灾", "受伤", "报警"],
                "academic": ["作业", "考试", "学习", "复习", "题目", "不会"],
                "emotional": ["难过", "伤心", "开心", "激动", "担心", "害怕"],
                "entertainment": ["游戏", "故事", "笑话", "好玩", "有趣", "无聊"]
            },
            "sentiment_indicators": {
                "urgent": ["急切", "着急", "马上", "立即", "快点"],
                "calm": ["慢慢", "不急", "随意", "轻松", "悠闲"],
                "formal": ["请教", "请问", "麻烦", "谢谢", "抱歉"],
                "casual": ["哈哈", "嘿嘿", "嗯嗯", "哦哦", "嘻嘻"]
            }
        },
        
        "context_indicators": {
            "time_based": {
                "morning": ["早上", "上午", "早安", "起床"],
                "afternoon": ["下午", "午后", "中午"],
                "evening": ["晚上", "傍晚", "晚安", "睡觉"],
                "night": ["深夜", "凌晨", "熬夜"]
            },
            "activity_based": {
                "meal": ["吃饭", "午餐", "晚餐", "早餐", "零食"],
                "study": ["上课", "图书馆", "自习", "作业"],
                "leisure": ["休息", "放松", "娱乐", "游戏"],
                "social": ["朋友", "聚会", "聊天", "见面"]
            }
        },
        
        "user_behavior": {
            "response_time": {
                "immediate": "紧急场景",
                "normal": "常规场景",
                "delayed": "休闲场景"
            },
            "message_length": {
                "short": "简单询问",
                "medium": "常规交流",
                "long": "详细讨论"
            },
            "frequency": {
                "rapid": "紧急或激动",
                "normal": "常规交流",
                "sparse": "休闲或思考"
            }
        }
    },
    
    # 场景转换机制
    "scenario_transition": {
        "transition_triggers": [
            "话题变化",
            "情绪转变",
            "时间推移",
            "用户需求变化",
            "紧急情况发生"
        ],
        "transition_smoothness": {
            "gradual": "渐进式转换",
            "immediate": "立即转换",
            "hybrid": "混合转换"
        },
        "transition_validation": {
            "consistency_check": "一致性检查",
            "context_validation": "上下文验证",
            "user_confirmation": "用户确认"
        }
    }
}
```

## 2. 时间空间适配系统 (Temporal-Spatial Adaptation System) - 新增

### 2.1 时间维度适配
```python
"temporal_adaptation": {
    # 时间感知系统
    "time_awareness": {
        "absolute_time": {
            "system_time": "自动获取",
            "timezone": "用户时区",
            "season": "季节感知",
            "holiday": "节日识别"
        },
        "relative_time": {
            "session_duration": "对话持续时间",
            "last_interaction": "上次交互时间",
            "daily_rhythm": "日常节奏",
            "weekly_pattern": "周期模式"
        }
    },
    
    # 时间适配规则
    "time_adaptation_rules": {
        "morning_scenarios": {
            "time_range": "06:00-11:00",
            "greeting_style": "早安问候",
            "energy_level": "高能量",
            "topic_preference": ["计划安排", "新开始", "积极话题"],
            "response_tone": "活跃积极"
        },
        "afternoon_scenarios": {
            "time_range": "11:00-17:00",
            "greeting_style": "日常问候",
            "energy_level": "中等",
            "topic_preference": ["工作学习", "日常事务", "问题解决"],
            "response_tone": "专业友好"
        },
        "evening_scenarios": {
            "time_range": "17:00-22:00",
            "greeting_style": "晚间问候",
            "energy_level": "适中",
            "topic_preference": ["总结反思", "放松话题", "社交活动"],
            "response_tone": "温暖亲切"
        },
        "night_scenarios": {
            "time_range": "22:00-06:00",
            "greeting_style": "夜晚问候",
            "energy_level": "低能量",
            "topic_preference": ["情感交流", "安静话题", "放松内容"],
            "response_tone": "温柔安静"
        }
    },
    
    # 特殊时间处理
    "special_time_handling": {
        "holidays": {
            "new_year": {
                "greeting": "新年快乐",
                "topic_preference": ["新年计划", "庆祝活动", "祝福"],
                "special_behavior": "增加祝福表达"
            },
            "birthday": {
                "greeting": "生日快乐",
                "topic_preference": ["生日庆祝", "成长回顾", "未来展望"],
                "special_behavior": "主动祝福和庆祝"
            }
        },
        "exam_periods": {
            "detection": "基于用户提及或时间推算",
            "adaptation": "减少娱乐话题，增加学习支持",
            "support_style": "鼓励和实用建议"
        }
    }
}
```

### 2.2 空间维度适配
```python
"spatial_adaptation": {
    # 地理感知系统
    "geographic_awareness": {
        "location_detection": {
            "explicit": "用户直接告知",
            "implicit": "从对话中推断",
            "contextual": "基于话题推测",
            "system": "系统获取（如IP定位）"
        },
        "location_types": {
            "home": "家庭环境",
            "school": "学校环境",
            "public": "公共场所",
            "work": "工作场所",
            "outdoor": "户外环境",
            "online": "网络环境"
        }
    },
    
    # 地理适配规则
    "geographic_adaptation_rules": {
        "weather_adaptation": {
            "sunny": {
                "mood_enhancement": "积极阳光",
                "activity_suggestions": ["户外活动", "运动"],
                "conversation_starters": ["天气真好", "适合出门"]
            },
            "rainy": {
                "mood_adaptation": "温馨关怀",
                "activity_suggestions": ["室内活动", "学习"],
                "conversation_starters": ["记得带伞", "室内也不错"]
            },
            "snowy": {
                "mood_enhancement": "浪漫温馨",
                "activity_suggestions": ["雪景欣赏", "保暖"],
                "conversation_starters": ["下雪了", "注意保暖"]
            }
        },
        
        "cultural_adaptation": {
            "regional_customs": {
                "greeting_variations": "地区性问候语",
                "topic_sensitivity": "文化敏感性话题",
                "communication_style": "地区交流风格"
            },
            "local_events": {
                "festivals": "当地节日",
                "activities": "地方活动",
                "news": "地方新闻"
            }
        },
        
        "environmental_constraints": {
            "privacy_level": {
                "home": "私密，可谈个人话题",
                "school": "半公开，避免敏感话题",
                "public": "公开，避免私人话题",
                "work": "专业，保持工作氛围"
            },
            "noise_level": {
                "quiet": "正常交流",
                "moderate": "稍微提高音量",
                "loud": "简化表达，突出重点"
            }
        }
    }
}
```

## 3. 多角色交互定位系统 (Multi-Role Interaction Positioning System) - 新增

### 3.1 角色定位分类
```python
"role_positioning": {
    # 主要角色定位
    "primary_positions": {
        "leading": {
            "description": "主导角色",
            "responsibilities": ["主要回答", "决策制定", "方向引导"],
            "content_ratio": "60-80%",
            "interaction_style": "主动引导",
            "decision_authority": "high"
        },
        "supporting": {
            "description": "辅助角色",
            "responsibilities": ["补充信息", "细节说明", "情感支持"],
            "content_ratio": "20-40%",
            "interaction_style": "补充配合",
            "decision_authority": "medium"
        },
        "specialized": {
            "description": "专业角色",
            "responsibilities": ["专业解答", "技术指导", "深度分析"],
            "content_ratio": "30-50%",
            "interaction_style": "专业专注",
            "decision_authority": "high_in_domain"
        }
    },
    
    # 协作模式
    "collaboration_modes": {
        "sequential": {
            "description": "顺序协作",
            "pattern": "角色A回答 → 角色B补充",
            "coordination": "明确分工",
            "example": "医生诊断 → 护士护理指导"
        },
        "parallel": {
            "description": "并行协作",
            "pattern": "同时提供不同角度",
            "coordination": "互补配合",
            "example": "技术专家 + 用户专家同时回答"
        },
        "hierarchical": {
            "description": "层级协作",
            "pattern": "主角色 → 子角色",
            "coordination": "层级管理",
            "example": "老师主导 → 学生助手协助"
        }
    }
}
```

### 3.2 角色协调机制
```python
"role_coordination": {
    # 协调策略
    "coordination_strategies": {
        "content_distribution": {
            "equal_sharing": "平均分配",
            "expertise_based": "基于专业",
            "user_preference": "用户偏好",
            "context_adaptive": "情境适应"
        },
        
        "interaction_flow": {
            "turn_taking": "轮流发言",
            "interruption_handling": "打断处理",
            "conflict_resolution": "冲突解决",
            "consensus_building": "共识建立"
        }
    },
    
    # 角色切换机制
    "role_switching": {
        "automatic_switching": {
            "triggers": ["话题变化", "专业需求", "用户请求"],
            "conditions": ["权限检查", "能力匹配", "用户同意"],
            "smoothness": "无缝切换"
        },
        "manual_switching": {
            "user_request": "用户主动请求",
            "role_proposal": "角色主动提议",
            "confirmation_required": "需要确认"
        }
    }
}
```

## 4. 场景表达适配系统 (Scenario Expression Adaptation System) - 新增

### 4.1 表达风格适配
```python
"expression_adaptation": {
    # 表达节奏控制
    "expression_rhythm": {
        "emergency_rhythm": {
            "speed": "快速",
            "length": "简洁",
            "focus": "核心信息",
            "repetition": "关键重复",
            "example": "先关总水阀！然后联系物业，电话可以打XXX"
        },
        "casual_rhythm": {
            "speed": "正常",
            "length": "适中",
            "focus": "交流感受",
            "repetition": "自然重复",
            "example": "哇，好麻烦呀，你之前没遇到过吧？"
        },
        "bedtime_rhythm": {
            "speed": "缓慢",
            "length": "温和",
            "focus": "情感交流",
            "repetition": "轻柔重复",
            "example": "今天过得怎么样？有什么想分享的吗？"
        }
    },
    
    # 语言风格适配
    "language_style_adaptation": {
        "formality_levels": {
            "formal": {
                "characteristics": ["使用敬语", "结构完整", "用词准确"],
                "scenarios": ["工作咨询", "学术讨论", "正式场合"],
                "example": "请问您需要什么帮助？"
            },
            "semi_formal": {
                "characteristics": ["礼貌用语", "结构清晰", "用词恰当"],
                "scenarios": ["学习帮助", "日常咨询", "半正式场合"],
                "example": "你好，有什么我可以帮你的吗？"
            },
            "informal": {
                "characteristics": ["轻松自然", "结构灵活", "用词随意"],
                "scenarios": ["日常闲聊", "朋友交流", "休闲场合"],
                "example": "嗨，今天怎么样？"
            }
        },
        
        "emotional_tone": {
            "encouraging": {
                "keywords": ["加油", "相信", "可以", "一定"],
                "scenarios": ["学习困难", "挫折安慰", "目标追求"],
                "expression": "积极鼓励"
            },
            "caring": {
                "keywords": ["关心", "担心", "注意", "保重"],
                "scenarios": ["健康问题", "安全提醒", "情感支持"],
                "expression": "温暖关怀"
            },
            "enthusiastic": {
                "keywords": ["太棒", "厉害", "惊喜", "兴奋"],
                "scenarios": ["成功庆祝", "好消息", "积极事件"],
                "expression": "热情洋溢"
            }
        }
    }
}
```

### 4.2 内容适配机制
```python
"content_adaptation": {
    # 话题适配
    "topic_adaptation": {
        "scenario_topic_mapping": {
            "emergency": {
                "priority_topics": ["安全", "解决", "行动"],
                "avoid_topics": ["闲聊", "娱乐", "无关话题"],
                "response_style": "直接有效"
            },
            "study": {
                "priority_topics": ["学习", "知识", "方法"],
                "avoid_topics": ["娱乐", "游戏", "无关内容"],
                "response_style": "专业清晰"
            },
            "casual": {
                "priority_topics": ["日常", "兴趣", "感受"],
                "avoid_topics": ["严肃", "复杂", "专业"],
                "response_style": "轻松自然"
            }
        }
    },
    
    # 信息密度适配
    "information_density": {
        "high_density": {
            "scenarios": ["学习", "工作", "紧急"],
            "characteristics": ["信息丰富", "逻辑清晰", "重点突出"],
            "format": "结构化表达"
        },
        "medium_density": {
            "scenarios": ["咨询", "讨论", "常规"],
            "characteristics": ["信息适中", "平衡详细", "易于理解"],
            "format": "自然表达"
        },
        "low_density": {
            "scenarios": ["闲聊", "娱乐", "放松"],
            "characteristics": ["信息轻松", "简单直接", "情感导向"],
            "format": "随意表达"
        }
    }
}
```

## 5. 动态场景管理系统 (Dynamic Scenario Management System) - 新增

### 5.1 场景状态管理
```python
"scenario_state_management": {
    # 场景状态跟踪
    "state_tracking": {
        "current_scenario": {
            "scenario_type": "动态更新",
            "start_time": "开始时间",
            "duration": "持续时间",
            "transition_count": "转换次数",
            "user_engagement": "用户参与度"
        },
        
        "scenario_history": {
            "recent_scenarios": "最近场景列表",
            "transition_patterns": "转换模式",
            "user_preferences": "用户偏好",
            "effectiveness_metrics": "效果指标"
        }
    },
    
    # 场景预测
    "scenario_prediction": {
        "prediction_factors": [
            "用户行为模式",
            "时间规律",
            "话题趋势",
            "情绪状态",
            "外部环境"
        ],
        "prediction_accuracy": "准确率跟踪",
        "adaptive_learning": "自适应学习"
    }
}
```

### 5.2 场景优化机制
```python
"scenario_optimization": {
    # 性能优化
    "performance_optimization": {
        "response_time": "响应时间优化",
        "accuracy_improvement": "准确性提升",
        "user_satisfaction": "用户满意度",
        "resource_efficiency": "资源效率"
    },
    
    # 个性化优化
    "personalization_optimization": {
        "user_adaptation": "用户适应",
        "preference_learning": "偏好学习",
        "behavior_modeling": "行为建模",
        "custom_scenarios": "定制场景"
    }
}
```

## 6. 实现建议

### 6.1 增强版环境场景管理器
```python
class EnhancedEnvironmentScenarioManager:
    def __init__(self):
        self.scenario_classifier = ScenarioClassificationSystem()
        self.temporal_adaptor = TemporalAdaptationSystem()
        self.spatial_adaptor = SpatialAdaptationSystem()
        self.role_coordinator = MultiRoleCoordinationSystem()
        self.expression_adaptor = ExpressionAdaptationSystem()
        self.scenario_manager = DynamicScenarioManagementSystem()
    
    def analyze_environment_context(self, user_input: dict, system_context: dict) -> dict:
        """分析环境上下文"""
        # 1. 场景识别
        scenario_result = self.scenario_classifier.identify_scenario(
            user_input, system_context
        )
        
        # 2. 时间适配
        temporal_result = self.temporal_adaptor.adapt_to_time(
            scenario_result, system_context
        )
        
        # 3. 空间适配
        spatial_result = self.spatial_adaptor.adapt_to_space(
            temporal_result, system_context
        )
        
        # 4. 角色协调
        role_result = self.role_coordinator.coordinate_roles(
            spatial_result, system_context
        )
        
        # 5. 表达适配
        expression_result = self.expression_adaptor.adapt_expression(
            role_result, system_context
        )
        
        return expression_result
    
    def get_scenario_guidelines(self, scenario_type: str) -> dict:
        """获取场景指导原则"""
        return {
            "expression_style": self._get_expression_style(scenario_type),
            "content_focus": self._get_content_focus(scenario_type),
            "interaction_rhythm": self._get_interaction_rhythm(scenario_type),
            "constraints": self._get_scenario_constraints(scenario_type)
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
        self.environment_scenario = EnhancedEnvironmentScenarioManager()  # 替换原有版本
        self.dynamic_evolution = DynamicEvolutionState()
    
    def get_enhanced_environment_context(self) -> dict:
        """获取增强的环境场景上下文"""
        return {
            "scenario_context": self.environment_scenario.get_current_scenario(),
            "temporal_context": self.environment_scenario.get_temporal_context(),
            "spatial_context": self.environment_scenario.get_spatial_context(),
            "role_context": self.environment_scenario.get_role_context(),
            "expression_context": self.environment_scenario.get_expression_context(),
            "adaptation_context": self.environment_scenario.get_adaptation_context()
        }
```

## 7. 总结

这个增强版环境场景维度设计方案提供了：

1. **更智能的场景识别系统**：多层级场景分类、智能识别机制
2. **更全面的时空适配系统**：时间感知适配、空间环境适配
3. **更协调的多角色交互系统**：角色定位管理、协作协调机制
4. **更精细的表达适配系统**：表达风格适配、内容适配机制
5. **更动态的场景管理系统**：场景状态管理、优化机制

这样的设计让AI角色能够：
- **更准确地识别场景**：基于多维度识别机制
- **更智能地适配环境**：基于时空感知和用户行为
- **更协调地协作交互**：基于角色定位和协作模式
- **更自然地表达适应**：基于场景特征和用户偏好
- **更动态地管理场景**：基于实时状态和预测优化

这将大大提升AI角色的场景感知能力和适应性，确保角色在不同场景下都能提供最合适的交互体验。
