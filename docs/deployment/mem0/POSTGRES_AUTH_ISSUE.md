# PostgreSQL 认证失败问题排查

## 问题现象

每次重启 API 容器后，都会报 PostgreSQL 密码认证失败错误：

```
psycopg2.OperationalError: connection to server at "postgres" (172.19.0.7), port 5432 failed: 
FATAL: password authentication failed for user "mem0"
```

## 可能原因

### 1. PostgreSQL 数据目录被重置（最常见）

**原因**：
- PostgreSQL 容器重启时，如果数据目录不存在或为空，会重新初始化
- 重新初始化时会使用**新的随机密码**或**默认密码**
- 但 API 容器仍使用旧的密码配置

**检查方法**：
```bash
# 检查数据目录
ls -la /data/mem0/postgres/

# 如果目录为空或只有很少文件，说明被重置了
```

### 2. 环境变量配置不一致

**原因**：
- `docker-compose.1panel.yml` 中的密码配置
- 容器实际使用的密码
- API 容器读取的密码

三者不一致。

**检查方法**：
```bash
cd /data/build/CozyMem0/deployment/mem0
./scripts/check-postgres-connection.sh
```

### 3. PostgreSQL 容器启动顺序问题

**原因**：
- API 容器在 PostgreSQL 完全初始化前就尝试连接
- PostgreSQL 初始化需要时间（特别是首次启动）

**检查方法**：
```bash
# 检查启动顺序配置
grep -A 5 "depends_on" docker-compose.1panel.yml
```

### 4. 密码被意外修改

**原因**：
- 手动修改了 PostgreSQL 密码
- 但 API 配置未更新

## 解决方案

### 方案 1：重置 PostgreSQL 数据（推荐）

如果数据可以丢失，重置是最简单的方法：

```bash
cd /data/build/CozyMem0/deployment/mem0

# 1. 停止服务
docker-compose -f docker-compose.1panel.yml stop postgres mem0-api

# 2. 删除 PostgreSQL 容器
docker-compose -f docker-compose.1panel.yml rm -f postgres

# 3. 删除数据目录（⚠️ 会删除所有数据）
rm -rf /data/mem0/postgres/*

# 4. 重新启动 PostgreSQL
docker-compose -f docker-compose.1panel.yml up -d postgres

# 5. 等待 PostgreSQL 完全启动（约 10-30 秒）
sleep 15

# 6. 检查 PostgreSQL 日志
docker logs mem0_postgres --tail 20

# 7. 验证连接
docker exec mem0_postgres psql -U mem0 -d mem0 -c "SELECT 1;"

# 8. 启动 API
docker-compose -f docker-compose.1panel.yml up -d mem0-api
```

### 方案 2：修复密码不匹配

如果数据不能丢失，需要修复密码：

#### 步骤 1：检查实际密码

```bash
# 检查 PostgreSQL 容器的环境变量
docker exec mem0_postgres env | grep POSTGRES

# 检查 API 容器的环境变量
docker exec mem0-api env | grep POSTGRES
```

#### 步骤 2：修改 PostgreSQL 密码

**方法 A：通过 psql 修改**

```bash
# 如果知道当前密码，可以修改
docker exec -it mem0_postgres psql -U mem0 -d mem0
# 在 psql 中执行：
# ALTER USER mem0 WITH PASSWORD 'mem0password';
```

**方法 B：重置容器（会丢失数据）**

```bash
# 停止并删除容器
docker-compose -f docker-compose.1panel.yml stop postgres
docker-compose -f docker-compose.1panel.yml rm -f postgres
rm -rf /data/mem0/postgres/*

# 重新启动（会使用 docker-compose 中的配置）
docker-compose -f docker-compose.1panel.yml up -d postgres
```

#### 步骤 3：确保配置一致

检查 `docker-compose.1panel.yml`：

```yaml
postgres:
  environment:
    POSTGRES_USER: mem0
    POSTGRES_PASSWORD: mem0password  # 确保这个值正确
    POSTGRES_DB: mem0

mem0-api:
  environment:
    POSTGRES_USER: mem0
    POSTGRES_PASSWORD: mem0password  # 必须与 postgres 一致
    POSTGRES_DB: mem0
```

### 方案 3：添加启动等待机制

确保 PostgreSQL 完全启动后再启动 API：

```yaml
mem0-api:
  depends_on:
    postgres:
      condition: service_healthy  # 需要添加健康检查
```

或使用脚本等待：

```bash
# 等待 PostgreSQL 就绪
until docker exec mem0_postgres pg_isready -U mem0 > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# 然后启动 API
docker-compose -f docker-compose.1panel.yml up -d mem0-api
```

## 诊断步骤

### 1. 运行诊断脚本

```bash
cd /data/build/CozyMem0/deployment/mem0
./scripts/check-postgres-connection.sh
```

### 2. 检查配置一致性

```bash
# 检查 docker-compose 配置
grep -A 10 "postgres:" docker-compose.1panel.yml | grep POSTGRES

# 检查容器实际配置
docker exec mem0_postgres env | grep POSTGRES
docker exec mem0-api env | grep POSTGRES
```

### 3. 测试连接

```bash
# 从 API 容器测试连接
docker exec mem0-api python3 -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'postgres'),
        port=int(os.environ.get('POSTGRES_PORT', 5432)),
        dbname=os.environ.get('POSTGRES_DB', 'mem0'),
        user=os.environ.get('POSTGRES_USER', 'mem0'),
        password=os.environ.get('POSTGRES_PASSWORD', 'mem0password')
    )
    print('✅ 连接成功')
    conn.close()
except Exception as e:
    print('❌ 连接失败:', e)
"
```

## 预防措施

### 1. 确保启动顺序

在 `docker-compose.1panel.yml` 中：

```yaml
mem0-api:
  depends_on:
    postgres:
      condition: service_started
```

### 2. 使用健康检查（可选）

```yaml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U mem0"]
    interval: 5s
    timeout: 5s
    retries: 5

mem0-api:
  depends_on:
    postgres:
      condition: service_healthy
```

### 3. 数据持久化

确保数据目录正确挂载：

```yaml
postgres:
  volumes:
    - /data/mem0/postgres:/var/lib/postgresql/data
```

### 4. 统一密码配置

使用环境变量文件或统一配置：

```yaml
# 使用变量
postgres:
  environment:
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-mem0password}

mem0-api:
  environment:
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-mem0password}
```

## 常见问题

### Q: 为什么之前能连上，重启后就失败了？

A: 可能的原因：
1. PostgreSQL 数据目录被清空或重置
2. 容器使用了不同的配置启动
3. 环境变量未正确传递

### Q: 如何避免数据丢失？

A: 
1. 确保数据目录正确挂载
2. 不要删除 `/data/mem0/postgres/` 目录
3. 备份重要数据

### Q: 如何验证修复是否成功？

A: 
```bash
# 1. 检查 API 日志
docker logs mem0-api --tail 20 | grep -i "error\|postgres" || echo "✅ 无错误"

# 2. 测试 API
curl http://192.168.66.11:8888/docs

# 3. 测试创建记忆
curl -X POST "http://192.168.66.11:8888/memories" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "测试"}], "user_id": "test"}'
```

## 快速修复命令

```bash
cd /data/build/CozyMem0/deployment/mem0

# 1. 诊断问题
./scripts/check-postgres-connection.sh

# 2. 如果数据可以丢失，重置
docker-compose -f docker-compose.1panel.yml stop postgres mem0-api
docker-compose -f docker-compose.1panel.yml rm -f postgres
rm -rf /data/mem0/postgres/*
docker-compose -f docker-compose.1panel.yml up -d postgres
sleep 15
docker-compose -f docker-compose.1panel.yml up -d mem0-api

# 3. 验证
docker logs mem0-api --tail 20
```

## 参考

- [PostgreSQL Docker 官方文档](https://hub.docker.com/_/postgres)
- [docker-compose.1panel.yml](../docker-compose.1panel.yml)
- [诊断脚本](../scripts/check-postgres-connection.sh)

