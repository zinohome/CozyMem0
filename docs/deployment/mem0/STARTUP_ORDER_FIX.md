# 启动顺序问题修复

## 问题描述

每次重启 API 容器后都会报 PostgreSQL/Neo4j 认证失败错误，但重建数据库后能连上。

**根本原因**：启动顺序问题
- API 容器在数据库完全初始化前就尝试连接
- `condition: service_started` 只确保容器启动，不确保数据库就绪
- 数据库初始化需要时间（PostgreSQL: 10-30秒，Neo4j: 30-60秒）

## 解决方案

### 已添加健康检查（Healthcheck）

为 PostgreSQL 和 Neo4j 添加了健康检查，确保数据库完全就绪：

#### PostgreSQL 健康检查

```yaml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U mem0 -d mem0"]
    interval: 10s      # 每 10 秒检查一次
    timeout: 5s       # 超时 5 秒
    retries: 5        # 重试 5 次
    start_period: 30s # 启动后 30 秒内不标记为失败
```

#### Neo4j 健康检查

```yaml
neo4j:
  healthcheck:
    test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "mem0graph", "RETURN 1"]
    interval: 30s      # 每 30 秒检查一次
    timeout: 10s       # 超时 10 秒
    retries: 3         # 重试 3 次
    start_period: 60s  # 启动后 60 秒内不标记为失败
```

### 已更新 depends_on 配置

从 `service_started` 改为 `service_healthy`：

```yaml
mem0-api:
  depends_on:
    postgres:
      condition: service_healthy  # 等待健康检查通过
    neo4j:
      condition: service_healthy   # 等待健康检查通过
```

## 工作原理

### 之前的问题

```
1. PostgreSQL 容器启动（service_started）
   ↓
2. API 容器立即启动（认为 PostgreSQL 已就绪）
   ↓
3. API 尝试连接 PostgreSQL（但数据库还在初始化）
   ↓
4. ❌ 连接失败：密码认证失败
```

### 修复后的流程

```
1. PostgreSQL 容器启动
   ↓
2. PostgreSQL 开始初始化（10-30秒）
   ↓
3. 健康检查开始运行（start_period: 30s）
   ↓
4. pg_isready 检查通过（数据库就绪）
   ↓
5. PostgreSQL 标记为 healthy
   ↓
6. API 容器启动（等待 healthy 状态）
   ↓
7. ✅ 连接成功
```

## 使用方法

### 正常启动（推荐）

现在可以直接启动，无需手动等待：

```bash
cd /data/build/CozyMem0/deployment/mem0

# 启动所有服务（会自动等待数据库就绪）
docker-compose -f docker-compose.1panel.yml up -d

# 或只启动 API（会自动等待数据库健康检查通过）
docker-compose -f docker-compose.1panel.yml up -d mem0-api
```

### 重启 API

重启 API 时，也会等待数据库健康检查：

```bash
docker-compose -f docker-compose.1panel.yml restart mem0-api
```

## 验证

### 检查健康检查状态

```bash
# 查看所有容器状态（包括健康检查）
docker ps --format "table {{.Names}}\t{{.Status}}"

# 应该看到：
# mem0_postgres    Up X seconds (healthy)
# mem0_neo4j       Up X seconds (healthy)
# mem0-api         Up X seconds
```

### 检查健康检查详情

```bash
# PostgreSQL
docker inspect mem0_postgres | grep -A 10 Healthcheck

# Neo4j
docker inspect mem0_neo4j | grep -A 10 Healthcheck
```

### 测试连接

```bash
# 检查 API 日志（应该没有认证错误）
docker logs mem0-api --tail 20 | grep -i "error\|postgres\|neo4j" || echo "✅ 无错误"

# 测试 API
curl http://192.168.66.11:8888/docs
```

## 健康检查配置说明

### PostgreSQL 健康检查

- **命令**：`pg_isready -U mem0 -d mem0`
  - `pg_isready` 是 PostgreSQL 官方工具
  - 检查数据库是否接受连接
  - 非常快速（< 100ms）

- **参数**：
  - `interval: 10s` - 每 10 秒检查一次（数据库启动快）
  - `timeout: 5s` - 超时 5 秒
  - `retries: 5` - 重试 5 次（最多等待 50 秒）
  - `start_period: 30s` - 启动后 30 秒内不标记为失败

### Neo4j 健康检查

- **命令**：`cypher-shell -u neo4j -p mem0graph RETURN 1`
  - 执行简单查询验证数据库可用
  - 需要 2-5 秒

- **参数**：
  - `interval: 30s` - 每 30 秒检查一次（Neo4j 是重量级服务）
  - `timeout: 10s` - 超时 10 秒
  - `retries: 3` - 重试 3 次（最多等待 90 秒）
  - `start_period: 60s` - 启动后 60 秒内不标记为失败（Neo4j 启动较慢）

## 故障排查

### 问题 1：健康检查一直失败

**检查方法**：
```bash
# 手动测试健康检查命令
docker exec mem0_postgres pg_isready -U mem0 -d mem0
docker exec mem0_neo4j cypher-shell -u neo4j -p mem0graph "RETURN 1"
```

**可能原因**：
- 数据库配置错误
- 数据库启动失败
- 密码不正确

### 问题 2：API 仍然在数据库就绪前启动

**检查方法**：
```bash
# 检查 depends_on 配置
grep -A 5 "depends_on" docker-compose.1panel.yml

# 应该看到 condition: service_healthy
```

**解决方法**：
- 确保使用 `condition: service_healthy`
- 确保健康检查配置正确

### 问题 3：启动时间过长

**原因**：
- Neo4j 启动较慢（可能需要 60-90 秒）
- 这是正常的，健康检查会等待

**优化**：
- 如果不需要 Neo4j，可以暂时禁用
- 或增加 `start_period` 时间

## 性能影响

### 健康检查开销

- **PostgreSQL**：`pg_isready` 非常快（< 100ms），几乎无影响
- **Neo4j**：`cypher-shell` 需要 2-5 秒，但只在启动时检查

### 启动时间

- **之前**：API 立即启动，但可能连接失败
- **现在**：API 等待数据库就绪（额外 10-60 秒），但确保连接成功

**权衡**：启动时间稍长，但可靠性大大提高。

## 总结

### ✅ **已修复**

1. ✅ 添加了 PostgreSQL 健康检查
2. ✅ 添加了 Neo4j 健康检查
3. ✅ 更新了 `depends_on` 使用 `service_healthy`
4. ✅ 确保 API 在数据库完全就绪后才启动

### 📝 **使用建议**

1. **正常启动**：直接使用 `docker-compose up -d`，会自动等待
2. **重启 API**：使用 `docker-compose restart mem0-api`，也会等待数据库
3. **检查状态**：使用 `docker ps` 查看健康检查状态

### 🔍 **验证**

```bash
# 1. 检查健康检查状态
docker ps --format "table {{.Names}}\t{{.Status}}"

# 2. 检查 API 日志
docker logs mem0-api --tail 20

# 3. 测试 API
curl http://192.168.66.11:8888/docs
```

现在重启 API 容器时，会自动等待数据库完全就绪，不会再出现认证失败的错误！

## 参考

- [Docker Compose Healthcheck 文档](https://docs.docker.com/compose/compose-file/compose-file-v3/#healthcheck)
- [PostgreSQL pg_isready 文档](https://www.postgresql.org/docs/current/app-pg-isready.html)
- [Neo4j cypher-shell 文档](https://neo4j.com/docs/operations-manual/current/tools/cypher-shell/)

