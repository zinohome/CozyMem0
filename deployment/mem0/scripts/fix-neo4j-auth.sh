#!/bin/bash
# 修复 Neo4j 认证问题

set -e

echo "=== Neo4j 认证问题修复脚本 ==="
echo ""

# 1. 检查 Neo4j 容器状态
echo "1. 检查 Neo4j 容器状态..."
if docker ps | grep -q mem0_neo4j; then
    echo "✅ Neo4j 容器正在运行"
    NEO4J_RUNNING=true
else
    echo "⚠️  Neo4j 容器未运行"
    NEO4J_RUNNING=false
fi
echo ""

# 2. 检查 Neo4j 日志
if [ "$NEO4J_RUNNING" = true ]; then
    echo "2. 检查 Neo4j 日志（最近 20 行）..."
    docker logs mem0_neo4j --tail 20 | grep -i "auth\|password\|started\|ready" || echo "未找到相关日志"
    echo ""
fi

# 3. 测试 Neo4j 连接
echo "3. 测试 Neo4j 连接..."
if [ "$NEO4J_RUNNING" = true ]; then
    if docker exec mem0_neo4j cypher-shell -u neo4j -p mem0graph "RETURN 1" > /dev/null 2>&1; then
        echo "✅ Neo4j 连接成功（密码正确）"
        echo ""
        echo "如果 Mem0 API 仍然报错，请检查："
        echo "  1. mem0-api 容器的环境变量是否正确"
        echo "  2. 网络连接是否正常"
        echo "  3. 重启 mem0-api 容器"
        exit 0
    else
        echo "❌ Neo4j 连接失败（密码可能不正确）"
        echo ""
    fi
else
    echo "⚠️  无法测试连接（容器未运行）"
    echo ""
fi

# 4. 提供修复选项
echo "4. 修复选项："
echo ""
echo "选项 A：重置 Neo4j 数据（会删除所有数据）"
echo "  这将删除 Neo4j 数据并重新初始化"
echo ""
read -p "是否重置 Neo4j 数据？(y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "⚠️  警告：这将删除所有 Neo4j 数据！"
    read -p "确认继续？(yes/N): " -r
    echo ""
    
    if [[ $REPLY == "yes" ]]; then
        echo "5. 停止 Neo4j 容器..."
        docker stop mem0_neo4j 2>/dev/null || true
        
        echo "6. 删除 Neo4j 数据..."
        if [ -d "/data/mem0/neo4j/data" ]; then
            rm -rf /data/mem0/neo4j/data/*
            echo "✅ 数据已删除"
        else
            echo "⚠️  数据目录不存在: /data/mem0/neo4j/data"
        fi
        
        echo "7. 启动 Neo4j 容器..."
        docker-compose -f docker-compose.1panel.yml up -d neo4j
        
        echo "8. 等待 Neo4j 启动（30 秒）..."
        sleep 30
        
        echo "9. 检查 Neo4j 状态..."
        if docker ps | grep -q mem0_neo4j; then
            echo "✅ Neo4j 容器已启动"
            echo ""
            echo "⚠️  重要：Neo4j 首次启动需要修改密码"
            echo "请执行以下步骤："
            echo "  1. 访问：http://192.168.66.11:8474"
            echo "  2. 使用默认用户名和密码登录：neo4j / neo4j"
            echo "  3. 修改密码为：mem0graph"
            echo "  4. 重启 mem0-api 容器"
        else
            echo "❌ Neo4j 容器启动失败"
            echo "请检查日志：docker logs mem0_neo4j"
        fi
    else
        echo "操作已取消"
    fi
else
    echo ""
    echo "选项 B：手动修复"
    echo ""
    echo "请手动执行以下步骤："
    echo "  1. 检查 Neo4j 容器日志："
    echo "     docker logs mem0_neo4j --tail 50"
    echo ""
    echo "  2. 测试连接："
    echo "     docker exec mem0_neo4j cypher-shell -u neo4j -p mem0graph 'RETURN 1'"
    echo ""
    echo "  3. 如果连接失败，访问 Neo4j 浏览器："
    echo "     http://192.168.66.11:8474"
    echo "     使用默认密码登录并修改密码"
    echo ""
    echo "  4. 确保 docker-compose.1panel.yml 中的配置正确："
    echo "     NEO4J_AUTH: neo4j/mem0graph"
    echo ""
    echo "  5. 重启 mem0-api 容器："
    echo "     docker-compose -f docker-compose.1panel.yml restart mem0-api"
fi

echo ""
echo "=== 脚本完成 ==="

