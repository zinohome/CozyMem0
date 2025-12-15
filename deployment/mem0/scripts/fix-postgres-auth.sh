#!/bin/bash
# 修复 PostgreSQL 认证问题

set -e

echo "=== PostgreSQL 认证问题修复 ==="
echo ""

# 1. 检查当前状态
echo "1. 检查当前状态..."
if docker ps | grep -q mem0_postgres; then
    echo "✅ PostgreSQL 容器正在运行"
else
    echo "⚠️  PostgreSQL 容器未运行"
fi

if docker ps | grep -q mem0-api; then
    echo "✅ mem0-api 容器正在运行"
else
    echo "⚠️  mem0-api 容器未运行"
fi
echo ""

# 2. 检查配置
echo "2. 检查配置..."
POSTGRES_USER=$(grep "POSTGRES_USER" docker-compose.1panel.yml | head -1 | cut -d: -f2 | tr -d ' "')
POSTGRES_PASSWORD=$(grep "POSTGRES_PASSWORD" docker-compose.1panel.yml | head -1 | cut -d: -f2 | tr -d ' "')
POSTGRES_DB=$(grep "POSTGRES_DB" docker-compose.1panel.yml | head -1 | cut -d: -f2 | tr -d ' "')

echo "docker-compose.1panel.yml 配置："
echo "  User: $POSTGRES_USER"
echo "  Password: ${POSTGRES_PASSWORD:0:3}***"
echo "  Database: $POSTGRES_DB"
echo ""

# 3. 提供修复选项
echo "3. 修复选项："
echo ""
echo "选项 A：重置 PostgreSQL（会删除所有数据）"
echo "选项 B：修改 PostgreSQL 密码以匹配配置"
echo "选项 C：检查并修复配置不一致"
echo ""

read -p "选择修复方式 (A/B/C): " -n 1 -r
echo ""

case $REPLY in
    A|a)
        echo ""
        echo "⚠️  警告：这将删除所有 PostgreSQL 数据！"
        read -p "确认继续？(yes/N): " -r
        echo ""
        
        if [[ $REPLY == "yes" ]]; then
            echo "4. 停止服务..."
            docker-compose -f docker-compose.1panel.yml stop postgres mem0-api
            
            echo "5. 删除 PostgreSQL 容器..."
            docker-compose -f docker-compose.1panel.yml rm -f postgres
            
            echo "6. 删除数据目录..."
            if [ -d "/data/mem0/postgres" ]; then
                rm -rf /data/mem0/postgres/*
                echo "✅ 数据已删除"
            else
                echo "⚠️  数据目录不存在: /data/mem0/postgres"
                mkdir -p /data/mem0/postgres
            fi
            
            echo "7. 启动 PostgreSQL..."
            docker-compose -f docker-compose.1panel.yml up -d postgres
            
            echo "8. 等待 PostgreSQL 启动（15 秒）..."
            sleep 15
            
            echo "9. 检查 PostgreSQL 状态..."
            if docker ps | grep -q mem0_postgres; then
                echo "✅ PostgreSQL 容器已启动"
                
                # 等待 PostgreSQL 完全就绪
                echo "10. 等待 PostgreSQL 就绪..."
                for i in {1..30}; do
                    if docker exec mem0_postgres pg_isready -U "$POSTGRES_USER" > /dev/null 2>&1; then
                        echo "✅ PostgreSQL 已就绪"
                        break
                    fi
                    echo "   等待中... ($i/30)"
                    sleep 1
                done
                
                # 验证连接
                echo "11. 验证连接..."
                if docker exec mem0_postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" > /dev/null 2>&1; then
                    echo "✅ PostgreSQL 连接成功"
                else
                    echo "❌ PostgreSQL 连接失败"
                fi
            else
                echo "❌ PostgreSQL 容器启动失败"
                echo "请检查日志：docker logs mem0_postgres"
            fi
            
            echo ""
            echo "12. 启动 mem0-api..."
            docker-compose -f docker-compose.1panel.yml up -d mem0-api
            
            echo ""
            echo "13. 检查 mem0-api 日志..."
            sleep 5
            docker logs mem0-api --tail 20 | grep -i "error\|postgres" || echo "✅ 未发现错误"
        else
            echo "操作已取消"
        fi
        ;;
    B|b)
        echo ""
        echo "修改 PostgreSQL 密码..."
        
        if docker ps | grep -q mem0_postgres; then
            # 尝试使用当前配置连接
            if docker exec mem0_postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" > /dev/null 2>&1; then
                echo "✅ 当前密码正确，无需修改"
            else
                echo "⚠️  当前密码不正确，需要重置数据"
                echo "请选择选项 A 重置 PostgreSQL"
            fi
        else
            echo "❌ PostgreSQL 容器未运行"
        fi
        ;;
    C|c)
        echo ""
        echo "检查配置不一致..."
        ./scripts/check-postgres-connection.sh
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "=== 修复完成 ==="
echo ""
echo "验证步骤："
echo "  1. 检查 mem0-api 日志："
echo "     docker logs mem0-api --tail 20"
echo ""
echo "  2. 测试 API："
echo "     curl http://192.168.66.11:8888/docs"
echo ""

