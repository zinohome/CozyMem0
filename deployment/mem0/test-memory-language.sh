#!/bin/bash
# 测试 Mem0 记忆语言处理行为

set -e

API_URL="${MEM0_API_URL:-http://192.168.66.11:8888}"
USER_ID="test_lang_$(date +%s)"

echo "=== Mem0 记忆语言处理测试 ==="
echo "API URL: $API_URL"
echo "Test User ID: $USER_ID"
echo ""

# 测试创建中文记忆
echo "1. 创建中文记忆..."
echo "   记忆 1: 我是湖北人"
echo "   记忆 2: 喜欢吃辣"
echo "   记忆 3: 我有高血脂"
echo ""

CREATE_RESPONSE=$(curl -s -X POST "$API_URL/memories" \
  -H "Content-Type: application/json" \
  -d "{
    \"messages\": [
      {\"role\": \"user\", \"content\": \"我是湖北人\"},
      {\"role\": \"user\", \"content\": \"喜欢吃辣\"},
      {\"role\": \"user\", \"content\": \"我有高血脂\"}
    ],
    \"user_id\": \"$USER_ID\"
  }")

echo "创建记忆响应："
echo "$CREATE_RESPONSE" | jq . 2>/dev/null || echo "$CREATE_RESPONSE"
echo ""

# 获取所有记忆
echo "2. 获取所有记忆..."
GET_ALL_RESPONSE=$(curl -s "$API_URL/memories?user_id=$USER_ID")

echo "所有记忆："
echo "$GET_ALL_RESPONSE" | jq '.results[] | {id, memory, metadata}' 2>/dev/null || echo "$GET_ALL_RESPONSE"
echo ""

# 分析记忆内容
echo "3. 分析记忆内容..."
if command -v jq > /dev/null 2>&1; then
    echo "记忆内容列表："
    echo "$GET_ALL_RESPONSE" | jq -r '.results[]?.memory // .results[]?.content // .results[]?.text // "N/A"' 2>/dev/null || echo "无法解析"
    echo ""
    
    # 检查是否有英文内容
    ENGLISH_COUNT=$(echo "$GET_ALL_RESPONSE" | jq -r '.results[]?.memory // .results[]?.content // .results[]?.text // ""' 2>/dev/null | grep -c "User is from\|User likes\|User has" || echo "0")
    if [ "$ENGLISH_COUNT" -gt 0 ]; then
        echo "⚠️  检测到英文记忆内容（可能是 Mem0 自动翻译/总结）"
    else
        echo "✅ 所有记忆保持原始语言"
    fi
fi

echo ""
echo "=== 测试完成 ==="
echo ""
echo "说明："
echo "- Mem0 使用 LLM 来处理和总结记忆内容"
echo "- 如果 LLM 配置为英文，可能会将中文记忆翻译/总结为英文"
echo "- 这是 Mem0 的默认行为，用于标准化和优化记忆存储"
echo ""
echo "如需保持原始语言，可能需要："
echo "1. 配置 LLM 使用中文模型"
echo "2. 在 prompt 中明确要求保持原始语言"
echo "3. 检查 Mem0 的配置选项"

