#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《超电磁炮》角色数据库查询示例
包含MySQL、Neo4j、Elasticsearch的查询接口
"""

import json
import mysql.connector
from neo4j import GraphDatabase
from elasticsearch import Elasticsearch
from typing import List, Dict, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RailgunCharacterDatabase:
    """《超电磁炮》角色数据库查询类"""
    
    def __init__(self, mysql_config: Dict, neo4j_config: Dict, es_config: Dict):
        """
        初始化数据库连接
        
        Args:
            mysql_config: MySQL连接配置
            neo4j_config: Neo4j连接配置  
            es_config: Elasticsearch连接配置
        """
        self.mysql_config = mysql_config
        self.neo4j_config = neo4j_config
        self.es_config = es_config
        
        # 初始化连接
        self.mysql_conn = None
        self.neo4j_driver = None
        self.es_client = None
        
    def connect_mysql(self):
        """连接MySQL数据库"""
        try:
            self.mysql_conn = mysql.connector.connect(**self.mysql_config)
            logger.info("MySQL连接成功")
        except Exception as e:
            logger.error(f"MySQL连接失败: {e}")
            
    def connect_neo4j(self):
        """连接Neo4j数据库"""
        try:
            self.neo4j_driver = GraphDatabase.driver(
                self.neo4j_config['uri'],
                auth=(self.neo4j_config['username'], self.neo4j_config['password'])
            )
            logger.info("Neo4j连接成功")
        except Exception as e:
            logger.error(f"Neo4j连接失败: {e}")
            
    def connect_elasticsearch(self):
        """连接Elasticsearch"""
        try:
            self.es_client = Elasticsearch([self.es_config['host']])
            logger.info("Elasticsearch连接成功")
        except Exception as e:
            logger.error(f"Elasticsearch连接失败: {e}")
    
    def get_character_basic_info(self, char_id: str) -> Optional[Dict]:
        """
        获取角色基础信息
        
        Args:
            char_id: 角色ID
            
        Returns:
            角色基础信息字典
        """
        if not self.mysql_conn:
            self.connect_mysql()
            
        cursor = self.mysql_conn.cursor(dictionary=True)
        query = """
        SELECT * FROM character_basic 
        WHERE char_id = %s
        """
        cursor.execute(query, (char_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            # 解析JSON字段
            result['identity'] = json.loads(result['identity'])
            result['personality'] = json.loads(result['personality'])
            result['speech_feature'] = json.loads(result['speech_feature'])
            result['appearance'] = json.loads(result['appearance'])
            result['abilities'] = json.loads(result['abilities'])
            
        return result
    
    def get_character_relationships(self, char_id: str) -> List[Dict]:
        """
        获取角色的所有关系
        
        Args:
            char_id: 角色ID
            
        Returns:
            关系列表
        """
        if not self.neo4j_driver:
            self.connect_neo4j()
            
        with self.neo4j_driver.session() as session:
            query = """
            MATCH (c:Character {char_id: $char_id})-[r]-(other:Character)
            RETURN other.char_id, other.name_cn, type(r) as relationship_type, 
                   r.intensity, r.relationship_desc, r.speech_rule, r.taboo
            ORDER BY r.intensity DESC
            """
            result = session.run(query, char_id=char_id)
            return [record.data() for record in result]
    
    def get_relationship_rules(self, char_id_1: str, char_id_2: str) -> List[Dict]:
        """
        获取两个角色之间的关系规则
        
        Args:
            char_id_1: 第一个角色ID
            char_id_2: 第二个角色ID
            
        Returns:
            关系规则列表
        """
        if not self.neo4j_driver:
            self.connect_neo4j()
            
        with self.neo4j_driver.session() as session:
            query = """
            MATCH (c1:Character {char_id: $char_id_1})-[r]-(c2:Character {char_id: $char_id_2})
            RETURN type(r) as relationship_type, r.speech_rule, r.taboo, 
                   r.typical_scene, r.intensity, r.relationship_desc, r.interaction_pattern
            """
            result = session.run(query, char_id_1=char_id_1, char_id_2=char_id_2)
            return [record.data() for record in result]
    
    def get_dialogue_context(self, char_id_1: str, char_id_2: str, scene_type: str = None) -> Dict:
        """
        获取对话生成所需的上下文信息
        
        Args:
            char_id_1: 第一个角色ID
            char_id_2: 第二个角色ID
            scene_type: 场景类型（可选）
            
        Returns:
            对话上下文信息
        """
        context = {}
        
        # 1. 获取角色基础信息
        context['characters'] = {
            'char_1': self.get_character_basic_info(char_id_1),
            'char_2': self.get_character_basic_info(char_id_2)
        }
        
        # 2. 获取关系规则
        context['relationship_rules'] = self.get_relationship_rules(char_id_1, char_id_2)
        
        # 3. 获取相似场景的对话示例
        context['dialogue_examples'] = self.get_similar_dialogues(char_id_1, char_id_2, scene_type)
        
        return context
    
    def get_similar_dialogues(self, char_id_1: str, char_id_2: str, scene_type: str = None) -> List[Dict]:
        """
        获取相似场景的对话示例
        
        Args:
            char_id_1: 第一个角色ID
            char_id_2: 第二个角色ID
            scene_type: 场景类型（可选）
            
        Returns:
            对话示例列表
        """
        if not self.mysql_conn:
            self.connect_mysql()
            
        cursor = self.mysql_conn.cursor(dictionary=True)
        
        # 构建查询条件
        participants = json.dumps([char_id_1, char_id_2])
        query = """
        SELECT ds.*, si.scene_name, si.scene_type, si.description as scene_description
        FROM dialogue_scene ds
        JOIN scene_info si ON ds.scene_id = si.scene_id
        WHERE JSON_CONTAINS(ds.participants, %s)
        """
        params = [participants]
        
        if scene_type:
            query += " AND si.scene_type = %s"
            params.append(scene_type)
            
        query += " ORDER BY ds.intensity_level DESC, ds.created_at DESC LIMIT 5"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        
        # 解析JSON字段
        for result in results:
            result['participants'] = json.loads(result['participants'])
            result['dialogue_turn'] = json.loads(result['dialogue_turn'])
            result['emotion_tag'] = json.loads(result['emotion_tag'])
            result['episode_info'] = json.loads(result['episode_info'])
            
        return results
    
    def search_dialogues_by_content(self, search_text: str, limit: int = 10) -> List[Dict]:
        """
        根据内容搜索对话
        
        Args:
            search_text: 搜索文本
            limit: 结果数量限制
            
        Returns:
            匹配的对话列表
        """
        if not self.mysql_conn:
            self.connect_mysql()
            
        cursor = self.mysql_conn.cursor(dictionary=True)
        query = """
        SELECT dt.*, ds.dialogue_id, ds.scene_id, cb.name_cn as speaker_name
        FROM dialogue_turns dt
        JOIN dialogue_scene ds ON dt.dialogue_id = ds.dialogue_id
        JOIN character_basic cb ON dt.speaker_id = cb.char_id
        WHERE dt.content LIKE %s
        ORDER BY dt.created_at DESC
        LIMIT %s
        """
        cursor.execute(query, (f"%{search_text}%", limit))
        results = cursor.fetchall()
        cursor.close()
        
        return results
    
    def get_character_speech_analysis(self, char_id: str) -> Dict:
        """
        获取角色的语言风格分析
        
        Args:
            char_id: 角色ID
            
        Returns:
            语言风格分析结果
        """
        if not self.mysql_conn:
            self.connect_mysql()
            
        cursor = self.mysql_conn.cursor(dictionary=True)
        query = """
        SELECT 
            emotion,
            speech_style,
            COUNT(*) as frequency,
            AVG(LENGTH(content)) as avg_length,
            GROUP_CONCAT(DISTINCT content SEPARATOR ' | ') as examples
        FROM dialogue_turns
        WHERE speaker_id = %s
        GROUP BY emotion, speech_style
        ORDER BY frequency DESC
        """
        cursor.execute(query, (char_id,))
        results = cursor.fetchall()
        cursor.close()
        
        return {
            'char_id': char_id,
            'speech_analysis': results,
            'total_dialogues': sum(r['frequency'] for r in results)
        }
    
    def get_relationship_network_analysis(self) -> Dict:
        """
        获取关系网络分析
        
        Returns:
            关系网络分析结果
        """
        if not self.neo4j_driver:
            self.connect_neo4j()
            
        with self.neo4j_driver.session() as session:
            # 查询所有关系
            query = """
            MATCH (c1:Character)-[r]-(c2:Character)
            RETURN c1.name_cn as char1_name, c2.name_cn as char2_name,
                   type(r) as relationship_type, r.intensity
            ORDER BY r.intensity DESC
            """
            result = session.run(query)
            relationships = [record.data() for record in result]
            
            # 查询关系类型统计
            query2 = """
            MATCH ()-[r]-()
            RETURN type(r) as relationship_type, count(r) as count, avg(r.intensity) as avg_intensity
            ORDER BY count DESC
            """
            result2 = session.run(query2)
            relationship_stats = [record.data() for record in result2]
            
            # 查询连接度最高的角色
            query3 = """
            MATCH (c:Character)-[r]-(other:Character)
            WITH c, count(r) as connection_count
            RETURN c.name_cn, c.char_id, connection_count
            ORDER BY connection_count DESC
            """
            result3 = session.run(query3)
            top_connected = [record.data() for record in result3]
            
            return {
                'relationships': relationships,
                'relationship_stats': relationship_stats,
                'top_connected_characters': top_connected
            }
    
    def generate_dialogue_suggestions(self, char_id_1: str, char_id_2: str, scene_type: str = None) -> Dict:
        """
        生成对话建议
        
        Args:
            char_id_1: 第一个角色ID
            char_id_2: 第二个角色ID
            scene_type: 场景类型（可选）
            
        Returns:
            对话建议
        """
        # 获取对话上下文
        context = self.get_dialogue_context(char_id_1, char_id_2, scene_type)
        
        suggestions = {
            'characters': context['characters'],
            'relationship_rules': context['relationship_rules'],
            'dialogue_examples': context['dialogue_examples'],
            'suggestions': []
        }
        
        # 基于关系规则生成建议
        for rule in context['relationship_rules']:
            if rule.get('speech_rule'):
                suggestions['suggestions'].append({
                    'type': 'speech_rule',
                    'content': f"遵循语言规则: {rule['speech_rule']}",
                    'relationship_type': rule['relationship_type'],
                    'intensity': rule['intensity']
                })
            
            if rule.get('taboo'):
                suggestions['suggestions'].append({
                    'type': 'taboo',
                    'content': f"避免禁忌: {rule['taboo']}",
                    'relationship_type': rule['relationship_type']
                })
        
        return suggestions
    
    def close_connections(self):
        """关闭所有数据库连接"""
        if self.mysql_conn:
            self.mysql_conn.close()
        if self.neo4j_driver:
            self.neo4j_driver.close()
        if self.es_client:
            self.es_client.close()


# 使用示例
def main():
    """主函数 - 使用示例"""
    
    # 数据库配置
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'railgun_character_db',
        'charset': 'utf8mb4'
    }
    
    neo4j_config = {
        'uri': 'bolt://localhost:7687',
        'username': 'neo4j',
        'password': 'password'
    }
    
    es_config = {
        'host': 'localhost:9200'
    }
    
    # 创建数据库实例
    db = RailgunCharacterDatabase(mysql_config, neo4j_config, es_config)
    
    try:
        # 示例1: 获取美琴的基础信息
        print("=== 美琴的基础信息 ===")
        misaka_info = db.get_character_basic_info('misaka_mikoto')
        if misaka_info:
            print(f"姓名: {misaka_info['name_cn']}")
            print(f"身份: {misaka_info['identity']}")
            print(f"性格: {misaka_info['personality']}")
            print(f"语言特征: {misaka_info['speech_feature']}")
        
        # 示例2: 获取黑子和美琴的关系
        print("\n=== 黑子和美琴的关系 ===")
        relationships = db.get_relationship_rules('shirai_kuroko', 'misaka_mikoto')
        for rel in relationships:
            print(f"关系类型: {rel['relationship_type']}")
            print(f"关系强度: {rel['intensity']}")
            print(f"语言规则: {rel['speech_rule']}")
            print(f"禁忌: {rel['taboo']}")
            print("---")
        
        # 示例3: 获取对话上下文
        print("\n=== 美琴和黑子的对话上下文 ===")
        context = db.get_dialogue_context('misaka_mikoto', 'shirai_kuroko', 'dormitory')
        print(f"找到 {len(context['dialogue_examples'])} 个相关对话示例")
        
        # 示例4: 生成对话建议
        print("\n=== 对话建议 ===")
        suggestions = db.generate_dialogue_suggestions('misaka_mikoto', 'shirai_kuroko', 'dormitory')
        for suggestion in suggestions['suggestions']:
            print(f"建议类型: {suggestion['type']}")
            print(f"内容: {suggestion['content']}")
            print("---")
        
        # 示例5: 关系网络分析
        print("\n=== 关系网络分析 ===")
        network_analysis = db.get_relationship_network_analysis()
        print("关系类型统计:")
        for stat in network_analysis['relationship_stats']:
            print(f"  {stat['relationship_type']}: {stat['count']}个关系, 平均强度: {stat['avg_intensity']:.1f}")
        
        print("\n连接度最高的角色:")
        for char in network_analysis['top_connected_characters'][:3]:
            print(f"  {char['name_cn']}: {char['connection_count']}个连接")
    
    finally:
        db.close_connections()


if __name__ == "__main__":
    main()
