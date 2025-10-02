#!/bin/bash
# 《超电磁炮》角色数据库快速启动脚本

set -e

echo "=== 《超电磁炮》角色数据库快速启动 ==="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建环境变量文件
if [ ! -f .env ]; then
    echo "创建环境变量文件..."
    cat > .env << EOF
MYSQL_ROOT_PASSWORD=railgun123
MYSQL_PASSWORD=railgun123
NEO4J_USER=neo4j
NEO4J_PASSWORD=railgun123
EOF
    echo "✓ 环境变量文件已创建"
fi

# 创建Docker Compose文件
if [ ! -f docker-compose.yml ]; then
    echo "创建Docker Compose配置文件..."
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: railgun-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-railgun123}
      MYSQL_DATABASE: railgun_character_db
      MYSQL_USER: railgun_user
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-railgun123}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database_schema:/docker-entrypoint-initdb.d
    command: --default-authentication-plugin=mysql_native_password
    restart: unless-stopped
    networks:
      - railgun-network

  neo4j:
    image: neo4j:4.4
    container_name: railgun-neo4j
    environment:
      NEO4J_AUTH: ${NEO4J_USER:-neo4j}/${NEO4J_PASSWORD:-railgun123}
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    restart: unless-stopped
    networks:
      - railgun-network

  elasticsearch:
    image: elasticsearch:7.15.0
    container_name: railgun-elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    restart: unless-stopped
    networks:
      - railgun-network

  redis:
    image: redis:6.2-alpine
    container_name: railgun-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - railgun-network

volumes:
  mysql_data:
  neo4j_data:
  neo4j_logs:
  es_data:
  redis_data:

networks:
  railgun-network:
    driver: bridge
EOF
    echo "✓ Docker Compose配置文件已创建"
fi

# 启动服务
echo "启动数据库服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 等待MySQL启动完成
echo "等待MySQL启动完成..."
until docker exec railgun-mysql mysqladmin ping -h localhost --silent; do
    echo "等待MySQL启动..."
    sleep 5
done

# 导入Neo4j数据
echo "导入Neo4j数据..."
sleep 10  # 等待Neo4j完全启动
docker exec -i railgun-neo4j cypher-shell -u neo4j -p railgun123 < 03_neo4j_relationships.cypher

# 创建Elasticsearch索引
echo "创建Elasticsearch索引..."
sleep 10  # 等待Elasticsearch启动

# 创建角色索引
curl -X PUT "localhost:9200/characters" -H 'Content-Type: application/json' -d'{
  "mappings": {
    "properties": {
      "char_id": {"type": "keyword"},
      "name_cn": {"type": "text"},
      "identity": {"type": "text"},
      "personality": {"type": "text"},
      "speech_feature": {"type": "text"}
    }
  }
}' 2>/dev/null || echo "角色索引可能已存在"

# 创建对话索引
curl -X PUT "localhost:9200/dialogues" -H 'Content-Type: application/json' -d'{
  "mappings": {
    "properties": {
      "dialogue_id": {"type": "keyword"},
      "content": {"type": "text"},
      "speaker_id": {"type": "keyword"},
      "emotion": {"type": "keyword"},
      "scene_type": {"type": "keyword"}
    }
  }
}' 2>/dev/null || echo "对话索引可能已存在"

# 显示访问信息
echo ""
echo "=== 服务启动完成 ==="
echo "MySQL: localhost:3306 (用户: railgun_user, 密码: railgun123)"
echo "Neo4j Browser: http://localhost:7474 (用户: neo4j, 密码: railgun123)"
echo "Elasticsearch: http://localhost:9200"
echo "Redis: localhost:6379"
echo ""
echo "数据库: railgun_character_db"
echo ""

# 运行测试查询
echo "运行测试查询..."
python3 -c "
import sys
sys.path.append('.')
from database_schema.query_examples import RailgunCharacterDatabase

# 数据库配置
mysql_config = {
    'host': 'localhost',
    'user': 'railgun_user',
    'password': 'railgun123',
    'database': 'railgun_character_db',
    'charset': 'utf8mb4'
}

neo4j_config = {
    'uri': 'bolt://localhost:7687',
    'username': 'neo4j',
    'password': 'railgun123'
}

es_config = {
    'host': 'localhost:9200'
}

try:
    db = RailgunCharacterDatabase(mysql_config, neo4j_config, es_config)
    
    # 测试查询
    print('测试查询美琴的信息...')
    misaka = db.get_character_basic_info('misaka_mikoto')
    if misaka:
        print(f'✓ 找到角色: {misaka[\"name_cn\"]}')
    else:
        print('✗ 未找到角色信息')
    
    print('测试查询关系...')
    relationships = db.get_character_relationships('misaka_mikoto')
    print(f'✓ 找到 {len(relationships)} 个关系')
    
    print('✓ 数据库连接测试成功!')
    
except Exception as e:
    print(f'✗ 测试失败: {e}')
" 2>/dev/null || echo "Python测试跳过（需要安装依赖包）"

echo ""
echo "=== 快速启动完成 ==="
echo "要停止服务，请运行: docker-compose down"
echo "要查看日志，请运行: docker-compose logs -f"
echo "要重新启动，请运行: docker-compose restart"
echo ""
echo "下一步："
echo "1. 安装Python依赖: pip install -r requirements.txt"
echo "2. 运行查询示例: python 04_query_examples.py"
echo "3. 查看详细文档: cat README.md"
