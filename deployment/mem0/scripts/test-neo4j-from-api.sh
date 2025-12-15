#!/bin/bash
# 从 mem0-api 容器测试 Neo4j 连接

set -e

echo "=== 从 mem0-api 容器测试 Neo4j 连接 ==="
echo ""

# 1. 检查 mem0-api 容器是否运行
if ! docker ps | grep -q mem0-api; then
    echo "❌ mem0-api 容器未运行"
    exit 1
fi

# 2. 检查环境变量
echo "1. 检查 mem0-api 容器中的 Neo4j 环境变量..."
docker exec mem0-api env | grep -i neo4j
echo ""

# 3. 测试网络连接
echo "2. 测试网络连接..."
if docker exec mem0-api ping -c 1 neo4j > /dev/null 2>&1; then
    echo "✅ mem0-api 可以访问 neo4j 容器"
else
    echo "❌ mem0-api 无法访问 neo4j 容器"
    echo "   检查网络配置..."
    docker network inspect 1panel-network 2>/dev/null | grep -A 5 "mem0\|neo4j" || echo "网络检查失败"
fi
echo ""

# 4. 尝试从 mem0-api 容器连接 Neo4j
echo "3. 尝试从 mem0-api 容器连接 Neo4j..."
NEO4J_URI=$(docker exec mem0-api env | grep NEO4J_URI | cut -d= -f2 || echo "bolt://neo4j:7687")
NEO4J_USERNAME=$(docker exec mem0-api env | grep NEO4J_USERNAME | cut -d= -f2 || echo "neo4j")
NEO4J_PASSWORD=$(docker exec mem0-api env | grep NEO4J_PASSWORD | cut -d= -f2 || echo "mem0graph")

echo "使用配置："
echo "  URI: $NEO4J_URI"
echo "  Username: $NEO4J_USERNAME"
echo "  Password: $NEO4J_PASSWORD"
echo ""

# 尝试使用 Python 连接
if docker exec mem0-api python3 -c "
import os
from neo4j import GraphDatabase

uri = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
username = os.environ.get('NEO4J_USERNAME', 'neo4j')
password = os.environ.get('NEO4J_PASSWORD', 'mem0graph')

try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        result = session.run('RETURN 1')
        print('✅ Neo4j 连接成功')
        print('   结果:', result.single()[0])
    driver.close()
except Exception as e:
    print('❌ Neo4j 连接失败:', str(e))
    exit(1)
" 2>&1; then
    echo ""
    echo "✅ 从 mem0-api 容器可以成功连接 Neo4j"
else
    echo ""
    echo "❌ 从 mem0-api 容器无法连接 Neo4j"
    echo ""
    echo "可能的原因："
    echo "  1. 环境变量未正确传递"
    echo "  2. Neo4j 容器未准备好"
    echo "  3. 网络配置问题"
    echo ""
    echo "建议："
    echo "  1. 检查 docker-compose.1panel.yml 中的环境变量"
    echo "  2. 重启 mem0-api 容器"
    echo "  3. 检查 Neo4j 容器日志"
fi

echo ""
echo "=== 测试完成 ==="

