#!/bin/bash
# Mem0 API 测试脚本
# 测试部署在 192.168.66.11:8888 的 Mem0 API

set -e

API_URL="${MEM0_API_URL:-http://192.168.66.11:8888}"
USER_ID="test_user_$(date +%s)"
TIMEOUT=10

echo "=== Mem0 API 测试 ==="
echo "API URL: $API_URL"
echo "Test User ID: $USER_ID"
echo ""

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    
    echo -n "测试 $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -L -w "\n%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null || echo -e "\n000")
    else
        response=$(curl -s -L -w "\n%{http_code}" --max-time $TIMEOUT -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$url" 2>/dev/null || echo -e "\n000")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ] || [ "$http_code" = "307" ]; then
        echo -e "${GREEN}✅ 成功 (HTTP $http_code)${NC}"
        if [ -n "$body" ] && [ "$body" != "null" ]; then
            echo "$body" | jq . 2>/dev/null || echo "$body" | head -n 5
        fi
        return 0
    elif [ "$http_code" = "000" ]; then
        echo -e "${RED}❌ 失败：无法连接到服务器${NC}"
        return 1
    else
        echo -e "${RED}❌ 失败 (HTTP $http_code)${NC}"
        echo "响应: $body" | head -n 3
        return 1
    fi
}

# 1. 检查 API 健康状态
echo "1. 检查 API 健康状态..."
if curl -s --max-time $TIMEOUT "$API_URL/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API 服务可访问${NC}"
    echo "   API 文档: $API_URL/docs"
else
    echo -e "${RED}❌ API 服务不可访问${NC}"
    echo "   请检查服务是否正在运行"
    exit 1
fi
echo ""

# 2. 测试根路径
echo "2. 测试 API 根路径..."
test_endpoint "根路径" "GET" "$API_URL/" ""
echo ""

# 3. 测试创建记忆
echo "3. 测试创建记忆..."
MEMORY_CONTENT="这是一个测试记忆，用于验证 Mem0 API 功能。创建时间: $(date '+%Y-%m-%d %H:%M:%S')"
CREATE_DATA=$(cat <<EOF
{
  "messages": [
    {
      "role": "user",
      "content": "$MEMORY_CONTENT"
    }
  ],
  "user_id": "$USER_ID",
  "metadata": {
    "test": true,
    "source": "api_test"
  }
}
EOF
)

if test_endpoint "创建记忆" "POST" "$API_URL/memories" "$CREATE_DATA"; then
    # 提取记忆 ID（如果响应中有）
    MEMORY_ID=$(echo "$body" | jq -r '.results[0].id // .id // empty' 2>/dev/null || echo "")
    if [ -n "$MEMORY_ID" ] && [ "$MEMORY_ID" != "null" ]; then
        echo "   记忆 ID: $MEMORY_ID"
    fi
else
    echo -e "${YELLOW}⚠️  创建记忆失败，但继续测试其他功能${NC}"
    MEMORY_ID=""
fi
echo ""

# 4. 测试获取所有记忆
echo "4. 测试获取所有记忆..."
test_endpoint "获取所有记忆" "GET" "$API_URL/memories?user_id=$USER_ID" ""
echo ""

# 5. 测试搜索记忆
echo "5. 测试搜索记忆..."
SEARCH_DATA=$(cat <<EOF
{
  "query": "测试",
  "user_id": "$USER_ID"
}
EOF
)
test_endpoint "搜索记忆" "POST" "$API_URL/search" "$SEARCH_DATA"
echo ""

# 6. 测试获取单个记忆（如果有 ID）
if [ -n "$MEMORY_ID" ] && [ "$MEMORY_ID" != "null" ]; then
    echo "6. 测试获取单个记忆 (ID: $MEMORY_ID)..."
    test_endpoint "获取单个记忆" "GET" "$API_URL/memories/$MEMORY_ID" ""
    echo ""
fi

# 7. 测试配置端点（只检查是否可访问）
echo "7. 测试配置端点..."
CONFIG_DATA='{"version": "v1.1", "llm": {"provider": "openai"}}'
test_endpoint "配置端点" "POST" "$API_URL/configure" "$CONFIG_DATA" || true
echo ""

# 总结
echo "=== 测试总结 ==="
echo "API URL: $API_URL"
echo "测试用户 ID: $USER_ID"
if [ -n "$MEMORY_ID" ] && [ "$MEMORY_ID" != "null" ]; then
    echo "创建的记忆 ID: $MEMORY_ID"
fi
echo ""
echo -e "${GREEN}✅ 基本功能测试完成！${NC}"
echo ""
echo "下一步："
echo "1. 访问 API 文档: $API_URL/docs"
echo "2. 使用 WebUI 测试（如果已部署）: http://192.168.66.11:3000"
echo "3. 查看 API 使用示例: deployment/mem0/README.md"

