#!/bin/bash
# 强制重新构建 Mem0 API 镜像（切换到 Qdrant）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

IMAGE_NAME="mem0-api"
IMAGE_TAG="latest"

echo "=== 强制重新构建 Mem0 API 镜像（切换到 Qdrant）==="
echo ""

# 1. 验证补丁文件
echo "1. 验证补丁文件..."
if [ ! -f "$SCRIPT_DIR/../patches/switch-to-qdrant.patch" ]; then
    echo "❌ 补丁文件不存在: $SCRIPT_DIR/../patches/switch-to-qdrant.patch"
    exit 1
fi
echo "✅ 补丁文件存在"
echo ""

# 2. 验证 requirements.txt
echo "2. 验证 requirements.txt..."
if ! grep -q "qdrant-client" "${PROJECT_ROOT}/projects/mem0/server/requirements.txt"; then
    echo "❌ 错误：requirements.txt 不包含 qdrant-client"
    echo "当前内容："
    cat "${PROJECT_ROOT}/projects/mem0/server/requirements.txt"
    exit 1
fi
echo "✅ requirements.txt 包含 qdrant-client"
echo ""

# 3. 停止并删除旧容器
echo "3. 停止并删除旧容器..."
docker stop mem0-api 2>/dev/null || true
docker rm mem0-api 2>/dev/null || true
echo "✅ 旧容器已清理"
echo ""

# 4. 删除旧镜像
echo "4. 删除旧镜像..."
docker rmi "${IMAGE_NAME}:${IMAGE_TAG}" 2>/dev/null || true
echo "✅ 旧镜像已删除"
echo ""

# 5. 清理构建缓存
echo "5. 清理构建缓存..."
docker builder prune -f > /dev/null 2>&1 || true
echo "✅ 构建缓存已清理"
echo ""

# 6. 重新构建镜像
echo "6. 重新构建镜像（不使用缓存）..."
cd "$SCRIPT_DIR/.."
docker build \
    --no-cache \
    --progress=plain \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -f Dockerfile \
    "$PROJECT_ROOT" 2>&1 | tee /tmp/mem0-build.log

# 检查构建日志
if grep -q "patching file main.py" /tmp/mem0-build.log; then
    echo ""
    echo "✅ 补丁已应用（在构建日志中确认）"
else
    echo ""
    echo "⚠️  未找到补丁应用信息"
    echo "   请检查构建日志: /tmp/mem0-build.log"
fi

echo ""
echo "=== 构建完成 ==="
echo ""

# 7. 验证镜像
echo "7. 验证镜像..."
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" python -c "from qdrant_client import QdrantClient; print('✅ Qdrant 客户端可用')" 2>/dev/null; then
    echo "✅ 验证成功：Qdrant 客户端已包含在镜像中"
else
    echo "❌ 验证失败：Qdrant 客户端未包含在镜像中"
    exit 1
fi

# 检查 main.py 配置
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" grep -q "provider.*qdrant" /app/main.py 2>/dev/null; then
    echo "✅ 验证成功：Qdrant 配置已包含"
else
    echo "❌ 验证失败：Qdrant 配置未找到"
    exit 1
fi

echo ""
echo "=== 镜像信息 ==="
docker images "${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "✅ 构建完成！现在可以启动服务："
echo "   docker-compose -f docker-compose.1panel.yml up -d"
echo ""
echo "注意："
echo "  - 确保 Qdrant 服务已启动"
echo "  - 旧数据需要迁移（如果需要）"

