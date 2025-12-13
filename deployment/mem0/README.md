# Mem0 部署指南

## 概述

本目录包含 Mem0 REST API 服务器的部署配置。Mem0 提供了官方的 `MemoryClient` 和 `AsyncMemoryClient` SDK，可以通过 REST API 与部署的服务进行交互。

## 快速开始

### 1. 准备环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置：

```env
# LLM 配置（必需）
OPENAI_API_KEY=your-openai-api-key-here

# 数据库配置（可选，docker-compose 中已配置默认值）
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=mem0
POSTGRES_USER=mem0
POSTGRES_PASSWORD=mem0password

# Neo4j 配置（可选，docker-compose 中已配置默认值）
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=mem0graph
```

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 验证部署

访问 API 文档：
- Swagger UI: http://localhost:8888/docs
- ReDoc: http://localhost:8888/redoc

健康检查：
```bash
curl http://localhost:8888/health
```

## 使用 SDK

### Python SDK

```python
from mem0 import MemoryClient, AsyncMemoryClient

# 同步客户端
client = MemoryClient(
    api_key="your-api-key",  # 如果启用了认证
    host="http://localhost:8888"
)

# 添加记忆
result = client.add(
    messages=[
        {"role": "user", "content": "我喜欢喝咖啡"},
        {"role": "assistant", "content": "好的，我记住了"}
    ],
    user_id="user_123"
)

# 搜索记忆
results = client.search(
    query="用户喜欢什么？",
    user_id="user_123"
)

# 异步客户端
import asyncio
from mem0 import AsyncMemoryClient

async def main():
    client = AsyncMemoryClient(
        api_key="your-api-key",
        host="http://localhost:8888"
    )
    
    try:
        result = await client.add(
            messages=[...],
            user_id="user_123"
        )
        results = await client.search(
            query="用户喜欢什么？",
            user_id="user_123"
        )
    finally:
        await client.close()

asyncio.run(main())
```

### 安装 SDK

```bash
pip install mem0ai
```

## 服务架构

```
┌─────────────────┐
│   Mem0 API      │  :8888
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Postgres│ │ Neo4j │
│(pgvector)│ │(Graph)│
└────────┘ └───────┘
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥（必需） | - |
| `POSTGRES_HOST` | PostgreSQL 主机 | `postgres` |
| `POSTGRES_PORT` | PostgreSQL 端口 | `5432` |
| `POSTGRES_DB` | 数据库名 | `mem0` |
| `POSTGRES_USER` | 数据库用户 | `mem0` |
| `POSTGRES_PASSWORD` | 数据库密码 | `mem0password` |
| `NEO4J_URI` | Neo4j 连接 URI | `bolt://neo4j:7687` |
| `NEO4J_USERNAME` | Neo4j 用户名 | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j 密码 | `mem0graph` |
| `HISTORY_DB_PATH` | 历史数据库路径 | `/app/history/history.db` |

### 端口映射

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|---------|---------|------|
| Mem0 API | 8000 | 8888 | REST API 服务 |
| PostgreSQL | 5432 | 8432 | 数据库服务 |
| Neo4j HTTP | 7474 | 8474 | Neo4j 浏览器 |
| Neo4j Bolt | 7687 | 8687 | Neo4j 连接 |

## API 端点

主要 API 端点：

- `POST /memories` - 创建记忆
- `GET /memories/{memory_id}` - 获取记忆
- `POST /memories/search` - 搜索记忆
- `PUT /memories/{memory_id}` - 更新记忆
- `DELETE /memories/{memory_id}` - 删除记忆
- `POST /configure` - 配置 Mem0

详细 API 文档请访问：http://localhost:8888/docs

## 数据持久化

数据存储在 Docker volumes：

- `mem0_postgres_data` - PostgreSQL 数据
- `mem0_neo4j_data` - Neo4j 数据
- `mem0_history` - 历史数据库

## 故障排查

### 检查服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 所有服务日志
docker-compose logs

# 特定服务日志
docker-compose logs mem0-api
docker-compose logs postgres
docker-compose logs neo4j
```

### 常见问题

1. **连接失败**：检查端口是否被占用
2. **数据库连接错误**：检查环境变量配置
3. **LLM API 错误**：检查 `OPENAI_API_KEY` 是否正确

## 参考

- [Mem0 官方文档](https://docs.mem0.ai)
- [Mem0 REST API 文档](https://docs.mem0.ai/open-source/features/rest-api)
- [Mem0 Python SDK](https://pypi.org/project/mem0ai/)

