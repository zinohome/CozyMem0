# Neo4j 认证失败问题分析

## 错误信息

```
neo4j.exceptions.AuthError: {code: Neo.ClientError.Security.Unauthorized} 
{message: The client is unauthorized due to authentication failure.}
```

## 原因分析

### 1. Neo4j 密码不匹配

可能的原因：
1. **Neo4j 首次启动需要修改密码**：Neo4j 首次启动时，默认密码是 `neo4j/neo4j`，需要修改
2. **密码已更改但配置未更新**：Neo4j 容器中的密码可能已被修改
3. **环境变量未正确传递**：容器间环境变量可能未正确传递

### 2. 配置检查

当前配置：
- **docker-compose.1panel.yml**：`NEO4J_AUTH: neo4j/mem0graph`
- **main.py 默认值**：`NEO4J_USERNAME: neo4j`, `NEO4J_PASSWORD: mem0graph`

## 解决方案

### 方案 1：重置 Neo4j 密码（推荐）

如果 Neo4j 是首次启动或密码不匹配：

```bash
# 1. 停止 Neo4j 容器
docker stop mem0_neo4j

# 2. 删除 Neo4j 数据（注意：这会删除所有数据）
rm -rf /data/mem0/neo4j/data/*

# 3. 重新启动 Neo4j
docker-compose -f docker-compose.1panel.yml up -d neo4j

# 4. 等待 Neo4j 启动（约 30 秒）
sleep 30

# 5. 通过浏览器访问 Neo4j 并修改密码
# 访问：http://192.168.66.11:8474
# 默认用户名：neo4j
# 默认密码：neo4j
# 修改为新密码：mem0graph
```

### 方案 2：检查并更新配置

1. **检查 Neo4j 容器日志**：
```bash
docker logs mem0_neo4j | grep -i auth
```

2. **验证 Neo4j 连接**：
```bash
docker exec -it mem0_neo4j cypher-shell -u neo4j -p mem0graph
```

如果连接失败，说明密码不正确。

3. **更新 docker-compose 配置**：
确保 `NEO4J_AUTH` 格式正确：
```yaml
NEO4J_AUTH: neo4j/mem0graph  # 格式：用户名/密码
```

### 方案 3：临时禁用 Neo4j（如果不需要图数据库）

如果暂时不需要图数据库功能，可以修改配置不使用 Neo4j：

```python
# 在 main.py 中，将 graph_store 设置为 None
"graph_store": None,  # 或删除 graph_store 配置
```

但 Mem0 的某些功能可能需要图数据库。

## 验证步骤

1. **检查 Neo4j 容器状态**：
```bash
docker ps | grep neo4j
```

2. **检查 Neo4j 日志**：
```bash
docker logs mem0_neo4j --tail 50
```

3. **测试连接**：
```bash
docker exec mem0_neo4j cypher-shell -u neo4j -p mem0graph "RETURN 1"
```

4. **检查 Mem0 API 日志**：
```bash
docker logs mem0-api --tail 50 | grep -i neo4j
```

## 常见问题

### Q: Neo4j 首次启动密码是什么？

A: Neo4j 首次启动时，默认用户名和密码都是 `neo4j`。首次登录后必须修改密码。

### Q: 如何重置 Neo4j 密码？

A: 
1. 删除数据目录：`rm -rf /data/mem0/neo4j/data/*`
2. 重启容器
3. 通过浏览器访问并修改密码

### Q: 密码格式是什么？

A: `NEO4J_AUTH` 环境变量的格式是 `用户名/密码`，例如：`neo4j/mem0graph`

## 相关配置

确保以下配置一致：
- `docker-compose.1panel.yml` 中的 `NEO4J_AUTH`
- `main.py` 中的 `NEO4J_USERNAME` 和 `NEO4J_PASSWORD`
- Neo4j 容器中的实际密码

