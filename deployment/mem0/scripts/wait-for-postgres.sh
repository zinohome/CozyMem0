#!/bin/bash
# 等待 PostgreSQL 就绪的脚本

set -e

POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-mem0}"
POSTGRES_DB="${POSTGRES_DB:-mem0}"
MAX_ATTEMPTS=30
ATTEMPT=0

echo "等待 PostgreSQL 就绪..."
echo "  Host: $POSTGRES_HOST"
echo "  Port: $POSTGRES_PORT"
echo "  User: $POSTGRES_USER"
echo "  Database: $POSTGRES_DB"
echo ""

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    
    # 检查 PostgreSQL 是否就绪
    if docker exec mem0_postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
        echo "✅ PostgreSQL 已就绪（尝试 $ATTEMPT/$MAX_ATTEMPTS）"
        
        # 验证连接
        if docker exec mem0_postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" > /dev/null 2>&1; then
            echo "✅ PostgreSQL 连接验证成功"
            exit 0
        else
            echo "⚠️  PostgreSQL 就绪但连接失败，继续等待..."
        fi
    else
        echo "   等待中... ($ATTEMPT/$MAX_ATTEMPTS)"
    fi
    
    sleep 2
done

echo "❌ PostgreSQL 在 $MAX_ATTEMPTS 次尝试后仍未就绪"
exit 1

