#!/bin/bash
# 快速修复 requirements.txt 文件
# 修复内容：
# 1. 将 psycopg 改为 psycopg[pool]
# 2. 将 mem0ai 改为 mem0ai[graph,vector_stores]（包含 Neo4j 等可选依赖）
# 3. 添加 langchain-neo4j 和 neo4j 依赖

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REQUIREMENTS_FILE="${PROJECT_ROOT}/projects/mem0/server/requirements.txt"

echo "=== 修复 requirements.txt 文件 ==="
echo "文件路径: ${REQUIREMENTS_FILE}"
echo ""

# 检查文件是否存在
if [ ! -f "${REQUIREMENTS_FILE}" ]; then
    echo "❌ 错误：文件不存在: ${REQUIREMENTS_FILE}"
    exit 1
fi

# 备份原文件
cp "${REQUIREMENTS_FILE}" "${REQUIREMENTS_FILE}.bak"
echo "✅ 已备份原文件到: ${REQUIREMENTS_FILE}.bak"
echo ""

# 写入完整的 requirements.txt 内容
echo "正在写入完整的 requirements.txt..."
cat > "${REQUIREMENTS_FILE}" << 'EOF'
fastapi==0.115.8
uvicorn==0.34.0
pydantic==2.10.4
# Mem0 核心包（包含 graph 可选依赖，支持 Neo4j）
mem0ai[graph,vector_stores]>=0.1.48
python-dotenv==1.0.1
# PostgreSQL 客户端（pgvector 需要）
psycopg[pool]>=3.2.8
# Neo4j 图数据库支持（Mem0 的 graph 可选依赖包含，但显式列出以确保安装）
langchain-neo4j>=0.4.0
neo4j>=5.23.1
EOF

echo "✅ 文件已更新"
echo ""

# 验证文件内容
echo "=== 验证文件内容 ==="
if grep -q "psycopg\[pool\]" "${REQUIREMENTS_FILE}"; then
    echo "✅ psycopg[pool] 已包含"
else
    echo "❌ 错误：psycopg[pool] 未找到"
    exit 1
fi

if grep -q "mem0ai\[graph,vector_stores\]" "${REQUIREMENTS_FILE}"; then
    echo "✅ mem0ai[graph,vector_stores] 已包含"
else
    echo "❌ 错误：mem0ai[graph,vector_stores] 未找到"
    exit 1
fi

if grep -q "langchain-neo4j" "${REQUIREMENTS_FILE}"; then
    echo "✅ langchain-neo4j 已包含"
else
    echo "❌ 错误：langchain-neo4j 未找到"
    exit 1
fi

if grep -q "^neo4j>=" "${REQUIREMENTS_FILE}"; then
    echo "✅ neo4j 已包含"
else
    echo "❌ 错误：neo4j 未找到"
    exit 1
fi

echo ""
echo "=== 当前文件内容 ==="
cat "${REQUIREMENTS_FILE}"
echo ""
echo "✅ 修复完成！现在可以运行 ./rebuild-api.sh 重新构建镜像"

