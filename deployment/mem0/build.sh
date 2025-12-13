#!/bin/bash
# Mem0 API 镜像构建脚本

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 镜像名称和标签
IMAGE_NAME="mem0-api"
IMAGE_TAG="${1:-latest}"

echo "Building Mem0 API Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"

# 构建镜像
docker build \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -f "${SCRIPT_DIR}/Dockerfile" \
    "${PROJECT_ROOT}"

echo "Build completed: ${IMAGE_NAME}:${IMAGE_TAG}"

# 可选：显示镜像信息
echo ""
echo "Image info:"
docker images "${IMAGE_NAME}:${IMAGE_TAG}"

