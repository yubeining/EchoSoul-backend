#!/usr/bin/env python3
"""
WebSocket AI聊天消息保存问题排查脚本
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import mysql_db, initialize_databases
from app.models.chat_models import Message, Conversation
from app.models.ai_character_models import AICharacter
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta

def check_database_connection():
    """检查数据库连接"""
    print("🔍 检查数据库连接...")
    try:
        # 先初始化数据库
        print("🔧 初始化数据库连接...")
        db_results = initialize_databases()
        print(f"📊 数据库初始化结果: {db_results}")
        
        if db_results.get("mysql", {}).get("status") != "connected":
            print("❌ MySQL数据库连接失败")
            return False
        
        db = mysql_db.get_session()
        # 测试查询
        from sqlalchemy import text
        result = db.execute(text("SELECT 1")).fetchone()
        print(f"✅ 数据库连接正常: {result}")
        db.close()
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def check_recent_messages():
    """检查最近的消息记录"""
    print("\n🔍 检查最近的消息记录...")
    try:
        db = mysql_db.get_session()
        
        # 查询最近1小时的消息
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_messages = db.query(Message).filter(
            Message.create_time >= one_hour_ago
        ).order_by(desc(Message.create_time)).limit(10).all()
        
        print(f"📊 最近1小时的消息数量: {len(recent_messages)}")
        
        if recent_messages:
            print("📝 最近的消息:")
            for msg in recent_messages:
                print(f"  - ID: {msg.message_id}")
                print(f"    会话ID: {msg.conversation_id}")
                print(f"    发送者: {msg.sender_id}")
                print(f"    内容: {msg.content[:50]}...")
                print(f"    时间: {msg.create_time}")
                print(f"    是否AI消息: {msg.is_ai_message}")
                print()
        else:
            print("⚠️ 没有找到最近的消息记录")
        
        db.close()
        return len(recent_messages)
        
    except Exception as e:
        print(f"❌ 查询消息记录失败: {e}")
        return 0

def check_conversations():
    """检查会话记录"""
    print("\n🔍 检查会话记录...")
    try:
        db = mysql_db.get_session()
        
        # 查询最近的会话
        recent_conversations = db.query(Conversation).filter(
            Conversation.status == 1
        ).order_by(desc(Conversation.create_time)).limit(5).all()
        
        print(f"📊 活跃会话数量: {len(recent_conversations)}")
        
        if recent_conversations:
            print("💬 最近的会话:")
            for conv in recent_conversations:
                print(f"  - 会话ID: {conv.conversation_id}")
                print(f"    用户1: {conv.user1_id}")
                print(f"    用户2: {conv.user2_id}")
                print(f"    类型: {conv.conversation_type}")
                print(f"    创建时间: {conv.create_time}")
                print()
        else:
            print("⚠️ 没有找到活跃的会话记录")
        
        db.close()
        return len(recent_conversations)
        
    except Exception as e:
        print(f"❌ 查询会话记录失败: {e}")
        return 0

def check_ai_characters():
    """检查AI角色"""
    print("\n🔍 检查AI角色...")
    try:
        db = mysql_db.get_session()
        
        ai_characters = db.query(AICharacter).filter(
            AICharacter.status == 1
        ).limit(5).all()
        
        print(f"🤖 可用AI角色数量: {len(ai_characters)}")
        
        if ai_characters:
            print("🎭 AI角色列表:")
            for char in ai_characters:
                print(f"  - 角色ID: {char.character_id}")
                print(f"    昵称: {char.nickname}")
                print(f"    使用次数: {char.usage_count}")
                print()
        else:
            print("⚠️ 没有找到可用的AI角色")
        
        db.close()
        return len(ai_characters)
        
    except Exception as e:
        print(f"❌ 查询AI角色失败: {e}")
        return 0

def test_message_insertion():
    """测试消息插入"""
    print("\n🧪 测试消息插入...")
    try:
        db = mysql_db.get_session()
        
        # 创建一个测试消息
        test_message = Message(
            message_id="081145e6-7305-4dac-b538-98be5bf2a418",
            conversation_id="44b436ea-8423-458f-92a5-7780b596f02b",
            sender_id=19,
            receiver_id=0,
            content="测试消息内容",
            message_type="text",
            is_ai_message=False,
            ai_character_id=None
        )
        
        db.add(test_message)
        db.commit()
        
        print("✅ 测试消息插入成功")
        
        # 验证插入
        inserted_msg = db.query(Message).filter(
            Message.message_id == test_message.message_id
        ).first()
        
        if inserted_msg:
            print(f"✅ 验证插入成功: {inserted_msg.content}")
            
            # 清理测试数据
            db.delete(inserted_msg)
            db.commit()
            print("🧹 测试数据已清理")
        else:
            print("❌ 验证插入失败")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试消息插入失败: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def check_websocket_logs():
    """检查WebSocket相关日志"""
    print("\n🔍 检查WebSocket处理逻辑...")
    
    # 检查关键文件是否存在
    files_to_check = [
        "app/websocket/ai_handler.py",
        "app/websocket/ai_manager.py",
        "app/api/ai_websocket.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")

def main():
    """主函数"""
    print("🚀 WebSocket AI聊天消息保存问题排查")
    print("=" * 50)
    
    # 1. 检查数据库连接
    if not check_database_connection():
        print("\n❌ 数据库连接失败，请检查数据库配置")
        return
    
    # 2. 检查最近的消息
    message_count = check_recent_messages()
    
    # 3. 检查会话记录
    conversation_count = check_conversations()
    
    # 4. 检查AI角色
    ai_character_count = check_ai_characters()
    
    # 5. 测试消息插入
    insertion_success = test_message_insertion()
    
    # 6. 检查WebSocket文件
    check_websocket_logs()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 排查结果总结:")
    print(f"  - 数据库连接: {'✅ 正常' if check_database_connection() else '❌ 异常'}")
    print(f"  - 最近消息数量: {message_count}")
    print(f"  - 活跃会话数量: {conversation_count}")
    print(f"  - AI角色数量: {ai_character_count}")
    print(f"  - 消息插入测试: {'✅ 成功' if insertion_success else '❌ 失败'}")
    
    # 问题诊断
    print("\n🔍 问题诊断:")
    if message_count == 0:
        print("⚠️ 没有最近的消息记录，可能的原因:")
        print("  1. WebSocket连接未建立")
        print("  2. 消息处理逻辑有错误")
        print("  3. 数据库事务未提交")
        print("  4. 会话ID无效")
    elif not insertion_success:
        print("⚠️ 消息插入测试失败，可能的原因:")
        print("  1. 数据库权限问题")
        print("  2. 表结构问题")
        print("  3. 约束冲突")
    else:
        print("✅ 基础功能正常，问题可能在WebSocket处理逻辑中")
    
    print("\n💡 建议的排查步骤:")
    print("  1. 检查WebSocket连接是否正常建立")
    print("  2. 查看服务器日志中的错误信息")
    print("  3. 验证发送的消息格式是否正确")
    print("  4. 检查会话ID是否有效")
    print("  5. 确认AI角色是否存在")

if __name__ == "__main__":
    main()
