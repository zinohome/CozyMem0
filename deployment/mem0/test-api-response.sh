#!/bin/bash

# Mem0 API 响应格式测试脚本
# 用于验证 Mem0 API 的实际响应格式，确保适配代码正确

set -e

API_URL="${MEM0_API_URL:-http://localhost:8888}"
USER_ID="test_user_$(date +%s)"

echo "=== Mem0 API 响应格式测试 ==="
echo "API URL: $API_URL"
echo "Test User ID: $USER_ID"
echo ""

# 检查 API 是否可用
echo "1. 检查 API 服务..."
if ! curl -s "$API_URL/docs" > /dev/null 2>&1; then
  echo "❌ API 服务不可用，请先启动 Mem0 API 服务"
  exit 1
fi
echo "✅ API 服务可用"
echo ""

# 测试创建记忆
echo "2. 测试创建记忆..."
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/memories" \
  -H "Content-Type: application/json" \
  -d "{
    \"messages\": [
      {\"role\": \"user\", \"content\": \"这是一个测试记忆，用于验证 API 响应格式\"}
    ],
    \"user_id\": \"$USER_ID\"
  }")

echo "创建记忆响应："
echo "$CREATE_RESPONSE" | jq . 2>/dev/null || echo "$CREATE_RESPONSE"
echo ""

# 提取记忆 ID（如果响应中有）
MEMORY_ID=$(echo "$CREATE_RESPONSE" | jq -r '.results[0].id // .id // empty' 2>/dev/null || echo "")

# 测试获取所有记忆
echo "3. 测试获取所有记忆..."
GET_ALL_RESPONSE=$(curl -s "$API_URL/memories?user_id=$USER_ID")

echo "获取所有记忆响应："
echo "$GET_ALL_RESPONSE" | jq . 2>/dev/null || echo "$GET_ALL_RESPONSE"
echo ""

# 分析响应格式
echo "4. 分析响应格式..."
if echo "$GET_ALL_RESPONSE" | jq -e '.results' > /dev/null 2>&1; then
  echo "✅ 响应格式：{results: [...]}"
  RESULTS_COUNT=$(echo "$GET_ALL_RESPONSE" | jq '.results | length' 2>/dev/null || echo "0")
  echo "   记忆数量: $RESULTS_COUNT"
elif echo "$GET_ALL_RESPONSE" | jq -e 'type == "array"' > /dev/null 2>&1; then
  echo "✅ 响应格式：数组 [...]"
  RESULTS_COUNT=$(echo "$GET_ALL_RESPONSE" | jq 'length' 2>/dev/null || echo "0")
  echo "   记忆数量: $RESULTS_COUNT"
else
  echo "⚠️  响应格式：未知格式"
  echo "   需要手动检查响应结构"
fi
echo ""

# 测试搜索记忆
echo "5. 测试搜索记忆..."
SEARCH_RESPONSE=$(curl -s -X POST "$API_URL/search" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"测试\",
    \"user_id\": \"$USER_ID\"
  }")

echo "搜索记忆响应："
echo "$SEARCH_RESPONSE" | jq . 2>/dev/null || echo "$SEARCH_RESPONSE"
echo ""

# 分析搜索响应格式
echo "6. 分析搜索响应格式..."
if echo "$SEARCH_RESPONSE" | jq -e '.results' > /dev/null 2>&1; then
  echo "✅ 搜索响应格式：{results: [...]}"
elif echo "$SEARCH_RESPONSE" | jq -e 'type == "array"' > /dev/null 2>&1; then
  echo "✅ 搜索响应格式：数组 [...]"
else
  echo "⚠️  搜索响应格式：未知格式"
fi
echo ""

# 测试获取单个记忆（如果有 ID）
if [ -n "$MEMORY_ID" ]; then
  echo "7. 测试获取单个记忆 (ID: $MEMORY_ID)..."
  GET_ONE_RESPONSE=$(curl -s "$API_URL/memories/$MEMORY_ID")
  
  echo "获取单个记忆响应："
  echo "$GET_ONE_RESPONSE" | jq . 2>/dev/null || echo "$GET_ONE_RESPONSE"
  echo ""
  
  # 检查时间戳字段
  echo "8. 检查时间戳字段..."
  if echo "$GET_ONE_RESPONSE" | jq -e '.created_at' > /dev/null 2>&1; then
    CREATED_AT=$(echo "$GET_ONE_RESPONSE" | jq -r '.created_at' 2>/dev/null || echo "")
    echo "✅ 找到 created_at 字段: $CREATED_AT"
    echo "   类型: $(echo "$GET_ONE_RESPONSE" | jq -r '.created_at | type' 2>/dev/null || echo "unknown")"
  else
    echo "⚠️  未找到 created_at 字段"
  fi
  echo ""
fi

# 生成适配建议
echo "=== 适配建议 ==="
echo ""
echo "根据测试结果，请检查以下适配代码："
echo "1. deployment/mem0/webui-adapters/useMemoriesApi.mem0.ts"
echo "   - 响应格式适配（results 字段 vs 数组）"
echo "   - 时间戳字段处理"
echo "   - 记忆字段映射（memory vs content vs text）"
echo ""
echo "2. 如果响应格式与假设不同，需要更新适配代码"

