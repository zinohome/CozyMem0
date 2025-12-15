#!/bin/bash
# Mem0 API 镜像构建脚本
# 注意：此脚本会应用以下补丁（在 Dockerfile 中）：
#   - CORS 支持补丁 (cors.patch)
#   - 中文语言支持补丁 (chinese-language-support.patch)

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 镜像名称和标签
IMAGE_NAME="mem0-api"
IMAGE_TAG="${1:-latest}"

echo "Building Mem0 API Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "注意：构建过程会自动应用 CORS 和中文语言支持补丁"
echo ""

# 验证补丁文件存在
if [ ! -f "$SCRIPT_DIR/patches/cors.patch" ]; then
    echo "⚠️  警告：CORS 补丁文件不存在: $SCRIPT_DIR/patches/cors.patch"
    echo "   构建将继续，但 CORS 功能可能不可用"
fi

if [ ! -f "$SCRIPT_DIR/patches/chinese-language-support.patch" ]; then
    echo "⚠️  警告：中文语言支持补丁文件不存在: $SCRIPT_DIR/patches/chinese-language-support.patch"
    echo "   构建将继续，但中文语言支持可能不可用"
fi

# 构建镜像
echo "开始构建镜像..."
docker build \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -f "${SCRIPT_DIR}/Dockerfile" \
    "${PROJECT_ROOT}"

echo ""
echo "Build completed: ${IMAGE_NAME}:${IMAGE_TAG}"

# 可选：显示镜像信息
echo ""
echo "Image info:"
docker images "${IMAGE_NAME}:${IMAGE_TAG}"

# 可选：验证补丁是否应用成功
echo ""
echo "验证补丁应用..."
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" grep -q "app.add_middleware" /app/main.py 2>/dev/null; then
    echo "✅ CORS 中间件配置已包含"
else
    echo "⚠️  警告：未找到 CORS 中间件配置，补丁可能未成功应用"
fi

if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" grep -q "CUSTOM_FACT_EXTRACTION_PROMPT" /app/main.py 2>/dev/null; then
    echo "✅ 中文语言支持配置已包含"
else
    echo "⚠️  警告：未找到中文语言支持配置，补丁可能未成功应用"
fi

echo ""
echo "✅ 构建完成！"
echo ""
echo "如需强制重新构建（清理缓存），请使用："
echo "   ./scripts/rebuild-api.sh"
echo ""
echo "如需验证 CORS 补丁，请使用："
echo "   ./scripts/rebuild-with-cors.sh"

