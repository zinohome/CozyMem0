#!/bin/bash
# 启动 mem0-api，等待 PostgreSQL 就绪

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== 启动 mem0-api（等待 PostgreSQL 就绪）==="
echo ""

# 1. 确保 PostgreSQL 正在运行
if ! docker ps | grep -q mem0_postgres; then
    echo "⚠️  PostgreSQL 容器未运行，先启动 PostgreSQL..."
    cd "$SCRIPT_DIR"
    docker-compose -f docker-compose.1panel.yml up -d postgres
fi

# 2. 等待 PostgreSQL 就绪
echo "等待 PostgreSQL 就绪..."
cd "$SCRIPT_DIR"
./scripts/wait-for-postgres.sh

# 3. 启动 mem0-api
echo ""
echo "启动 mem0-api..."
docker-compose -f docker-compose.1panel.yml up -d mem0-api

# 4. 等待 API 启动
echo "等待 mem0-api 启动（5 秒）..."
sleep 5

# 5. 检查日志
echo ""
echo "检查 mem0-api 日志..."
docker logs mem0-api --tail 30 | grep -i "error\|postgres\|started\|ready" || echo "✅ 无错误"

echo ""
echo "=== 启动完成 ==="
echo ""
echo "如果仍有错误，请检查："
echo "  1. PostgreSQL 日志：docker logs mem0_postgres --tail 20"
echo "  2. mem0-api 日志：docker logs mem0-api --tail 20"
echo "  3. 运行诊断：./scripts/check-postgres-connection.sh"

