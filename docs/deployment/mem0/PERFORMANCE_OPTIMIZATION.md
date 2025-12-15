# Mem0 性能优化指南

## 问题总结

### 问题 1：Neo4j 认证失败

**错误信息**：
```
neo4j.exceptions.AuthError: {code: Neo.ClientError.Security.Unauthorized}
{message: The client is unauthorized due to authentication failure.}
```

**影响**：
- 每次添加记忆都会尝试连接 Neo4j
- 连接失败导致重试和超时
- **可能增加 5-30 秒延迟**

### 问题 2：添加记忆慢

**正常耗时**：350-1000ms
**当前耗时**：可能 5-30 秒（由于 Neo4j 连接失败）

## 性能瓶颈分析

### Mem0 添加记忆的完整流程

```
1. 解析消息（< 10ms）
   ↓
2. 【第一次 LLM 调用】提取事实（200-2000ms）⭐ 最慢
   - 调用 OpenAI API
   - 等待 LLM 响应
   - 解析 JSON
   ↓
3. 向量嵌入（50-200ms）
   - 调用嵌入模型
   ↓
4. 搜索现有记忆（50-200ms）
   - 向量搜索
   ↓
5. 【第二次 LLM 调用】更新记忆（200-2000ms）⭐ 也很慢
   - 调用 OpenAI API
   - 决定如何合并/更新记忆
   ↓
6. 存储到向量数据库（50-100ms）
   ↓
7. 存储到图数据库 Neo4j（50-200ms）
   - 如果连接失败：+5000-30000ms ⚠️ 主要问题
   ↓
8. 返回结果
```

**总耗时**：
- 正常情况：350-1000ms
- Neo4j 失败：5-30 秒

## 立即修复步骤

### 步骤 1：修复 Neo4j 认证（最重要）

```bash
cd /data/build/CozyMem0/deployment/mem0

# 运行诊断脚本
./scripts/diagnose-performance.sh

# 运行修复脚本
./scripts/fix-neo4j-auth.sh
```

或者手动修复：

```bash
# 1. 检查 Neo4j 容器
docker ps | grep neo4j

# 2. 测试连接
docker exec mem0_neo4j cypher-shell -u neo4j -p mem0graph "RETURN 1"

# 3. 如果连接失败，访问 Neo4j 浏览器
# http://192.168.66.11:8474
# 使用默认密码 neo4j/neo4j 登录
# 修改密码为 mem0graph

# 4. 重启 mem0-api
docker-compose -f docker-compose.1panel.yml restart mem0-api
```

### 步骤 2：验证修复效果

```bash
# 测试添加记忆的速度
time curl -X POST "http://192.168.66.11:8888/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "测试记忆"}],
    "user_id": "test_user"
  }'
```

## 性能优化方案

### 方案 1：使用更快的 LLM 模型

在 `docker-compose.1panel.yml` 中：

```yaml
environment:
  # 使用更快的模型（推荐）
  OPENAI_MODEL: gpt-3.5-turbo  # 比 gpt-4 快 3-5 倍，成本更低
  
  # 或使用 gpt-4-turbo（平衡速度和性能）
  # OPENAI_MODEL: gpt-4-turbo
```

**性能对比**：
- `gpt-4.1-nano-2025-04-14`：200-500ms（但可能不支持中文）
- `gpt-3.5-turbo`：100-300ms（快，支持中文）
- `gpt-4`：300-800ms（慢，但性能好）
- `gpt-4-turbo`：200-500ms（平衡）

### 方案 2：优化数据库连接

确保数据库连接池配置合理：

```yaml
# PostgreSQL 连接池（在应用层配置）
# Neo4j 连接池（在应用层配置）
```

### 方案 3：批量处理（如果支持）

如果可能，批量添加多个记忆，减少 API 调用次数。

### 方案 4：异步处理（前端优化）

前端可以：
- 显示"处理中"状态
- 异步等待结果
- 使用 WebSocket 或轮询获取结果

## 性能基准

### 正常情况下的预期时间

| 步骤 | 时间 | 说明 |
|------|------|------|
| 第一次 LLM 调用 | 200-500ms | 提取事实 |
| 向量嵌入 | 50-200ms | 文本嵌入 |
| 搜索现有记忆 | 50-200ms | 向量搜索 |
| 第二次 LLM 调用 | 200-500ms | 更新记忆 |
| 向量数据库写入 | 50-100ms | pgvector |
| 图数据库写入 | 50-200ms | Neo4j |
| **总计** | **600-1700ms** | 正常情况 |

### Neo4j 连接失败时的额外时间

| 情况 | 额外时间 | 说明 |
|------|---------|------|
| 连接重试 | +2-5秒 | 每次重试 |
| 超时等待 | +5-30秒 | 取决于超时设置 |
| **总计** | **+7-35秒** | 严重影响 |

## 诊断工具

### 1. 性能诊断脚本

```bash
cd /data/build/CozyMem0/deployment/mem0
./scripts/diagnose-performance.sh
```

### 2. 检查容器状态

```bash
# 检查所有容器
docker ps

# 检查资源使用
docker stats mem0-api mem0_postgres mem0_neo4j

# 检查日志
docker logs mem0-api --tail 50
docker logs mem0_neo4j --tail 50
```

### 3. 测试 API 性能

```bash
# 测试添加记忆
time curl -X POST "http://192.168.66.11:8888/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "测试"}],
    "user_id": "test"
  }'
```

## 常见问题

### Q: 为什么需要两次 LLM 调用？

A: Mem0 的设计：
1. 第一次：从对话中提取事实
2. 第二次：决定如何与现有记忆合并/更新

这是 Mem0 的核心设计，无法避免。

### Q: 可以禁用 Neo4j 吗？

A: 可以，但会失去图数据库功能（实体关系、知识图谱等）。如果不需要这些功能，可以：

```python
# 在配置中移除 graph_store
"graph_store": None,
```

### Q: 如何进一步优化？

A: 
1. ✅ 修复 Neo4j 认证（最重要）
2. 使用更快的 LLM 模型
3. 优化网络延迟
4. 考虑使用本地模型（如果可用）

## 参考

- [Neo4j 认证问题](./NEO4J_AUTH_ISSUE.md)
- [添加记忆性能分析](./MEMORY_ADD_PERFORMANCE.md)
- [诊断脚本](../scripts/diagnose-performance.sh)
- [Neo4j 修复脚本](../scripts/fix-neo4j-auth.sh)

