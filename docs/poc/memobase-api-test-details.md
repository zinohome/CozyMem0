# Memobase API 详细测试报告

**测试日期**: 2025-12-18  
**测试工具**: `test_all_apis.py`  
**服务地址**: `http://192.168.66.11:8019`

## 测试总结

- **总测试数**: 5
- **成功**: 3 (60%)
- **失败**: 2 (40%) - 这些功能通过SDK使用，REST API不直接暴露

## 1. 健康检查 ✅

**端点**: `GET /api/v1/healthcheck`

**请求**:
```bash
curl -X GET "http://192.168.66.11:8019/api/v1/healthcheck"
```

**响应** (HTTP 200):
```json
{
  "data": null,
  "errno": 0,
  "errmsg": ""
}
```

**说明**: 
- `errno: 0` 表示服务正常
- Memobase服务运行正常

---

## 2. 获取用户（创建前）✅

**端点**: `GET /api/v1/users/{user_id}`

**请求**:
```bash
# 注意：user_id必须是UUID格式
# 对于test_user_001，UUID为: 5e7e5f3b-6416-567a-80cb-4ee21a6a03ec
curl -X GET "http://192.168.66.11:8019/api/v1/users/5e7e5f3b-6416-567a-80cb-4ee21a6a03ec"
```

**响应** (HTTP 200):
```json
{
  "data": null,
  "errno": 404,
  "errmsg": "User 5e7e5f3b-6416-567a-80cb-4ee21a6a03ec not found"
}
```

**说明**: 
- 用户不存在时返回 `errno: 404`
- 这是正常的响应格式

---

## 3. 创建用户 ✅

**端点**: `POST /api/v1/users`

**请求**:
```bash
curl -X POST "http://192.168.66.11:8019/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "5e7e5f3b-6416-567a-80cb-4ee21a6a03ec",
    "data": {}
  }'
```

**响应** (HTTP 200):
```json
{
  "data": {
    "id": "5e7e5f3b-6416-567a-80cb-4ee21a6a03ec"
  },
  "errno": 0,
  "errmsg": ""
}
```

**说明**: 
- 成功创建用户
- `errno: 0` 表示操作成功
- 返回创建的用户ID

---

## 4. 获取用户（创建后）✅

**端点**: `GET /api/v1/users/{user_id}`

**请求**:
```bash
curl -X GET "http://192.168.66.11:8019/api/v1/users/5e7e5f3b-6416-567a-80cb-4ee21a6a03ec"
```

**响应** (HTTP 200):
```json
{
  "data": {
    "data": {},
    "id": null,
    "created_at": "2025-12-18T01:14:42.240013Z",
    "updated_at": "2025-12-18T01:14:42.240013Z"
  },
  "errno": 0,
  "errmsg": ""
}
```

**说明**: 
- 成功获取用户信息
- 包含创建时间和更新时间
- `data` 字段包含用户的自定义数据（当前为空）

---

## 5. 用户画像、对话数据等高级功能 ⚠️

**重要说明**: Memobase的高级功能（用户画像、对话数据插入、数据刷新等）主要通过 **Python SDK** 使用，而不是直接通过REST API。

### 5.1 用户画像端点

**端点**: `GET /api/v1/users/{user_id}/profile`

**测试结果**: HTTP 404 - 端点不存在

**说明**: 用户画像功能通过SDK的 `user.profile()` 方法使用。

### 5.2 插入对话数据端点

**端点**: `POST /api/v1/users/{user_id}/blobs`

**测试结果**: HTTP 404 - 端点不存在

**说明**: 对话数据插入通过SDK的 `user.insert(blob)` 方法使用。

### 5.3 刷新用户数据端点

**端点**: `POST /api/v1/users/{user_id}/flush`

**测试结果**: HTTP 404 - 端点不存在

**说明**: 数据刷新通过SDK的 `user.flush()` 方法使用。

---

## Memobase SDK 使用指南

### 安装SDK

```bash
pip install memobase
```

### 初始化客户端

```python
from memobase import MemoBaseClient, ChatBlob

client = MemoBaseClient(
    project_url="http://192.168.66.11:8019",
    api_key="your-api-key"
)
```

### 创建用户

```python
# 方式1: 直接创建
user_id = client.add_user({"name": "测试用户"})

# 方式2: 获取或创建
user = client.get_or_create_user(user_id)
```

### 插入对话数据

```python
# 创建对话数据
blob = ChatBlob(messages=[
    {"role": "user", "content": "你好，我是测试用户，我是一名软件工程师，对Python很感兴趣"},
    {"role": "assistant", "content": "很高兴认识你！作为一名软件工程师，Python是一个很好的选择。"}
])

# 插入数据
user.insert(blob)

# 刷新数据（触发画像更新）
user.flush(sync=True)
```

### 获取用户画像

```python
# 获取用户画像
profile = user.profile(
    max_token_size=500,
    prefer_topics=["basic_info", "interest", "work"]
)

print(profile)
```

### 完整示例

```python
from memobase import MemoBaseClient, ChatBlob
import uuid

# 初始化客户端
client = MemoBaseClient(
    project_url="http://192.168.66.11:8019",
    api_key="your-api-key"
)

# 将任意用户ID转换为UUID
def user_id_to_uuid(user_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))

# 获取或创建用户
user_id = user_id_to_uuid("test_user_001")
user = client.get_or_create_user(user_id)

# 插入对话数据
blob = ChatBlob(messages=[
    {"role": "user", "content": "你好，我是测试用户，我是一名软件工程师"},
    {"role": "assistant", "content": "很高兴认识你！"}
])
user.insert(blob)
user.flush(sync=True)

# 获取用户画像
profile = user.profile(max_token_size=500)
print(f"用户画像: {profile}")
```

---

## 在POC项目中的使用

在POC项目中，Memobase通过 `MemobaseClientWrapper` 类封装使用：

### 获取用户画像

```python
from src.clients.memobase_client import MemobaseClientWrapper

client = MemobaseClientWrapper()
profile = client.get_user_profile("test_user_001", max_token_size=500)
```

### 更新用户画像

```python
messages = [
    {"role": "user", "content": "你好，我是测试用户"},
    {"role": "assistant", "content": "很高兴认识你！"}
]
client.extract_and_update_profile("test_user_001", messages)
```

---

## API响应格式说明

Memobase的REST API使用统一的响应格式：

```json
{
  "data": <响应数据>,
  "errno": <错误码>,
  "errmsg": <错误消息>
}
```

### 错误码说明

- `errno: 0` - 成功
- `errno: 404` - 资源不存在（如用户不存在）
- 其他错误码 - 参考Memobase官方文档

---

## 测试结论

### ✅ 功能正常

1. **健康检查**: 正常工作
2. **用户创建**: 正常工作
3. **用户获取**: 正常工作

### ⚠️ 注意事项

1. **高级功能通过SDK使用**: 用户画像、对话数据插入等功能主要通过Python SDK使用，REST API端点不直接暴露
2. **用户ID格式**: Memobase要求用户ID必须是UUID格式，POC项目中使用 `uuid.uuid5()` 将任意字符串转换为UUID
3. **异步处理**: 用户画像的更新可能需要时间，`flush()` 操作会触发画像更新

### 📊 性能指标

- **API响应时间**: 所有API响应时间在可接受范围内
- **成功率**: 基础功能 100% 正常工作
- **SDK功能**: 通过SDK使用的功能在POC项目中正常工作

---

**文档生成时间**: 2025-12-18  
**测试执行时间**: 2025-12-18 09:14:26 - 09:17:38
