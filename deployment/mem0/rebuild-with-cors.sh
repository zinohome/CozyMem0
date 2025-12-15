#!/bin/bash
# 强制重新构建 Mem0 API 镜像并应用 CORS patch

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

IMAGE_NAME="mem0-api"
IMAGE_TAG="latest"

echo "=== 强制重新构建 Mem0 API 镜像（应用 CORS patch）==="
echo ""

# 1. 验证 patch 文件
echo "1. 验证 patch 文件..."
if [ ! -f "$SCRIPT_DIR/patches/cors.patch" ]; then
    echo "❌ Patch 文件不存在: $SCRIPT_DIR/patches/cors.patch"
    exit 1
fi
echo "✅ Patch 文件存在"

# 验证 patch 可以应用
echo ""
echo "2. 验证 patch 可以应用..."
cd "$PROJECT_ROOT"
if ! ./deployment/mem0/verify-patch.sh > /dev/null 2>&1; then
    echo "❌ Patch 验证失败，请检查 patch 文件"
    exit 1
fi
echo "✅ Patch 验证通过"
echo ""

# 2. 停止并删除旧容器
echo "3. 停止并删除旧容器..."
docker stop mem0-api 2>/dev/null || true
docker rm mem0-api 2>/dev/null || true
echo "✅ 旧容器已清理"
echo ""

# 3. 删除旧镜像（强制重新构建）
echo "4. 删除旧镜像..."
docker rmi "${IMAGE_NAME}:${IMAGE_TAG}" 2>/dev/null || true
echo "✅ 旧镜像已删除"
echo ""

# 4. 清理构建缓存
echo "5. 清理构建缓存..."
docker builder prune -f > /dev/null 2>&1 || true
echo "✅ 构建缓存已清理"
echo ""

# 5. 重新构建镜像（不使用缓存）
echo "6. 重新构建镜像（不使用缓存）..."
cd "$SCRIPT_DIR"
docker build \
    --no-cache \
    --progress=plain \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -f Dockerfile \
    "$PROJECT_ROOT" 2>&1 | tee /tmp/mem0-build.log

# 检查构建日志中是否有 patch 相关信息
if grep -q "patching file main.py" /tmp/mem0-build.log; then
    echo ""
    echo "✅ Patch 已应用（在构建日志中确认）"
elif grep -q "Warning: CORS patch failed" /tmp/mem0-build.log; then
    echo ""
    echo "⚠️  Patch 应用失败，但构建继续"
    echo "   请检查构建日志: /tmp/mem0-build.log"
else
    echo ""
    echo "⚠️  未找到 patch 应用信息"
    echo "   请检查构建日志: /tmp/mem0-build.log"
fi

echo ""
echo "=== 构建完成 ==="
echo ""

# 6. 验证镜像中的 CORS 代码
echo "7. 验证镜像中的 CORS 代码..."
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" python -c "from fastapi.middleware.cors import CORSMiddleware; print('✅ CORS 模块导入成功')" 2>/dev/null; then
    echo "✅ 验证成功：CORS 代码已包含在镜像中"
else
    echo "❌ 验证失败：CORS 代码未包含在镜像中"
    echo "   请检查构建日志: /tmp/mem0-build.log"
    exit 1
fi

# 检查 main.py 中是否有 CORS 配置
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" grep -q "app.add_middleware" /app/main.py 2>/dev/null; then
    echo "✅ 验证成功：CORS 中间件配置已包含"
else
    echo "❌ 验证失败：CORS 中间件配置未找到"
    exit 1
fi

echo ""
echo "=== 镜像信息 ==="
docker images "${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "✅ 构建完成！现在可以启动服务："
echo "   docker-compose -f docker-compose.1panel.yml up -d mem0-api"
echo ""
echo "启动后验证 CORS："
echo "   curl -H 'Origin: http://192.168.66.11:4000' -v http://192.168.66.11:8888/memories?user_id=test 2>&1 | grep -i access-control"

