#!/bin/bash
# 测试 PostgreSQL 健康检查命令

set -e

echo "=== PostgreSQL 健康检查测试 ==="
echo ""

# 测试 1: pg_isready（不需要密码）
echo "1. 测试 pg_isready（不需要密码）..."
if docker exec mem0_postgres pg_isready -U mem0 -d mem0 2>&1; then
    echo "✅ pg_isready 成功（只检查服务器是否监听）"
else
    echo "❌ pg_isready 失败"
fi
echo ""

# 测试 2: pg_isready 详细输出
echo "2. pg_isready 详细输出："
docker exec mem0_postgres pg_isready -U mem0 -d mem0 -v 2>&1 || true
echo ""

# 测试 3: 使用 psql 进行实际连接测试（需要密码）
echo "3. 测试 psql 实际连接（需要密码）..."
if docker exec mem0_postgres psql -U mem0 -d mem0 -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ psql 连接成功（验证了密码和数据库可用性）"
else
    echo "❌ psql 连接失败"
fi
echo ""

# 测试 4: 使用环境变量中的密码
echo "4. 使用环境变量中的密码测试..."
POSTGRES_PASSWORD=$(docker exec mem0_postgres env | grep POSTGRES_PASSWORD | cut -d= -f2)
if [ -n "$POSTGRES_PASSWORD" ]; then
    echo "   密码已设置（长度: ${#POSTGRES_PASSWORD}）"
    # 注意：psql 在容器内可以通过 peer 认证或环境变量，不需要显式密码
    if docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" mem0_postgres psql -U mem0 -d mem0 -c "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ 使用环境变量密码连接成功"
    else
        echo "⚠️  使用环境变量密码连接失败（可能不需要，因为容器内认证）"
    fi
else
    echo "⚠️  未找到 POSTGRES_PASSWORD 环境变量"
fi
echo ""

echo "=== 结论 ==="
echo ""
echo "pg_isready 特点："
echo "  - ✅ 不需要密码（只检查服务器是否监听）"
echo "  - ✅ 非常快速（< 100ms）"
echo "  - ⚠️  不验证密码认证是否可用"
echo "  - ⚠️  不验证数据库是否真正可连接"
echo ""
echo "psql 特点："
echo "  - ✅ 验证实际连接（包括密码认证）"
echo "  - ✅ 验证数据库是否真正可用"
echo "  - ⚠️  需要密码（但在容器内可能通过 peer 认证）"
echo "  - ⚠️  稍慢（需要 200-500ms）"
echo ""
echo "建议："
echo "  - 如果只需要检查服务器是否启动：使用 pg_isready（当前配置）"
echo "  - 如果需要验证密码认证：使用 psql（更严格）"

