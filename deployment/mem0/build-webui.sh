#!/bin/bash

# 构建 Mem0 WebUI Docker 镜像脚本
# 基于 OpenMemory UI，适配 Mem0 API

set -e

# 默认镜像名称和标签
IMAGE_NAME="mem0-webui"
IMAGE_TAG="${1:-latest}"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Building Mem0 WebUI Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Project root: $PROJECT_ROOT"

# 构建镜像
docker build \
  -f "$SCRIPT_DIR/webui.Dockerfile" \
  -t "${IMAGE_NAME}:${IMAGE_TAG}" \
  "$PROJECT_ROOT"

echo "Build completed: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "To run the image:"
echo "  docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8888 ${IMAGE_NAME}:${IMAGE_TAG}"

