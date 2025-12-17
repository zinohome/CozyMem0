#!/bin/bash

# API端点完整测试脚本
# 测试所有外部服务和POC项目的API端点

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务地址配置
COGNEE_API_URL="http://192.168.66.11:8000"
MEMOBASE_PROJECT_URL="http://192.168.66.11:8019"
MEM0_API_URL="http://192.168.66.11:8888"
POC_API_URL="http://localhost:8080"

# 测试数据集
DATASET_NAME="kb_tech"
TEST_USER_ID="test_user_001"
TEST_SESSION_ID="test_session_001"

# 输出文件
OUTPUT_DIR="test_results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="${OUTPUT_DIR}/api_test_results_${TIMESTAMP}.json"
LOG_FILE="${OUTPUT_DIR}/api_test_log_${TIMESTAMP}.txt"

# 创建输出目录
mkdir -p "${OUTPUT_DIR}"

# 日志函数
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}✗${NC} $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "${LOG_FILE}"
}

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local description=$5
    
    log "测试: ${name}"
    log "  描述: ${description}"
    log "  方法: ${method}"
    log "  URL: ${url}"
    
    if [ -n "$data" ]; then
        log "  数据: ${data}"
    fi
    
    # 执行请求
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "${url}" \
            -H "Content-Type: application/json" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X "${method}" "${url}" \
            -H "Content-Type: application/json" \
            -d "${data}" 2>&1)
    fi
    
    # 分离HTTP状态码和响应体
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # 检查HTTP状态码
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        log_success "HTTP状态码: ${http_code}"
        echo "$body" | jq . 2>/dev/null || echo "$body" | tee -a "${LOG_FILE}"
        echo ""
        return 0
    else
        log_error "HTTP状态码: ${http_code}"
        echo "$body" | tee -a "${LOG_FILE}"
        echo ""
        return 1
    fi
}

# 开始测试
log "=========================================="
log "开始API端点完整测试"
log "测试时间: $(date)"
log "=========================================="
echo ""

# ==========================================
# 1. 测试外部服务 - Cognee
# ==========================================
log "=========================================="
log "1. 测试 Cognee API"
log "=========================================="

# 1.1 Cognee 健康检查
test_endpoint \
    "Cognee Health Check" \
    "GET" \
    "${COGNEE_API_URL}/health" \
    "" \
    "Cognee服务健康检查"

# 1.2 Cognee 搜索知识
test_endpoint \
    "Cognee Search Knowledge" \
    "POST" \
    "${COGNEE_API_URL}/api/v1/search" \
    "{\"query\": \"Python编程基础\", \"datasets\": [\"${DATASET_NAME}\"], \"search_type\": \"GRAPH_COMPLETION\", \"top_k\": 5}" \
    "从Cognee知识库搜索知识"

# 1.3 Cognee 列出数据集
test_endpoint \
    "Cognee List Datasets" \
    "GET" \
    "${COGNEE_API_URL}/api/v1/datasets" \
    "" \
    "列出Cognee中的所有数据集"

echo ""

# ==========================================
# 2. 测试外部服务 - Memobase
# ==========================================
log "=========================================="
log "2. 测试 Memobase API"
log "=========================================="

# Memobase API 端点需要根据实际API文档调整
# 这里使用通用的测试方式
log_warning "Memobase API测试需要根据实际API文档调整端点"

# 2.1 Memobase 健康检查（如果存在）
test_endpoint \
    "Memobase Health Check" \
    "GET" \
    "${MEMOBASE_PROJECT_URL}/health" \
    "" \
    "Memobase服务健康检查（如果支持）"

echo ""

# ==========================================
# 3. 测试外部服务 - Mem0
# ==========================================
log "=========================================="
log "3. 测试 Mem0 API"
log "=========================================="

# 3.1 Mem0 健康检查
test_endpoint \
    "Mem0 Health Check" \
    "GET" \
    "${MEM0_API_URL}/health" \
    "" \
    "Mem0服务健康检查"

# 3.2 Mem0 搜索记忆（当前会话）
test_endpoint \
    "Mem0 Search Memories (Current Session)" \
    "POST" \
    "${MEM0_API_URL}/api/v1/search" \
    "{\"query\": \"用户信息\", \"user_id\": \"${TEST_USER_ID}\", \"agent_id\": \"${TEST_SESSION_ID}\"}" \
    "搜索当前会话的记忆"

# 3.3 Mem0 搜索记忆（跨会话）
test_endpoint \
    "Mem0 Search Memories (Cross Session)" \
    "POST" \
    "${MEM0_API_URL}/api/v1/search" \
    "{\"query\": \"用户信息\", \"user_id\": \"${TEST_USER_ID}\"}" \
    "搜索跨会话的记忆"

# 3.4 Mem0 创建记忆
test_endpoint \
    "Mem0 Create Memory" \
    "POST" \
    "${MEM0_API_URL}/api/v1/memories" \
    "{\"messages\": [{\"role\": \"user\", \"content\": \"我是测试用户，喜欢Python编程\"}, {\"role\": \"assistant\", \"content\": \"好的，我记住了\"}], \"user_id\": \"${TEST_USER_ID}\", \"agent_id\": \"${TEST_SESSION_ID}\"}" \
    "创建新的记忆"

# 3.5 Mem0 获取用户记忆列表
test_endpoint \
    "Mem0 List User Memories" \
    "GET" \
    "${MEM0_API_URL}/api/v1/users/${TEST_USER_ID}/memories" \
    "" \
    "获取用户的所有记忆（如果支持）"

echo ""

# ==========================================
# 4. 测试 POC 项目 API
# ==========================================
log "=========================================="
log "4. 测试 POC 项目 API"
log "=========================================="

# 4.1 POC 根路径
test_endpoint \
    "POC Root" \
    "GET" \
    "${POC_API_URL}/" \
    "" \
    "POC项目根路径"

# 4.2 POC 健康检查
test_endpoint \
    "POC Health Check" \
    "GET" \
    "${POC_API_URL}/health" \
    "" \
    "POC服务健康检查"

# 4.3 POC 调试状态
test_endpoint \
    "POC Debug Status" \
    "GET" \
    "${POC_API_URL}/api/v1/debug/status" \
    "" \
    "查看POC服务状态和配置"

# 4.4 POC 发送消息（标准接口）
test_endpoint \
    "POC Send Message" \
    "POST" \
    "${POC_API_URL}/api/v1/conversations/${TEST_SESSION_ID}/messages" \
    "{\"message\": \"你好，我想了解一下Python编程\", \"user_id\": \"${TEST_USER_ID}\", \"session_id\": \"${TEST_SESSION_ID}\", \"dataset_names\": [\"${DATASET_NAME}\"]}" \
    "发送消息并获取响应（标准接口）"

# 4.5 POC 测试对话（返回完整上下文）
test_endpoint \
    "POC Test Conversation" \
    "POST" \
    "${POC_API_URL}/api/v1/test/conversation" \
    "{\"user_id\": \"${TEST_USER_ID}\", \"session_id\": \"${TEST_SESSION_ID}\", \"message\": \"你好，我是测试用户，我是一名软件工程师，对Python很感兴趣\", \"dataset_names\": [\"${DATASET_NAME}\"]}" \
    "测试对话接口（返回完整上下文信息）"

# 4.6 POC 获取用户画像
test_endpoint \
    "POC Get User Profile" \
    "GET" \
    "${POC_API_URL}/api/v1/users/${TEST_USER_ID}/profile" \
    "" \
    "获取用户画像"

# 4.7 POC 第二次对话（测试记忆功能）
test_endpoint \
    "POC Second Conversation (Memory Test)" \
    "POST" \
    "${POC_API_URL}/api/v1/test/conversation" \
    "{\"user_id\": \"${TEST_USER_ID}\", \"session_id\": \"${TEST_SESSION_ID}\", \"message\": \"我之前说过我的职业是什么？\", \"dataset_names\": [\"${DATASET_NAME}\"]}" \
    "第二次对话，测试记忆功能"

# 4.8 POC 新会话（跨会话记忆测试）
test_endpoint \
    "POC New Session (Cross-Session Memory)" \
    "POST" \
    "${POC_API_URL}/api/v1/test/conversation" \
    "{\"user_id\": \"${TEST_USER_ID}\", \"session_id\": \"test_session_002\", \"message\": \"你还记得我的职业吗？\", \"dataset_names\": [\"${DATASET_NAME}\"]}" \
    "新会话，测试跨会话记忆"

echo ""

# ==========================================
# 测试完成
# ==========================================
log "=========================================="
log "API端点测试完成"
log "测试时间: $(date)"
log "=========================================="
log "测试结果已保存到: ${LOG_FILE}"
log "请查看详细日志了解每个端点的测试结果"
