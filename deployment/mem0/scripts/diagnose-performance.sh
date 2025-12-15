#!/bin/bash
# Mem0 性能诊断脚本

set -e

echo "=== Mem0 性能诊断 ==="
echo ""

# 1. 检查 Neo4j 连接
echo "1. 检查 Neo4j 连接..."
if docker exec mem0_neo4j cypher-shell -u neo4j -p mem0graph "RETURN 1" > /dev/null 2>&1; then
    echo "✅ Neo4j 连接正常"
    NEO4J_OK=true
else
    echo "❌ Neo4j 连接失败（这是主要性能瓶颈！）"
    echo "   建议立即修复 Neo4j 认证问题"
    NEO4J_OK=false
fi
echo ""

# 2. 检查 Mem0 API 日志中的错误
echo "2. 检查 Mem0 API 错误..."
ERROR_COUNT=$(docker logs mem0-api --tail 100 2>&1 | grep -i "neo4j\|auth\|error\|timeout" | wc -l || echo "0")
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️  发现 $ERROR_COUNT 个相关错误"
    echo "   最近的错误："
    docker logs mem0-api --tail 50 2>&1 | grep -i "neo4j\|auth\|error" | tail -5 || echo "无"
else
    echo "✅ 未发现明显错误"
fi
echo ""

# 3. 测试添加记忆的性能
echo "3. 测试添加记忆性能..."
START_TIME=$(date +%s%N)
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "http://192.168.66.11:8888/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "性能测试记忆"}],
    "user_id": "perf_test_'$(date +%s)'"
  }' 2>&1)

END_TIME=$(date +%s%N)
DURATION=$((($END_TIME - $START_TIME) / 1000000))  # 转换为毫秒

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 添加记忆成功"
    echo "   耗时: ${DURATION}ms"
    
    if [ "$DURATION" -gt 5000 ]; then
        echo "⚠️  性能警告：耗时超过 5 秒，可能存在问题"
    elif [ "$DURATION" -gt 2000 ]; then
        echo "⚠️  性能提示：耗时超过 2 秒，可能可以优化"
    else
        echo "✅ 性能正常"
    fi
else
    echo "❌ 添加记忆失败 (HTTP $HTTP_CODE)"
    echo "   响应: $BODY"
fi
echo ""

# 4. 分析性能瓶颈
echo "4. 性能瓶颈分析："
echo ""

if [ "$NEO4J_OK" = false ]; then
    echo "🔴 主要瓶颈：Neo4j 认证失败"
    echo "   影响：每次操作可能增加 5-30 秒延迟"
    echo "   建议：立即修复 Neo4j 认证（运行 ./fix-neo4j-auth.sh）"
    echo ""
fi

if [ "$DURATION" -gt 2000 ]; then
    echo "⚠️  性能瓶颈分析："
    echo "   - LLM 调用：200-2000ms（正常）"
    echo "   - 向量嵌入：50-200ms（正常）"
    echo "   - 数据库写入：50-300ms（正常）"
    if [ "$NEO4J_OK" = false ]; then
        echo "   - Neo4j 连接失败：+5000-30000ms（问题！）"
    fi
    echo ""
fi

# 5. 提供优化建议
echo "5. 优化建议："
echo ""

if [ "$NEO4J_OK" = false ]; then
    echo "   1. 【最重要】修复 Neo4j 认证："
    echo "      ./fix-neo4j-auth.sh"
    echo ""
fi

echo "   2. 使用更快的 LLM 模型："
echo "      在 docker-compose.1panel.yml 中设置："
echo "      OPENAI_MODEL: gpt-3.5-turbo  # 比 gpt-4 快 3-5 倍"
echo ""

echo "   3. 检查网络延迟："
echo "      ping 192.168.66.11"
echo ""

echo "   4. 检查数据库性能："
echo "      docker stats mem0_postgres mem0_neo4j"
echo ""

echo "=== 诊断完成 ==="

