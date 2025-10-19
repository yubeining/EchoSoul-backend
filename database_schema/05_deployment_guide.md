# 《超电磁炮》角色数据库部署指南

## 一、系统要求

### 硬件要求
- **CPU**: 4核心以上
- **内存**: 8GB以上（推荐16GB）
- **存储**: 100GB以上SSD
- **网络**: 稳定的网络连接

### 软件要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.8+
- **Node.js**: 16+（可选，用于Web界面）

## 二、快速部署（Docker Compose）

### 2.1 创建部署目录

```bash
mkdir -p /opt/railgun-database
cd /opt/railgun-database
```

### 2.2 创建Docker Compose配置

```yaml
# docker-compose.yml
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
      - ./config/mysql.cnf:/etc/mysql/conf.d/custom.cnf
    command: --default-authentication-plugin=mysql_native_password
    restart: unless-stopped
    networks:
      - railgun-network

  neo4j:
    image: neo4j:4.4
    container_name: railgun-neo4j
    environment:
      NEO4J_AUTH: ${NEO4J_USER:-neo4j}/${NEO4J_PASSWORD:-railgun123}
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_dbms_security_procedures_unrestricted: apoc.*
      NEO4J_dbms_security_procedures_allowlist: apoc.*
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins
    restart: unless-stopped
    networks:
      - railgun-network

  elasticsearch:
    image: elasticsearch:7.15.0
    container_name: railgun-elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
      - "9300:9300"
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

  api-server:
    build: ./api-server
    container_name: railgun-api
    environment:
      MYSQL_HOST: mysql
      MYSQL_USER: railgun_user
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-railgun123}
      MYSQL_DATABASE: railgun_character_db
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: ${NEO4J_USER:-neo4j}
      NEO4J_PASSWORD: ${NEO4J_PASSWORD:-railgun123}
      ES_HOST: elasticsearch:9200
      REDIS_HOST: redis:6379
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - neo4j
      - elasticsearch
      - redis
    restart: unless-stopped
    networks:
      - railgun-network

  web-ui:
    build: ./web-ui
    container_name: railgun-web
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000
    depends_on:
      - api-server
    restart: unless-stopped
    networks:
      - railgun-network

volumes:
  mysql_data:
  neo4j_data:
  neo4j_logs:
  neo4j_import:
  neo4j_plugins:
  es_data:
  redis_data:

networks:
  railgun-network:
    driver: bridge
```

### 2.3 创建环境变量文件

```bash
# .env
MYSQL_ROOT_PASSWORD=railgun123
MYSQL_PASSWORD=railgun123
NEO4J_USER=neo4j
NEO4J_PASSWORD=railgun123
```

### 2.4 创建MySQL配置文件

```bash
mkdir -p config
cat > config/mysql.cnf << EOF
[mysqld]
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
max_connections=200
innodb_buffer_pool_size=1G
innodb_log_file_size=256M
slow_query_log=1
slow_query_log_file=/var/lib/mysql/slow.log
long_query_time=2
EOF
```

### 2.5 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 三、手动安装部署

### 3.1 安装MySQL 8.0

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server-8.0

# 配置MySQL
sudo mysql_secure_installation

# 创建数据库和用户
sudo mysql -u root -p
```

```sql
CREATE DATABASE railgun_character_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'railgun_user'@'localhost' IDENTIFIED BY 'railgun123';
GRANT ALL PRIVILEGES ON railgun_character_db.* TO 'railgun_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3.2 安装Neo4j

```bash
# 添加Neo4j仓库
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list

# 安装Neo4j
sudo apt update
sudo apt install neo4j

# 启动服务
sudo systemctl start neo4j
sudo systemctl enable neo4j

# 设置密码
sudo neo4j-admin set-initial-password railgun123
```

### 3.3 安装Elasticsearch

```bash
# 添加Elasticsearch仓库
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list

# 安装Elasticsearch
sudo apt update
sudo apt install elasticsearch

# 配置Elasticsearch
sudo nano /etc/elasticsearch/elasticsearch.yml
```

```yaml
# /etc/elasticsearch/elasticsearch.yml
cluster.name: railgun-cluster
node.name: railgun-node-1
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch
network.host: localhost
http.port: 9200
discovery.type: single-node
```

```bash
# 启动服务
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch
```

### 3.4 安装Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server

# 配置Redis
sudo nano /etc/redis/redis.conf
```

```bash
# 启动服务
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## 四、数据库初始化

### 4.1 导入MySQL数据

```bash
# 导入基础数据
mysql -u railgun_user -p railgun_character_db < database_schema/01_character_basic.sql
mysql -u railgun_user -p railgun_character_db < database_schema/02_dialogue_scene.sql
```

### 4.2 导入Neo4j数据

```bash
# 使用Neo4j Browser或cypher-shell
cypher-shell -u neo4j -p railgun123 -f database_schema/03_neo4j_relationships.cypher
```

### 4.3 创建Elasticsearch索引

```bash
# 创建角色索引
curl -X PUT "localhost:9200/characters" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "char_id": {"type": "keyword"},
      "name_cn": {"type": "text", "analyzer": "ik_max_word"},
      "identity": {"type": "text"},
      "personality": {"type": "text"},
      "speech_feature": {"type": "text"}
    }
  }
}'

# 创建对话索引
curl -X PUT "localhost:9200/dialogues" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "dialogue_id": {"type": "keyword"},
      "content": {"type": "text", "analyzer": "ik_max_word"},
      "speaker_id": {"type": "keyword"},
      "emotion": {"type": "keyword"},
      "scene_type": {"type": "keyword"}
    }
  }
}'
```

## 五、API服务器部署

### 5.1 创建API服务器

```bash
mkdir -p api-server
cd api-server
```

```python
# api-server/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from database_schema.query_examples import RailgunCharacterDatabase
import os

app = Flask(__name__)
CORS(app)

# 数据库配置
mysql_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'railgun_user'),
    'password': os.getenv('MYSQL_PASSWORD', 'railgun123'),
    'database': os.getenv('MYSQL_DATABASE', 'railgun_character_db'),
    'charset': 'utf8mb4'
}

neo4j_config = {
    'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    'username': os.getenv('NEO4J_USER', 'neo4j'),
    'password': os.getenv('NEO4J_PASSWORD', 'railgun123')
}

es_config = {
    'host': os.getenv('ES_HOST', 'localhost:9200')
}

# 初始化数据库连接
db = RailgunCharacterDatabase(mysql_config, neo4j_config, es_config)

@app.route('/api/characters/<char_id>', methods=['GET'])
def get_character(char_id):
    """获取角色信息"""
    try:
        character = db.get_character_basic_info(char_id)
        if character:
            return jsonify({'success': True, 'data': character})
        else:
            return jsonify({'success': False, 'message': '角色不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/characters/<char_id>/relationships', methods=['GET'])
def get_character_relationships(char_id):
    """获取角色关系"""
    try:
        relationships = db.get_character_relationships(char_id)
        return jsonify({'success': True, 'data': relationships})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/dialogue/context', methods=['POST'])
def get_dialogue_context():
    """获取对话上下文"""
    try:
        data = request.get_json()
        char_id_1 = data.get('char_id_1')
        char_id_2 = data.get('char_id_2')
        scene_type = data.get('scene_type')
        
        context = db.get_dialogue_context(char_id_1, char_id_2, scene_type)
        return jsonify({'success': True, 'data': context})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/dialogue/suggestions', methods=['POST'])
def get_dialogue_suggestions():
    """获取对话建议"""
    try:
        data = request.get_json()
        char_id_1 = data.get('char_id_1')
        char_id_2 = data.get('char_id_2')
        scene_type = data.get('scene_type')
        
        suggestions = db.generate_dialogue_suggestions(char_id_1, char_id_2, scene_type)
        return jsonify({'success': True, 'data': suggestions})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/search/dialogues', methods=['GET'])
def search_dialogues():
    """搜索对话"""
    try:
        search_text = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        results = db.search_dialogues_by_content(search_text, limit)
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/analysis/network', methods=['GET'])
def get_network_analysis():
    """获取关系网络分析"""
    try:
        analysis = db.get_relationship_network_analysis()
        return jsonify({'success': True, 'data': analysis})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
```

```dockerfile
# api-server/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```

```txt
# api-server/requirements.txt
Flask==2.3.2
Flask-CORS==4.0.0
mysql-connector-python==8.1.0
neo4j==5.8.0
elasticsearch==7.15.0
redis==4.6.0
python-dotenv==1.0.0
```

## 六、Web界面部署

### 6.1 创建React应用

```bash
npx create-react-app web-ui
cd web-ui
npm install axios react-router-dom @mui/material @emotion/react @emotion/styled
```

```jsx
// web-ui/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import CharacterList from './components/CharacterList';
import CharacterDetail from './components/CharacterDetail';
import DialogueGenerator from './components/DialogueGenerator';
import NetworkAnalysis from './components/NetworkAnalysis';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<CharacterList />} />
          <Route path="/character/:id" element={<CharacterDetail />} />
          <Route path="/dialogue" element={<DialogueGenerator />} />
          <Route path="/analysis" element={<NetworkAnalysis />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
```

```dockerfile
# web-ui/Dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

## 七、监控和维护

### 7.1 健康检查

```bash
# 创建健康检查脚本
cat > health_check.sh << 'EOF'
#!/bin/bash

echo "=== 数据库健康检查 ==="

# MySQL检查
echo "检查MySQL..."
mysql -u railgun_user -prailgun123 -e "SELECT 1" railgun_character_db > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ MySQL正常"
else
    echo "✗ MySQL异常"
fi

# Neo4j检查
echo "检查Neo4j..."
curl -s http://localhost:7474 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Neo4j正常"
else
    echo "✗ Neo4j异常"
fi

# Elasticsearch检查
echo "检查Elasticsearch..."
curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Elasticsearch正常"
else
    echo "✗ Elasticsearch异常"
fi

# Redis检查
echo "检查Redis..."
redis-cli ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Redis正常"
else
    echo "✗ Redis异常"
fi

echo "=== 检查完成 ==="
EOF

chmod +x health_check.sh
```

### 7.2 备份脚本

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/railgun-backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "开始备份到: $BACKUP_DIR"

# 备份MySQL
echo "备份MySQL..."
mysqldump -u railgun_user -prailgun123 railgun_character_db > $BACKUP_DIR/mysql_backup.sql

# 备份Neo4j
echo "备份Neo4j..."
docker exec railgun-neo4j neo4j-admin dump --database=neo4j --to=/tmp/neo4j_backup.dump
docker cp railgun-neo4j:/tmp/neo4j_backup.dump $BACKUP_DIR/

# 备份Elasticsearch
echo "备份Elasticsearch..."
curl -X POST "localhost:9200/_snapshot/backup_repo/snapshot_$(date +%Y%m%d_%H%M%S)" -H 'Content-Type: application/json' -d'
{
  "indices": "characters,dialogues",
  "ignore_unavailable": true,
  "include_global_state": false
}'

echo "备份完成: $BACKUP_DIR"
EOF

chmod +x backup.sh
```

### 7.3 定时任务

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点执行健康检查
0 2 * * * /opt/railgun-database/health_check.sh >> /var/log/railgun-health.log

# 每周日凌晨3点执行备份
0 3 * * 0 /opt/railgun-database/backup.sh
```

## 八、性能优化

### 8.1 MySQL优化

```sql
-- 创建索引
CREATE INDEX idx_character_name ON character_basic(name_cn);
CREATE INDEX idx_dialogue_scene ON dialogue_scene(scene_id);
CREATE INDEX idx_dialogue_participants ON dialogue_scene((CAST(participants AS CHAR(100) ARRAY)));

-- 优化查询
ANALYZE TABLE character_basic;
ANALYZE TABLE dialogue_scene;
ANALYZE TABLE dialogue_turns;
```

### 8.2 Neo4j优化

```cypher
// 创建复合索引
CREATE INDEX character_identity_index FOR (c:Character) ON (c.identity);
CREATE INDEX relationship_intensity_index FOR ()-[r]-() ON (r.intensity);

// 优化查询计划
EXPLAIN MATCH (c:Character)-[r]-(other:Character) RETURN c, r, other;
```

### 8.3 Elasticsearch优化

```bash
# 设置分片和副本
curl -X PUT "localhost:9200/characters/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  }
}'
```

## 九、故障排除

### 9.1 常见问题

1. **MySQL连接失败**
   ```bash
   # 检查服务状态
   sudo systemctl status mysql
   
   # 检查端口
   netstat -tlnp | grep 3306
   
   # 检查日志
   sudo tail -f /var/log/mysql/error.log
   ```

2. **Neo4j连接失败**
   ```bash
   # 检查服务状态
   sudo systemctl status neo4j
   
   # 检查端口
   netstat -tlnp | grep 7474
   
   # 检查日志
   sudo tail -f /var/log/neo4j/neo4j.log
   ```

3. **Elasticsearch启动失败**
   ```bash
   # 检查Java版本
   java -version
   
   # 检查内存设置
   sudo nano /etc/elasticsearch/jvm.options
   
   # 检查日志
   sudo tail -f /var/log/elasticsearch/elasticsearch.log
   ```

### 9.2 日志管理

```bash
# 配置日志轮转
sudo nano /etc/logrotate.d/railgun-database

# 内容
/var/log/railgun-*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

## 十、安全配置

### 10.1 防火墙设置

```bash
# 只允许必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 3000  # Web UI
sudo ufw allow 8000  # API
sudo ufw enable
```

### 10.2 数据库安全

```sql
-- 创建只读用户
CREATE USER 'railgun_readonly'@'localhost' IDENTIFIED BY 'readonly123';
GRANT SELECT ON railgun_character_db.* TO 'railgun_readonly'@'localhost';

-- 限制连接数
SET GLOBAL max_connections = 100;
```

这个部署指南提供了完整的《超电磁炮》角色数据库部署方案，包括Docker快速部署和手动安装两种方式，以及监控、备份、优化等运维相关内容。
