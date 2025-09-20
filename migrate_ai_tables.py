#!/usr/bin/env python3
"""
AI角色系统数据库迁移脚本
为现有表添加AI角色相关字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db import mysql_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """执行数据库迁移"""
    try:
        # 连接数据库
        if not mysql_db.connect():
            logger.error("数据库连接失败")
            return False
        
        session = mysql_db.get_session()
        
        # 1. 创建AI角色表
        logger.info("创建AI角色表...")
        create_ai_character_table = """
        CREATE TABLE IF NOT EXISTS ai_character (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            character_id VARCHAR(32) UNIQUE NOT NULL COMMENT 'AI角色唯一标识',
            name VARCHAR(100) NOT NULL COMMENT '角色名称',
            nickname VARCHAR(100) NOT NULL COMMENT '角色昵称',
            avatar VARCHAR(500) COMMENT '角色头像URL',
            description TEXT COMMENT '角色描述',
            personality TEXT COMMENT '人设描述',
            background_story TEXT COMMENT '背景故事',
            speaking_style TEXT COMMENT '说话风格',
            creator_id BIGINT NOT NULL COMMENT '创建者用户ID',
            is_public BOOLEAN DEFAULT FALSE COMMENT '是否公开',
            status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-禁用',
            usage_count INT DEFAULT 0 COMMENT '使用次数',
            like_count INT DEFAULT 0 COMMENT '点赞数',
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) COMMENT='AI角色信息表'
        """
        session.execute(text(create_ai_character_table))
        
        # 2. 创建用户-AI关系表
        logger.info("创建用户-AI关系表...")
        create_user_ai_relation_table = """
        CREATE TABLE IF NOT EXISTS user_ai_relation (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            user_id BIGINT NOT NULL COMMENT '用户ID',
            character_id VARCHAR(32) NOT NULL COMMENT 'AI角色ID',
            relation_type ENUM('created', 'favorited', 'blocked') NOT NULL COMMENT '关系类型',
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) COMMENT='用户与AI角色关联关系表'
        """
        session.execute(text(create_user_ai_relation_table))
        
        # 3. 检查并添加conversations表的新字段
        logger.info("检查conversations表结构...")
        check_conversation_type = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'conversations' 
        AND COLUMN_NAME = 'conversation_type'
        """
        result = session.execute(text(check_conversation_type)).fetchone()
        
        if not result:
            logger.info("添加conversation_type字段...")
            add_conversation_type = """
            ALTER TABLE conversations 
            ADD COLUMN conversation_type ENUM('user_user', 'user_ai') DEFAULT 'user_user' COMMENT '会话类型'
            """
            session.execute(text(add_conversation_type))
        else:
            logger.info("conversation_type字段已存在")
        
        # 检查并添加ai_character_id字段
        check_ai_character_id = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'conversations' 
        AND COLUMN_NAME = 'ai_character_id'
        """
        result = session.execute(text(check_ai_character_id)).fetchone()
        
        if not result:
            logger.info("添加ai_character_id字段...")
            add_ai_character_id = """
            ALTER TABLE conversations 
            ADD COLUMN ai_character_id VARCHAR(32) NULL COMMENT 'AI角色ID（当conversation_type为user_ai时使用）'
            """
            session.execute(text(add_ai_character_id))
        else:
            logger.info("ai_character_id字段已存在")
        
        # 4. 检查并添加messages表的新字段
        logger.info("检查messages表结构...")
        check_is_ai_message = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'messages' 
        AND COLUMN_NAME = 'is_ai_message'
        """
        result = session.execute(text(check_is_ai_message)).fetchone()
        
        if not result:
            logger.info("添加is_ai_message字段...")
            add_is_ai_message = """
            ALTER TABLE messages 
            ADD COLUMN is_ai_message BOOLEAN DEFAULT FALSE COMMENT '是否为AI消息'
            """
            session.execute(text(add_is_ai_message))
        else:
            logger.info("is_ai_message字段已存在")
        
        # 检查并添加ai_character_id字段到messages表
        check_messages_ai_character_id = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'messages' 
        AND COLUMN_NAME = 'ai_character_id'
        """
        result = session.execute(text(check_messages_ai_character_id)).fetchone()
        
        if not result:
            logger.info("添加messages表的ai_character_id字段...")
            add_messages_ai_character_id = """
            ALTER TABLE messages 
            ADD COLUMN ai_character_id VARCHAR(32) NULL COMMENT 'AI角色ID（当is_ai_message为true时使用）'
            """
            session.execute(text(add_messages_ai_character_id))
        else:
            logger.info("messages表的ai_character_id字段已存在")
        
        # 提交更改
        session.commit()
        logger.info("✅ 数据库迁移完成")
        
        # 关闭会话
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

if __name__ == "__main__":
    print("🚀 开始AI角色系统数据库迁移...")
    if migrate_database():
        print("🎉 数据库迁移成功完成！")
    else:
        print("❌ 数据库迁移失败！")
        sys.exit(1)
