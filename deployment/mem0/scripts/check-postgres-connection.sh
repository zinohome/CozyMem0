#!/bin/bash
# 检查 PostgreSQL 连接配置

set -e

echo "=== PostgreSQL 连接配置检查 ==="
echo ""

# 1. 检查 PostgreSQL 容器状态
echo "1. 检查 PostgreSQL 容器状态..."
if docker ps | grep -q mem0_postgres; then
    echo "✅ PostgreSQL 容器正在运行"
    POSTGRES_RUNNING=true
else
    echo "❌ PostgreSQL 容器未运行"
    POSTGRES_RUNNING=false
fi
echo ""

# 2. 检查 PostgreSQL 容器中的密码配置
if [ "$POSTGRES_RUNNING" = true ]; then
    echo "2. 检查 PostgreSQL 容器中的密码配置..."
    POSTGRES_USER=$(docker exec mem0_postgres env | grep POSTGRES_USER | cut -d= -f2 || echo "mem0")
    POSTGRES_PASSWORD=$(docker exec mem0_postgres env | grep POSTGRES_PASSWORD | cut -d= -f2 || echo "")
    POSTGRES_DB=$(docker exec mem0_postgres env | grep POSTGRES_DB | cut -d= -f2 || echo "mem0")
    
    echo "PostgreSQL 容器配置："
    echo "  User: $POSTGRES_USER"
    echo "  Password: ${POSTGRES_PASSWORD:0:3}*** (隐藏)"
    echo "  Database: $POSTGRES_DB"
    echo ""
fi

# 3. 检查 mem0-api 容器中的配置
echo "3. 检查 mem0-api 容器中的 PostgreSQL 配置..."
if docker ps | grep -q mem0-api; then
    API_POSTGRES_USER=$(docker exec mem0-api env | grep POSTGRES_USER | cut -d= -f2 || echo "")
    API_POSTGRES_PASSWORD=$(docker exec mem0-api env | grep POSTGRES_PASSWORD | cut -d= -f2 || echo "")
    API_POSTGRES_HOST=$(docker exec mem0-api env | grep POSTGRES_HOST | cut -d= -f2 || echo "")
    API_POSTGRES_DB=$(docker exec mem0-api env | grep POSTGRES_DB | cut -d= -f2 || echo "")
    
    echo "mem0-api 容器配置："
    echo "  Host: $API_POSTGRES_HOST"
    echo "  User: $API_POSTGRES_USER"
    echo "  Password: ${API_POSTGRES_PASSWORD:0:3}*** (隐藏)"
    echo "  Database: $API_POSTGRES_DB"
    echo ""
    
    # 检查配置是否匹配
    if [ "$POSTGRES_RUNNING" = true ]; then
        if [ "$POSTGRES_USER" = "$API_POSTGRES_USER" ] && [ "$POSTGRES_PASSWORD" = "$API_POSTGRES_PASSWORD" ] && [ "$POSTGRES_DB" = "$API_POSTGRES_DB" ]; then
            echo "✅ 配置匹配"
        else
            echo "❌ 配置不匹配！"
            echo "   容器配置 vs API 配置："
            echo "   User: $POSTGRES_USER vs $API_POSTGRES_USER"
            echo "   Password: 匹配" || echo "   Password: 不匹配"
            echo "   Database: $POSTGRES_DB vs $API_POSTGRES_DB"
        fi
    fi
else
    echo "❌ mem0-api 容器未运行"
fi
echo ""

# 4. 测试 PostgreSQL 连接
if [ "$POSTGRES_RUNNING" = true ]; then
    echo "4. 测试 PostgreSQL 连接..."
    
    # 使用容器配置测试
    if docker exec mem0_postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ PostgreSQL 内部连接成功"
    else
        echo "❌ PostgreSQL 内部连接失败"
    fi
    
    # 使用 API 配置测试（如果 API 容器运行）
    if docker ps | grep -q mem0-api; then
        if docker exec mem0-api python3 -c "
import os
import psycopg2

try:
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'postgres'),
        port=int(os.environ.get('POSTGRES_PORT', 5432)),
        dbname=os.environ.get('POSTGRES_DB', 'mem0'),
        user=os.environ.get('POSTGRES_USER', 'mem0'),
        password=os.environ.get('POSTGRES_PASSWORD', 'mem0password')
    )
    conn.close()
    print('✅ 从 mem0-api 连接 PostgreSQL 成功')
except Exception as e:
    print('❌ 从 mem0-api 连接 PostgreSQL 失败:', str(e))
    exit(1)
" 2>&1; then
            echo ""
        else
            echo ""
        fi
    fi
fi
echo ""

# 5. 检查 docker-compose 配置
echo "5. 检查 docker-compose.1panel.yml 配置..."
if [ -f "docker-compose.1panel.yml" ]; then
    POSTGRES_USER_YAML=$(grep -A 5 "postgres:" docker-compose.1panel.yml | grep "POSTGRES_USER" | cut -d: -f2 | tr -d ' "')
    POSTGRES_PASSWORD_YAML=$(grep -A 5 "postgres:" docker-compose.1panel.yml | grep "POSTGRES_PASSWORD" | cut -d: -f2 | tr -d ' "')
    POSTGRES_DB_YAML=$(grep -A 5 "postgres:" docker-compose.1panel.yml | grep "POSTGRES_DB" | cut -d: -f2 | tr -d ' "')
    
    echo "docker-compose.1panel.yml 配置："
    echo "  User: $POSTGRES_USER_YAML"
    echo "  Password: ${POSTGRES_PASSWORD_YAML:0:3}*** (隐藏)"
    echo "  Database: $POSTGRES_DB_YAML"
    echo ""
    
    # 检查是否匹配
    if [ "$POSTGRES_RUNNING" = true ]; then
        if [ "$POSTGRES_USER" = "$POSTGRES_USER_YAML" ] && [ "$POSTGRES_PASSWORD" = "$POSTGRES_PASSWORD_YAML" ] && [ "$POSTGRES_DB" = "$POSTGRES_DB_YAML" ]; then
            echo "✅ docker-compose 配置与容器配置匹配"
        else
            echo "❌ docker-compose 配置与容器配置不匹配！"
            echo "   这可能是问题所在：容器启动时使用了不同的配置"
        fi
    fi
fi
echo ""

# 6. 检查启动顺序
echo "6. 检查启动顺序配置..."
if [ -f "docker-compose.1panel.yml" ]; then
    if grep -q "condition: service_started" docker-compose.1panel.yml; then
        echo "✅ 已配置启动顺序（depends_on with condition）"
    else
        echo "⚠️  未配置启动顺序，可能导致 API 在 PostgreSQL 启动前连接"
    fi
fi
echo ""

# 7. 提供修复建议
echo "=== 修复建议 ==="
echo ""
echo "如果配置不匹配，可能的解决方案："
echo ""
echo "1. 确保 docker-compose.1panel.yml 中的密码配置正确"
echo "2. 停止并删除 PostgreSQL 容器和数据："
echo "   docker-compose -f docker-compose.1panel.yml stop postgres"
echo "   docker-compose -f docker-compose.1panel.yml rm -f postgres"
echo "   rm -rf /data/mem0/postgres/*"
echo ""
echo "3. 重新启动服务："
echo "   docker-compose -f docker-compose.1panel.yml up -d postgres"
echo "   sleep 10  # 等待 PostgreSQL 完全启动"
echo "   docker-compose -f docker-compose.1panel.yml up -d mem0-api"
echo ""
echo "4. 检查日志："
echo "   docker logs mem0_postgres --tail 20"
echo "   docker logs mem0-api --tail 20"

