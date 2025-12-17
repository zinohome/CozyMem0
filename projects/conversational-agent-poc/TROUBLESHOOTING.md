# 故障排查指南

## 问题分析

### 1. Memobase 422 错误

**错误信息**：
```
422 Unprocessable Entity for url 'http://192.168.66.11:8019/api/v1/users/user_123'
```

**可能原因**：
- Memobase SDK 使用的 API 路径可能不正确
- Memobase 服务器可能不支持 `/api/v1` 前缀
- 请求格式不符合 Memobase 服务器要求

**解决方案**：
1. 检查 Memobase 服务器的实际 API 路径
2. 查看 Memobase 服务器的 API 文档：`http://192.168.66.11:8019/docs`
3. 确认 Memobase SDK 版本是否与服务器版本匹配

**临时解决方案**：
- 如果 Memobase 服务不可用，系统会返回空用户画像，但不影响对话功能
- 用户画像会在后续对话中逐步建立

### 2. Cognee 数据集不存在

**错误信息**：
```
[409] DatasetNotFoundError: No datasets found. (Status code: 404)
```

**原因**：
- 请求的数据集 `kb_tech` 在 Cognee 中不存在
- 需要先创建数据集

**解决方案**：

#### 方案 1: 创建数据集（推荐）

```bash
# 使用 Cognee SDK 创建数据集
python3 << EOF
import asyncio
from cognee_sdk import CogneeClient

async def create_dataset():
    client = CogneeClient(
        api_url="http://192.168.66.11:8000",
        api_token="your-token-if-needed"
    )
    
    # 添加数据到数据集
    result = await client.add(
        data="Python是一种高级编程语言...",
        dataset_name="kb_tech"
    )
    print(f"数据集创建成功: {result}")
    
    await client.close()

asyncio.run(create_dataset())
EOF
```

#### 方案 2: 使用空数据集（临时）

在 API 请求中不指定数据集或使用空数组：

```bash
curl -X POST "http://localhost:8080/api/v1/test/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "session_id": "session_123",
    "message": "你好，我想了解一下Python编程",
    "dataset_names": []
  }'
```

#### 方案 3: 检查现有数据集

```bash
# 访问 Cognee API 文档查看数据集
open http://192.168.66.11:8000/docs
```

### 3. Mem0 无记忆数据

**现象**：
```
Retrieved 0 session memories
```

**原因**：
- 这是正常现象，因为是第一次使用
- 记忆会在对话保存后逐步积累

**解决方案**：
- 继续使用系统，记忆会自动保存
- 第二次对话时就能看到之前的记忆

## 快速诊断

### 1. 检查服务状态

```bash
curl http://localhost:8080/api/v1/debug/status
```

### 2. 测试各个服务

```bash
# 测试 Cognee
curl http://192.168.66.11:8000/docs

# 测试 Memobase
curl http://192.168.66.11:8019/docs

# 测试 Mem0
curl http://192.168.66.11:8888/docs
```

### 3. 运行诊断脚本

```bash
cd /Users/zhangjun/CursorProjects/CozyMem0/projects/conversational-agent-poc
python3 diagnose.py
```

## 常见问题

### Q: 为什么用户画像为空？

**A**: 
- 首次使用时，用户画像为空是正常的
- 如果持续为空，可能是 Memobase 服务连接问题
- 检查 Memobase 服务是否正常运行

### Q: 为什么知识检索返回空？

**A**:
- 检查数据集是否存在：访问 Cognee API 文档
- 确认数据集名称拼写正确
- 如果数据集不存在，先创建数据集或使用空数组

### Q: 为什么没有会话记忆？

**A**:
- 首次使用时没有记忆是正常的
- 记忆会在对话保存后自动创建
- 第二次对话时就能看到之前的记忆

### Q: 如何查看详细的错误信息？

**A**:
1. 查看服务日志（终端输出）
2. 使用调试端点：`/api/v1/debug/status`
3. 运行诊断脚本：`python3 diagnose.py`

## 最佳实践

1. **首次使用**：
   - 不指定数据集（使用空数组）
   - 系统会正常响应，但不会有知识检索结果

2. **后续使用**：
   - 先创建数据集并添加数据
   - 然后使用数据集名称进行知识检索

3. **调试**：
   - 使用 `/api/v1/test/conversation` 端点查看完整上下文
   - 查看服务日志了解详细错误信息
