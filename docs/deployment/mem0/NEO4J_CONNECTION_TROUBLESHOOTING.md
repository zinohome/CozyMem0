# Neo4j 连接问题排查指南

## 问题现象

Neo4j 容器连接正常，但 Mem0 API 报认证失败错误。

## 诊断步骤

### 步骤 1：检查 mem0-api 容器中的环境变量

```bash
docker exec mem0-api env | grep -i neo4j
```

应该看到：
```
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=mem0graph
```

如果环境变量不正确或缺失，说明配置未正确传递。

### 步骤 2：从 mem0-api 容器测试 Neo4j 连接

```bash
cd /data/build/CozyMem0/deployment/mem0
./scripts/test-neo4j-from-api.sh
```

或手动测试：

```bash
docker exec mem0-api python3 -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://neo4j:7687', auth=('neo4j', 'mem0graph'))
with driver.session() as session:
    result = session.run('RETURN 1')
    print('连接成功:', result.single()[0])
driver.close()
"
```

### 步骤 3：检查网络连接

```bash
# 检查 mem0-api 是否能访问 neo4j 容器
docker exec mem0-api ping -c 1 neo4j

# 检查网络配置
docker network inspect 1panel-network | grep -A 10 "mem0\|neo4j"
```

### 步骤 4：检查启动顺序

Mem0 API 可能在 Neo4j 完全启动前就尝试连接。

**解决方案**：已更新 `docker-compose.1panel.yml`，添加了 `condition: service_started`。

重启服务：

```bash
docker-compose -f docker-compose.1panel.yml restart mem0-api
```

### 步骤 5：检查 Mem0 初始化时机

Mem0 在启动时（`main.py` 第 59 行）就初始化 `MEMORY_INSTANCE`，此时会尝试连接 Neo4j。

如果 Neo4j 还没准备好，会导致连接失败。

**解决方案**：
1. 确保 Neo4j 先启动并完全就绪
2. 重启 mem0-api 容器

## 常见问题和解决方案

### 问题 1：环境变量未传递

**症状**：`docker exec mem0-api env | grep NEO4J` 返回空

**解决**：
1. 检查 `docker-compose.1panel.yml` 中的环境变量配置
2. 确保格式正确（1Panel 使用 YAML 字典格式）
3. 重启容器

### 问题 2：网络连接问题

**症状**：`docker exec mem0-api ping neo4j` 失败

**解决**：
1. 检查容器是否在同一网络：`docker network inspect 1panel-network`
2. 确保两个容器都连接到 `1panel-network`
3. 重启容器

### 问题 3：启动顺序问题

**症状**：Mem0 API 启动时 Neo4j 还没准备好

**解决**：
1. 已更新 `docker-compose.1panel.yml` 添加 `condition: service_started`
2. 重启服务：
   ```bash
   docker-compose -f docker-compose.1panel.yml down
   docker-compose -f docker-compose.1panel.yml up -d
   ```

### 问题 4：Neo4j 密码已更改但配置未更新

**症状**：Neo4j 容器可以连接，但 Mem0 API 连接失败

**解决**：
1. 检查 Neo4j 的实际密码：
   ```bash
   docker exec mem0_neo4j cypher-shell -u neo4j -p mem0graph "RETURN 1"
   ```
2. 如果失败，访问 Neo4j 浏览器修改密码
3. 更新 `docker-compose.1panel.yml` 中的密码
4. 重启 mem0-api

## 快速修复命令

```bash
cd /data/build/CozyMem0/deployment/mem0

# 1. 检查配置
./scripts/check-mem0-neo4j-config.sh

# 2. 测试连接
./scripts/test-neo4j-from-api.sh

# 3. 如果配置正确但仍有问题，重启服务
docker-compose -f docker-compose.1panel.yml restart mem0-api

# 4. 检查日志
docker logs mem0-api --tail 50 | grep -i neo4j
```

## 验证修复

修复后验证：

```bash
# 1. 检查 mem0-api 是否正常启动
docker logs mem0-api --tail 20 | grep -i "error\|exception" || echo "✅ 无错误"

# 2. 测试添加记忆
curl -X POST "http://192.168.66.11:8888/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "测试记忆"}],
    "user_id": "test_user"
  }'
```

如果不再报 Neo4j 认证错误，说明问题已解决。

