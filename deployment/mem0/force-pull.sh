#!/bin/bash
# 强制用 GitHub 上的代码覆盖本地更改

set -e

echo "=== 强制用远程代码覆盖本地更改 ==="
echo ""

# 获取当前分支名
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
REMOTE_BRANCH="origin/${CURRENT_BRANCH}"

echo "当前分支: ${CURRENT_BRANCH}"
echo "远程分支: ${REMOTE_BRANCH}"
echo ""

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  检测到本地有未提交的更改："
    git status --short
    echo ""
    read -p "确定要用远程代码覆盖这些更改吗？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 操作已取消"
        exit 1
    fi
fi

# 1. 获取最新的远程代码
echo "1. 获取最新的远程代码..."
git fetch origin

# 2. 强制重置到远程分支
echo "2. 强制重置到远程分支 ${REMOTE_BRANCH}..."
git reset --hard "${REMOTE_BRANCH}"

# 3. 清理未跟踪的文件（可选，谨慎使用）
echo ""
read -p "是否清理未跟踪的文件和目录？(y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "3. 清理未跟踪的文件..."
    git clean -fd
else
    echo "3. 跳过清理未跟踪的文件"
fi

echo ""
echo "✅ 完成！本地代码已强制同步到远程版本"
echo ""
echo "当前状态："
git status

