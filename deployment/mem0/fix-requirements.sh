#!/bin/bash
# 快速修复 requirements.txt 文件

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REQUIREMENTS_FILE="${PROJECT_ROOT}/projects/mem0/server/requirements.txt"

echo "修复 requirements.txt 文件..."
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

# 替换 psycopg 为 psycopg[pool]
if grep -q "psycopg\[pool\]" "${REQUIREMENTS_FILE}"; then
    echo "✅ 文件已包含 psycopg[pool]，无需修改"
else
    echo "正在修改文件..."
    # 使用 sed 替换（兼容不同系统）
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' 's/^psycopg>=/psycopg[pool]>=/' "${REQUIREMENTS_FILE}"
        sed -i '' 's/^psycopg$/psycopg[pool]>=3.2.8/' "${REQUIREMENTS_FILE}"
    else
        # Linux
        sed -i 's/^psycopg>=/psycopg[pool]>=/' "${REQUIREMENTS_FILE}"
        sed -i 's/^psycopg$/psycopg[pool]>=3.2.8/' "${REQUIREMENTS_FILE}"
    fi
    echo "✅ 文件已修改"
fi

echo ""
echo "当前文件内容："
cat "${REQUIREMENTS_FILE}"
echo ""
echo "✅ 修复完成！现在可以运行 ./rebuild-api.sh 重新构建镜像"

