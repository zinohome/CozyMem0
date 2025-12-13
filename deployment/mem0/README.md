# Mem0 部署指南

## 概述

本目录包含 Mem0 REST API 服务器的部署配置。Mem0 提供了官方的 `MemoryClient` 和 `AsyncMemoryClient` SDK，可以通过 REST API 与部署的服务进行交互。

## 部署方式

### 方式 1：1Panel 部署（推荐）

使用 `docker-compose.1panel.yml` 文件，适用于 1Panel 面板部署。

### 方式 2：本地开发部署

使用 `docker-compose.yml` 文件，适用于本地开发和测试。

## 快速开始

### 1. 构建 Docker 镜像

首先需要构建 Mem0 API 镜像：

```bash
# 使用构建脚本（推荐）
./build.sh

# 或指定标签
./build.sh v1.0.0

# 或手动构建
docker build -t mem0-api:latest -f Dockerfile ../..
```

### 2. 准备环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置：

```env
# LLM 配置（必需）
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. 启动服务

#### 1Panel 部署

```bash
docker-compose -f docker-compose.1panel.yml up -d
```

#### 本地开发部署

```bash
docker-compose up -d
```

### 4. 验证部署

访问 API 文档：
- Swagger UI: http://localhost:8888/docs
- ReDoc: http://localhost:8888/redoc

健康检查：
```bash
curl http://localhost:8888/health
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

### 版本信息

- **PostgreSQL + pgvector**: `pgvector/pgvector:0.8.1-pg17-trixie`（与 CozyCognee 和 CozyMemobase 统一）
- **Neo4j**: `neo4j:latest`（与 CozyCognee 统一）

## 1Panel 部署说明

### 数据存储位置

1Panel 部署时，所有数据存储在 `/data/mem0/` 目录：

- `/data/mem0/postgres` - PostgreSQL 数据
- `/data/mem0/neo4j/data` - Neo4j 数据
- `/data/mem0/neo4j/logs` - Neo4j 日志
- `/data/mem0/neo4j/import` - Neo4j 导入目录
- `/data/mem0/neo4j/plugins` - Neo4j 插件目录
- `/data/mem0/history` - 历史数据库
- `/data/mem0/logs` - Mem0 API 日志

### 网络配置

使用外部网络 `1panel-network`，与其他服务（Cognee、Memobase）在同一网络中，可以互相访问。

### 部署步骤

1. **构建镜像**：
```bash
cd deployment/mem0
./build.sh
```

2. **配置环境变量**：
```bash
# 在 1Panel 中配置环境变量，或创建 .env 文件
OPENAI_API_KEY=your-openai-api-key-here
```

3. **启动服务**：
```bash
docker-compose -f docker-compose.1panel.yml up -d
```

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

### 1Panel 部署

数据存储在 `/data/mem0/` 目录（主机路径）

### 本地开发部署

数据存储在 Docker volumes：

- `mem0_postgres_data` - PostgreSQL 数据
- `mem0_neo4j_data` - Neo4j 数据
- `mem0_neo4j_logs` - Neo4j 日志
- `mem0_neo4j_import` - Neo4j 导入目录
- `mem0_neo4j_plugins` - Neo4j 插件目录
- `mem0_history` - 历史数据库

## 故障排查

### 检查服务状态

```bash
# 1Panel 部署
docker-compose -f docker-compose.1panel.yml ps

# 本地开发部署
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
4. **镜像不存在**：确保已运行 `./build.sh` 构建镜像

## 参考

- [Mem0 官方文档](https://docs.mem0.ai)
- [Mem0 REST API 文档](https://docs.mem0.ai/open-source/features/rest-api)
- [Mem0 Python SDK](https://pypi.org/project/mem0ai/)
