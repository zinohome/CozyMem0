#!/bin/bash
# 构建 Mem0 WebUI 开发模式镜像

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
IMAGE_NAME="mem0-webui-dev"
IMAGE_TAG="${1:-latest}"

echo "=== 构建 Mem0 WebUI 开发模式镜像 ==="
echo "项目根目录: $PROJECT_ROOT"
echo "镜像名称: $IMAGE_NAME:$IMAGE_TAG"
echo ""

cd "$PROJECT_ROOT"

echo "开始构建..."
docker build \
  -t "${IMAGE_NAME}:${IMAGE_TAG}" \
  -f deployment/mem0/webui.dev.Dockerfile \
  .

echo ""
echo "✅ 构建完成！"
echo ""
echo "镜像信息："
docker images | grep "$IMAGE_NAME" | head -1
echo ""
echo "使用方法："
echo "  docker-compose -f deployment/mem0/docker-compose.dev.yml up -d"

