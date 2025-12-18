# 快速开始指南

## 🎯 概述

Conversational Agent POC 是一个智能对话系统原型，整合了三种记忆系统：
- **Cognee**: 知识检索（长期专业知识）
- **Memobase**: 用户画像（用户信息和偏好）
- **Mem0**: 会话记忆（对话历史和上下文）

## ✅ 前置条件

### 1. 环境要求

- Python 3.10+
- 必需的服务（需要运行）：
  - Cognee 服务（默认: http://192.168.66.11:8000）
  - Memobase 服务（默认: http://192.168.66.11:8019）
  - Mem0 服务（默认: http://192.168.66.11:8888）
- OpenAI API Key 或兼容的 LLM API

### 2. 安装依赖

```bash
cd /Users/zhangjun/CursorProjects/CozyMem0/projects/conversational-agent-poc
pip3 install -r requirements.txt
```

## 🚀 启动服务

### 方法一：使用启动脚本（推荐）

```bash
# 设置 OpenAI API Key
export OPENAI_API_KEY='your-api-key-here'

# 或设置自定义 OpenAI 兼容 API
export OPENAI_API_KEY='your-api-key'
export OPENAI_BASE_URL='http://your-llm-api-url'
export OPENAI_MODEL='gpt-4'

# 启动服务
./start_poc.sh
```

### 方法二：手动启动

```bash
# 设置环境变量
export COGNEE_API_URL="http://192.168.66.11:8000"
export MEMOBASE_PROJECT_URL="http://192.168.66.11:8019"
export MEMOBASE_API_KEY="secret"
export MEM0_API_URL="http://192.168.66.11:8888"
export OPENAI_API_KEY="your-api-key-here"

# 启动服务
python3 -m src.main
```

### 方法三：使用 uvicorn

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

## 🧪 测试服务

### 1. 验证语法修复

```bash
python3 test_syntax.py
```

预期输出：
```
✅ 所有模块导入成功！语法错误已修复
```

### 2. 验证改进功能

```bash
python3 test_improvements.py
```

预期输出：
```
✅ 所有测试通过！
```

### 3. 健康检查

```bash
curl http://localhost:8080/health
```

预期输出：
```json
{"status": "healthy"}
```

### 4. 查看服务状态

```bash
curl http://localhost:8080/api/v1/debug/status
```

## 💬 测试对话

### 使用快速测试脚本

```bash
python3 quick_test.py
```

这将运行一系列测试对话，包括：
1. 首次对话（介绍自己）
2. 记忆测试（询问之前说过的内容）
3. 获取用户画像

### 使用 curl 命令

#### 1. 测试对话（首次对话）

```bash
curl -X POST "http://localhost:8080/api/v1/test/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "session_id": "test_session_001",
    "message": "你好，我是张三，我是一名软件工程师，对Python编程很感兴趣",
    "dataset_names": []
  }'
```

**预期响应**（首次对话，无历史数据）：
```json
{
  "success": true,
  "user_id": "test_user_001",
  "session_id": "test_session_001",
  "message": "你好，我是张三...",
  "response": "你好张三！很高兴认识你...",
  "context": {
    "user_profile": {},
    "user_profile_status": "暂无（首次对话或新用户）",
    "session_memories_count": 0,
    "session_memories_status": "暂无（首次对话或新会话）",
    "knowledge_count": 0,
    "knowledge_status": "暂无（未指定知识库或知识库为空）",
    "session_memories": [],
    "knowledge": []
  }
}
```

#### 2. 测试记忆（第二次对话）

等待 5-10 秒后：

```bash
curl -X POST "http://localhost:8080/api/v1/test/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "session_id": "test_session_001",
    "message": "我之前说过我的职业是什么？",
    "dataset_names": []
  }'
```

**预期响应**（有记忆数据）：
```json
{
  "success": true,
  "response": "你之前说过你是一名软件工程师...",
  "context": {
    "user_profile": {
      "name": "张三",
      "occupation": "软件工程师",
      "interests": ["Python编程"]
    },
    "user_profile_status": "已加载",
    "session_memories_count": 2,
    "session_memories_status": "已加载 2 条记忆",
    "session_memories": [
      {
        "content": "用户名字是张三",
        "type": "semantic",
        "session": "current"
      },
      {
        "content": "用户职业是软件工程师",
        "type": "semantic",
        "session": "current"
      }
    ]
  }
}
```

#### 3. 获取用户画像

```bash
curl "http://localhost:8080/api/v1/users/test_user_001/profile"
```

## 📊 诊断工具

运行完整的诊断测试：

```bash
python3 diagnose.py
```

这将检查：
- POC 服务状态
- 各个服务的连接状态
- 测试对话功能
- 显示详细的调试信息

## 🎯 关键改进

### 1. 空数据友好

即使是首次对话或没有数据，系统也会返回有意义的状态信息：

**Prompt 中的状态显示**：
```
# 用户画像
- 暂无用户画像信息（首次对话或新用户）

# 对话记忆
- 暂无历史对话记忆（首次对话或新会话）

# 专业知识
- 暂无相关专业知识（未指定知识库或知识库为空）
```

**API 响应中的状态描述**：
```json
{
  "user_profile_status": "暂无（首次对话或新用户）",
  "session_memories_status": "暂无（首次对话或新会话）",
  "knowledge_status": "暂无（未指定知识库或知识库为空）"
}
```

### 2. 详细的数据展示

当有数据时，会以格式化的方式展示：

**用户画像**：
```
# 用户画像
- name: 张三
- occupation: 软件工程师
- interests: ['Python编程']
```

**对话记忆**：
```
# 对话记忆
- [current/semantic] 用户喜欢Python编程
- [cross/semantic] 用户正在学习AI
```

**专业知识**：
```
# 专业知识
- [kb_tech] (相关度: 0.95) Python是一种高级编程语言
```

## ❓ 常见问题

### 1. 服务无法启动

**错误**: `SyntaxError: expected 'except' or 'finally' block`

**解决**: 已修复！运行 `python3 test_syntax.py` 验证。

### 2. 三种记忆都返回空

**原因**: 首次对话或新用户

**解决**: 这是正常情况！系统会显示友好的状态信息：
- "暂无（首次对话或新用户）"
- 继续对话，系统会自动保存并在下次对话时使用

### 3. Cognee 知识检索失败

**错误**: `DatasetNotFoundError`

**解决**: 
- 使用空数组 `"dataset_names": []`
- 或先在 Cognee 中创建数据集

### 4. Memobase 返回 422 错误

**原因**: 用户不存在

**解决**: 代码已改进，会自动创建用户！

### 5. Mem0 记忆保存失败

**检查**: 
1. Mem0 服务是否正常运行
2. 查看 Mem0 的日志
3. 可能需要等待 5-10 秒让记忆处理完成

## 📚 相关文档

- [改进报告](../../docs/poc/conversational-agent-improvements-20241218.md) - 详细的改进说明
- [API 测试报告](../../docs/poc/api-test-report.md) - API 测试结果
- [问题分析](ISSUES_ANALYSIS.md) - 已知问题和解决方案
- [测试报告](TEST_REPORT.md) - 完整测试流程
- [故障排查](TROUBLESHOOTING.md) - 常见问题解决

## 🔧 开发调试

### 查看日志

服务启动时会显示详细日志：
```
2024-12-18 10:00:00 - INFO - Initializing services...
2024-12-18 10:00:00 - INFO - Cognee URL: http://192.168.66.11:8000
2024-12-18 10:00:00 - INFO - Memobase URL: http://192.168.66.11:8019
2024-12-18 10:00:00 - INFO - Mem0 URL: http://192.168.66.11:8888
2024-12-18 10:00:00 - INFO - Services initialized successfully
```

### 调试模式

设置日志级别为 DEBUG：
```bash
export LOG_LEVEL=DEBUG
python3 -m src.main
```

### 测试单个组件

```bash
# 测试 Memobase 客户端
python3 test_memobase_profile.py

# 测试 Mem0 客户端
python3 test_mem0_client.py

# 测试所有服务
python3 test_all_services.py
```

## 🎉 现在开始

1. ✅ 确认语法修复：`python3 test_syntax.py`
2. ✅ 验证功能改进：`python3 test_improvements.py`
3. 🚀 启动服务：`./start_poc.sh`
4. 💬 测试对话：`python3 quick_test.py`
5. 📊 查看诊断：`python3 diagnose.py`

祝你使用愉快！🎊
