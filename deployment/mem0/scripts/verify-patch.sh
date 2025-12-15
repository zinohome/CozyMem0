#!/bin/bash
# 验证 CORS patch 是否正确应用

set -e

echo "=== 验证 CORS Patch 应用 ==="
echo ""

# 检查 patch 文件是否存在
if [ ! -f "deployment/mem0/patches/cors.patch" ]; then
    echo "❌ Patch 文件不存在: deployment/mem0/patches/cors.patch"
    exit 1
fi
echo "✅ Patch 文件存在"

# 检查源文件
if [ ! -f "projects/mem0/server/main.py" ]; then
    echo "❌ 源文件不存在: projects/mem0/server/main.py"
    exit 1
fi
echo "✅ 源文件存在"

# 创建临时目录测试 patch
TEMP_DIR=$(mktemp -d)
echo "临时目录: $TEMP_DIR"

# 复制源文件到临时目录
cp projects/mem0/server/main.py "$TEMP_DIR/main.py"

# 应用 patch
echo ""
echo "应用 patch..."
cd "$TEMP_DIR"
if patch -p0 < "$OLDPWD/deployment/mem0/patches/cors.patch" 2>&1; then
    echo "✅ Patch 应用成功"
    
    # 检查是否包含 CORS 代码
    if grep -q "CORSMiddleware" "$TEMP_DIR/main.py"; then
        echo "✅ 找到 CORSMiddleware 导入"
    else
        echo "❌ 未找到 CORSMiddleware 导入"
        exit 1
    fi
    
    if grep -q "app.add_middleware" "$TEMP_DIR/main.py"; then
        echo "✅ 找到 CORS 中间件配置"
    else
        echo "❌ 未找到 CORS 中间件配置"
        exit 1
    fi
    
    echo ""
    echo "=== Patch 应用后的关键代码 ==="
    grep -A 5 "CORSMiddleware" "$TEMP_DIR/main.py" | head -10
    echo ""
    grep -A 10 "app.add_middleware" "$TEMP_DIR/main.py" | head -15
    
else
    echo "❌ Patch 应用失败"
    echo "检查 patch 文件格式和源文件是否匹配"
    exit 1
fi

# 清理
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Patch 验证完成！"

