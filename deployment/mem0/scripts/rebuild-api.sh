#!/bin/bash
# 强制重新构建 Mem0 API 镜像（清理缓存）

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 镜像名称和标签
IMAGE_NAME="mem0-api"
IMAGE_TAG="${1:-latest}"

echo "=== 强制重新构建 Mem0 API 镜像 ==="
echo "镜像: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# 1. 停止并删除旧容器（如果存在）
echo "1. 停止并删除旧容器..."
docker stop mem0-api 2>/dev/null || true
docker rm mem0-api 2>/dev/null || true
echo "✅ 旧容器已清理"
echo ""

# 2. 删除旧镜像（如果存在）
echo "2. 删除旧镜像..."
docker rmi "${IMAGE_NAME}:${IMAGE_TAG}" 2>/dev/null || true
echo "✅ 旧镜像已删除"
echo ""

# 3. 清理构建缓存（可选，但确保使用最新配置）
echo "3. 清理 Docker 构建缓存..."
docker builder prune -f
echo "✅ 构建缓存已清理"
echo ""

# 4. 验证 requirements.txt 内容
echo "4. 验证 requirements.txt..."
if grep -q "psycopg\[pool\]" "${PROJECT_ROOT}/projects/mem0/server/requirements.txt"; then
    echo "✅ requirements.txt 包含 psycopg[pool]"
else
    echo "❌ 错误：requirements.txt 不包含 psycopg[pool]"
    echo "当前内容："
    cat "${PROJECT_ROOT}/projects/mem0/server/requirements.txt"
    exit 1
fi
echo ""

# 5. 验证 Dockerfile 内容
echo "5. 验证 Dockerfile..."
if grep -q "libpq-dev" "${SCRIPT_DIR}/Dockerfile" && grep -q "python3-dev" "${SCRIPT_DIR}/Dockerfile"; then
    echo "✅ Dockerfile 包含必要的系统依赖"
else
    echo "❌ 错误：Dockerfile 缺少必要的系统依赖"
    exit 1
fi
echo ""

# 6. 构建新镜像（不使用缓存）
echo "6. 构建新镜像（不使用缓存）..."
docker build \
    --no-cache \
    --progress=plain \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -f "${SCRIPT_DIR}/Dockerfile" \
    "${PROJECT_ROOT}"

echo ""
echo "=== 构建完成 ==="
echo ""

# 7. 验证镜像中的 psycopg
echo "7. 验证镜像中的 psycopg 安装..."
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" python -c "import psycopg; from psycopg_pool import ConnectionPool; print('✅ psycopg[pool] 已正确安装')" 2>/dev/null; then
    echo "✅ 验证成功：psycopg[pool] 已正确安装"
else
    echo "❌ 验证失败：psycopg[pool] 未正确安装"
    echo ""
    echo "检查已安装的包："
    docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" pip list | grep psycopg || echo "未找到 psycopg"
    exit 1
fi

echo ""
echo "=== 镜像信息 ==="
docker images "${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "✅ 构建完成！现在可以启动服务了："
echo "   docker-compose -f docker-compose.1panel.yml up -d mem0-api"

