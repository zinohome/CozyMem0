# API 使用指南

## 快速测试

### 1. 启动服务

```bash
cd projects/conversational-agent-poc
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件，配置 API 密钥

# 启动服务
python -m src.main
# 或
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### 2. 访问 API 文档

打开浏览器访问：http://localhost:8080/docs

## API 端点

### 1. 健康检查

```bash
curl http://localhost:8080/health
```

**响应**：
```json
{
  "status": "healthy"
}
```

### 2. 发送消息（标准接口）

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

**响应**：
```json
{
  "success": true,
  "session_id": "session_123",
  "response": "你好！我很乐意帮助你了解Python编程...",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 3. 测试对话（返回完整上下文信息）⭐ 推荐用于测试

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

**响应**（包含完整上下文信息）：
```json
{
  "success": true,
  "user_id": "user_123",
  "session_id": "session_123",
  "message": "你好，我想了解一下Python编程",
  "response": "你好！我很乐意帮助你了解Python编程...",
  "context": {
    "user_profile": {
      "basic_info": {
        "name": "用户123"
      },
      "interest": {
        "programming": "Python"
      }
    },
    "session_memories_count": 3,
    "knowledge_count": 5,
    "session_memories": [
      {
        "content": "用户之前询问过Python基础语法",
        "type": "semantic",
        "session": "current",
        "timestamp": "2024-01-01T00:00:00Z"
      }
    ],
    "knowledge": [
      {
        "content": "Python是一种高级编程语言...",
        "score": 0.95,
        "source": "kb_tech"
      }
    ]
  },
  "dataset_names": ["kb_tech"]
}
```

### 4. 获取用户画像

```bash
curl "http://localhost:8080/api/v1/users/user_123/profile"
```

**响应**：
```json
{
  "success": true,
  "user_id": "user_123",
  "profile": {
    "basic_info": {
      "name": "用户123",
      "language": "中文"
    },
    "interest": {
      "programming": "Python, JavaScript"
    },
    "work": {
      "industry": "IT",
      "role": "Developer"
    }
  }
}
```

## 测试流程示例

### 完整对话测试流程

```bash
# 1. 第一次对话（新用户）
curl -X POST "http://localhost:8080/api/v1/test/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "message": "你好，我是张三，我是一名软件工程师，对Python很感兴趣",
    "dataset_names": ["kb_tech"]
  }'

# 2. 第二次对话（应该能记住用户信息）
curl -X POST "http://localhost:8080/api/v1/test/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "session_id": "session_001",
    "message": "我之前说过我的职业是什么？",
    "dataset_names": ["kb_tech"]
  }'

# 3. 查看用户画像
curl "http://localhost:8080/api/v1/users/user_001/profile"

# 4. 新会话（跨会话记忆测试）
curl -X POST "http://localhost:8080/api/v1/test/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "session_id": "session_002",
    "message": "你还记得我的职业吗？",
    "dataset_names": ["kb_tech"]
  }'
```

## 使用 Python 测试

```python
import requests
import json

BASE_URL = "http://localhost:8080"

# 测试对话
def test_conversation():
    url = f"{BASE_URL}/api/v1/test/conversation"
    data = {
        "user_id": "user_001",
        "session_id": "session_001",
        "message": "你好，我想了解Python编程",
        "dataset_names": ["kb_tech"]
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print("响应:", result["response"])
    print("用户画像:", json.dumps(result["context"]["user_profile"], indent=2, ensure_ascii=False))
    print("会话记忆数量:", result["context"]["session_memories_count"])
    print("知识数量:", result["context"]["knowledge_count"])
    
    return result

# 获取用户画像
def get_profile(user_id: str):
    url = f"{BASE_URL}/api/v1/users/{user_id}/profile"
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    # 测试对话
    result = test_conversation()
    
    # 获取用户画像
    profile = get_profile("user_001")
    print("\n用户画像:", json.dumps(profile, indent=2, ensure_ascii=False))
```

## 使用 JavaScript/Node.js 测试

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8080';

// 测试对话
async function testConversation() {
  const response = await axios.post(`${BASE_URL}/api/v1/test/conversation`, {
    user_id: 'user_001',
    session_id: 'session_001',
    message: '你好，我想了解Python编程',
    dataset_names: ['kb_tech']
  });
  
  console.log('响应:', response.data.response);
  console.log('用户画像:', JSON.stringify(response.data.context.user_profile, null, 2));
  console.log('会话记忆数量:', response.data.context.session_memories_count);
  console.log('知识数量:', response.data.context.knowledge_count);
  
  return response.data;
}

// 获取用户画像
async function getProfile(userId) {
  const response = await axios.get(`${BASE_URL}/api/v1/users/${userId}/profile`);
  return response.data;
}

// 运行测试
(async () => {
  const result = await testConversation();
  const profile = await getProfile('user_001');
  console.log('\n用户画像:', JSON.stringify(profile, null, 2));
})();
```

## 注意事项

1. **确保服务已启动**：Cognee、Memobase、Mem0 服务必须运行
2. **配置 API 密钥**：在 `.env` 文件中配置 OpenAI API 密钥
3. **知识库名称**：`dataset_names` 应该是 Cognee 中已存在的数据集名称
4. **用户ID和会话ID**：使用有意义的ID便于测试和调试

## 故障排查

### 1. 服务未初始化

**错误**：`Service not initialized`

**解决**：检查服务启动日志，确保所有客户端初始化成功

### 2. OpenAI API 错误

**错误**：`OpenAI API error`

**解决**：检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确

### 3. 知识库不存在

**错误**：知识检索返回空结果

**解决**：确保 Cognee 中已创建对应的数据集，并使用正确的数据集名称

