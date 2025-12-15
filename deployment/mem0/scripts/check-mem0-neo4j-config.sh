#!/bin/bash
# 检查 Mem0 API 的 Neo4j 配置

set -e

echo "=== 检查 Mem0 API 的 Neo4j 配置 ==="
echo ""

# 1. 检查 mem0-api 容器中的环境变量
echo "1. 检查 mem0-api 容器中的 Neo4j 环境变量..."
if docker ps | grep -q mem0-api; then
    echo "Neo4j 配置："
    docker exec mem0-api env | grep -i neo4j || echo "未找到 NEO4j 环境变量"
    echo ""
    
    # 2. 检查 mem0-api 是否能访问 Neo4j 容器
    echo "2. 检查 mem0-api 是否能访问 Neo4j 容器..."
    if docker exec mem0-api ping -c 1 neo4j > /dev/null 2>&1; then
        echo "✅ mem0-api 可以访问 neo4j 容器"
    else
        echo "❌ mem0-api 无法访问 neo4j 容器（网络问题）"
    fi
    echo ""
    
    # 3. 检查 mem0-api 是否能连接到 Neo4j
    echo "3. 检查 mem0-api 是否能连接到 Neo4j..."
    if docker exec mem0-api python3 -c "
import os
print('NEO4J_URI:', os.environ.get('NEO4J_URI', 'NOT SET'))
print('NEO4J_USERNAME:', os.environ.get('NEO4J_USERNAME', 'NOT SET'))
print('NEO4J_PASSWORD:', os.environ.get('NEO4J_PASSWORD', 'NOT SET'))
" 2>/dev/null; then
        echo "✅ 环境变量读取成功"
    else
        echo "❌ 无法读取环境变量"
    fi
    echo ""
    
    # 4. 检查 mem0-api 日志中的 Neo4j 相关错误
    echo "4. 检查 mem0-api 日志中的 Neo4j 错误..."
    NEO4J_ERRORS=$(docker logs mem0-api --tail 100 2>&1 | grep -i "neo4j\|auth\|unauthorized" | tail -5 || echo "")
    if [ -n "$NEO4J_ERRORS" ]; then
        echo "发现 Neo4j 相关错误："
        echo "$NEO4J_ERRORS"
    else
        echo "✅ 未发现 Neo4j 相关错误"
    fi
    echo ""
    
    # 5. 检查网络连接
    echo "5. 检查网络配置..."
    echo "mem0-api 网络："
    docker inspect mem0-api --format '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' 2>/dev/null || echo "无法获取"
    echo "neo4j 网络："
    docker inspect mem0_neo4j --format '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' 2>/dev/null || echo "无法获取"
    echo ""
    
else
    echo "❌ mem0-api 容器未运行"
    echo "请先启动容器："
    echo "  docker-compose -f docker-compose.1panel.yml up -d mem0-api"
fi

echo "=== 检查完成 ==="
echo ""
echo "如果环境变量不正确，请："
echo "  1. 检查 docker-compose.1panel.yml 中的配置"
echo "  2. 重启 mem0-api 容器："
echo "     docker-compose -f docker-compose.1panel.yml restart mem0-api"

