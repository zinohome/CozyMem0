#!/bin/bash
# 启动 POC 服务的脚本

# 设置服务地址（根据您提供的地址）
export COGNEE_API_URL="http://192.168.66.11:8000"
export MEMOBASE_PROJECT_URL="http://192.168.66.11:8019"
export MEMOBASE_API_KEY="${MEMOBASE_API_KEY:-secret}"
export MEM0_API_URL="http://192.168.66.11:8888"

# 检查 OpenAI API Key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  警告: OPENAI_API_KEY 环境变量未设置"
    echo "请设置 OPENAI_API_KEY 环境变量："
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "或者创建 .env 文件并添加："
    echo "  OPENAI_API_KEY=your-api-key-here"
    echo ""
    read -p "是否继续启动服务？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 设置其他可选配置
export OPENAI_MODEL="${OPENAI_MODEL:-gpt-4}"
# OpenAI Base URL（可选，如果使用自定义 OpenAI 兼容 API）
if [ -n "$OPENAI_BASE_URL" ]; then
    echo "使用自定义 OpenAI Base URL: $OPENAI_BASE_URL"
fi
export APP_HOST="${APP_HOST:-0.0.0.0}"
export APP_PORT="${APP_PORT:-8080}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

echo "=========================================="
echo "启动 Conversational Agent POC 服务"
echo "=========================================="
echo "Cognee URL: $COGNEE_API_URL"
echo "Memobase URL: $MEMOBASE_PROJECT_URL"
echo "Mem0 URL: $MEM0_API_URL"
if [ -n "$OPENAI_BASE_URL" ]; then
    echo "OpenAI Base URL: $OPENAI_BASE_URL"
fi
echo "服务地址: http://$APP_HOST:$APP_PORT"
echo "=========================================="
echo ""

# 启动服务
python3 -m src.main
