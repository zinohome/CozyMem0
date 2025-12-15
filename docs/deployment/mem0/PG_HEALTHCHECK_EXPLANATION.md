# PostgreSQL 健康检查说明

## 当前配置

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U mem0 -d mem0"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

## pg_isready 与密码的关系

### ✅ **pg_isready 不需要密码**

`pg_isready` 是 PostgreSQL 官方工具，用于检查服务器是否准备好接受连接。它**不需要密码**，因为：

1. **只检查服务器状态**：它只检查 PostgreSQL 服务器是否在监听端口，不进行实际连接
2. **不验证认证**：它不尝试连接数据库，因此不需要密码
3. **轻量级**：执行非常快（< 100ms）

### ⚠️ **局限性**

`pg_isready` 的局限性：
- ❌ **不验证密码认证**：即使密码错误，只要服务器在监听，`pg_isready` 也会返回成功
- ❌ **不验证数据库可用性**：不检查数据库是否真正可以连接和查询

### ✅ **为什么仍然有效**

在 Docker 容器内，`pg_isready` 仍然有效，因为：

1. **容器内认证**：在 PostgreSQL 容器内，可以通过 `peer` 认证或本地连接，不需要密码
2. **启动顺序**：如果 `pg_isready` 成功，说明 PostgreSQL 已经初始化完成，密码认证通常也已经配置好
3. **性能优势**：非常快速，适合频繁的健康检查

## 更严格的健康检查选项

如果需要验证密码认证和数据库真正可用，可以使用以下方法：

### 选项 1：使用 psql（推荐用于严格检查）

```yaml
healthcheck:
  test: ["CMD-SHELL", "psql -U mem0 -d mem0 -c 'SELECT 1;'"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

**优点**：
- ✅ 验证实际连接（包括密码认证）
- ✅ 验证数据库是否真正可用
- ✅ 在容器内可以通过 peer 认证，不需要显式密码

**缺点**：
- ⚠️ 稍慢（需要 200-500ms）
- ⚠️ 如果密码认证配置有问题，可能失败

### 选项 2：使用环境变量密码（如果需要显式密码）

```yaml
healthcheck:
  test: ["CMD-SHELL", "PGPASSWORD=$POSTGRES_PASSWORD psql -U mem0 -d mem0 -c 'SELECT 1;'"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

**注意**：在容器内，通常不需要显式密码，因为可以通过 peer 认证。

### 选项 3：组合检查（最严格）

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U mem0 -d mem0 && psql -U mem0 -d mem0 -c 'SELECT 1;' > /dev/null 2>&1"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

## 当前配置的适用场景

### ✅ **当前配置（pg_isready）适合：**

1. **快速启动检查**：只需要检查服务器是否启动
2. **性能优先**：需要频繁检查，要求快速响应
3. **容器内环境**：在 PostgreSQL 容器内，peer 认证可用
4. **标准部署**：PostgreSQL 标准配置，密码认证通常正常

### ⚠️ **需要更严格检查的场景：**

1. **密码认证问题**：如果经常遇到密码认证失败
2. **数据库连接问题**：如果 `pg_isready` 通过但实际连接失败
3. **生产环境**：需要确保数据库真正可用

## 推荐配置

### 对于大多数场景（当前配置）

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U mem0 -d mem0"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

**理由**：
- ✅ 快速、高效
- ✅ 在容器内通常足够
- ✅ 与 CozyCognee 保持一致

### 如果需要更严格的检查

```yaml
healthcheck:
  test: ["CMD-SHELL", "psql -U mem0 -d mem0 -c 'SELECT 1;'"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

## 验证方法

### 测试当前配置

```bash
# 测试 pg_isready（不需要密码）
docker exec mem0_postgres pg_isready -U mem0 -d mem0

# 测试 psql（验证实际连接）
docker exec mem0_postgres psql -U mem0 -d mem0 -c "SELECT 1;"
```

### 运行测试脚本

```bash
cd /data/build/CozyMem0/deployment/mem0
./scripts/test-pg-healthcheck.sh
```

## 总结

### ✅ **当前配置是正确的**

- `pg_isready` 不需要密码，这是正常的
- 在容器内，它通常足够验证 PostgreSQL 是否就绪
- 与 CozyCognee 的配置保持一致

### 🔄 **如果需要更严格的检查**

可以改用 `psql` 进行实际连接测试，但：
- 会增加健康检查时间（200-500ms vs < 100ms）
- 在容器内通常不需要，因为 peer 认证可用

### 📝 **建议**

1. **保持当前配置**：如果启动顺序问题已解决（通过 `service_healthy`）
2. **如果仍有问题**：考虑改用 `psql` 进行更严格的检查
3. **监控**：观察健康检查是否正常工作

## 参考

- [PostgreSQL pg_isready 文档](https://www.postgresql.org/docs/current/app-pg-isready.html)
- [Docker Compose Healthcheck 文档](https://docs.docker.com/compose/compose-file/compose-file-v3/#healthcheck)
- [CozyCognee 健康检查配置](../CozyCognee/docs/deployment/HEALTHCHECK_SUMMARY.md)

