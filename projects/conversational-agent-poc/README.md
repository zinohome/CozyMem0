# 对话智能体 POC

智能对话系统 POC，整合 Cognee、Memobase、Mem0 三个记忆/知识管理系统。

## 功能特性

- ✅ **智能对话**：基于 OpenAI API 的对话能力
- ✅ **知识检索**：从 Cognee 知识库中检索专业知识
- ✅ **用户画像**：从对话中提取并更新用户画像
- ✅ **会话记忆**：跨会话的记忆管理
- ✅ **性能优化**：并发获取上下文，异步保存记忆

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置。

### 3. 启动服务

```bash
# 开发模式
python -m src.main

# 或使用 uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## API 使用示例

### 1. 发送消息

```bash
curl -X POST "http://localhost:8080/api/v1/conversations/session_123/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，我想了解一下Python编程",
    "user_id": "user_123",
    "session_id": "session_123",
    "dataset_names": ["kb_tech"]
  }'
```

### 2. 测试对话（返回完整上下文）

```bash
curl -X POST "http://localhost:8080/api/v1/test/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "session_id": "session_123",
    "message": "你好，我想了解一下Python编程",
    "dataset_names": ["kb_tech"]
  }'
```

### 3. 获取用户画像

```bash
curl "http://localhost:8080/api/v1/users/user_123/profile"
```

## 项目结构

```
conversational-agent-poc/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── clients/                # SDK 客户端封装
│   │   ├── __init__.py
│   │   ├── cognee_client.py
│   │   ├── memobase_client.py
│   │   └── mem0_client.py
│   ├── services/               # 业务服务
│   │   ├── __init__.py
│   │   ├── conversation_engine.py
│   │   ├── knowledge_service.py
│   │   ├── profile_service.py
│   │   └── memory_service.py
│   └── prompts/                # Prompt 模板
│       └── templates.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## 架构说明

### 数据流

1. **并发获取上下文**（步骤 1-3）
   - 用户画像（Memobase）
   - 会话记忆（Mem0）
   - 专业知识（Cognee）

2. **构建 Prompt 并调用 OpenAI**（步骤 4-5）

3. **立即返回响应**

4. **异步保存**（步骤 6-7）
   - 会话记忆（Mem0）
   - 用户画像（Memobase）

## 开发

### 运行测试

```bash
pytest tests/
```

### 代码结构说明

- **clients/**: SDK 客户端封装，简洁清晰
- **services/**: 业务服务层，职责分明
- **prompts/**: Prompt 模板管理
- **main.py**: API 路由和生命周期管理

## 部署

参考 `deployment/` 目录下的 Docker 配置。

## 参考文档

详细设计文档请查看：`docs/poc/conversational-agent-poc-design.md`

