# Memobase Swagger API 文档使用指南

**服务地址**: `http://192.168.66.11:8019`

## 访问 Swagger 文档

### 方式1: 通过浏览器访问（推荐）

打开浏览器，访问以下地址：

- **Swagger UI**: http://192.168.66.11:8019/docs
- **ReDoc**: http://192.168.66.11:8019/redoc
- **OpenAPI JSON**: http://192.168.66.11:8019/openapi.json

**注意**: Swagger UI 地址是 `/docs`，不是 `/swagger`

### 方式2: 通过 curl 查看 OpenAPI 规范

```bash
curl -X GET "http://192.168.66.11:8019/openapi.json"
```

---

## API 认证方式

### 认证方式

Memobase API 使用 **Bearer Token** 认证方式。

### API Key 配置

在 POC 项目中，默认的 API Key 是 `secret`（可在 `.env` 文件中配置）。

### 在 Swagger UI 中设置认证

1. 打开 Swagger UI: `http://192.168.66.11:8019/docs`
2. 点击右上角的 **"Authorize"** 按钮
3. 在弹出的对话框中，输入你的 API Key
4. 点击 **"Authorize"** 确认
5. 点击 **"Close"** 关闭对话框

现在你可以测试所有需要认证的 API 端点了。

### 在 curl 请求中使用认证

```bash
# 使用 Bearer Token 认证
curl -X GET "http://192.168.66.11:8019/api/v1/users/{user_id}" \
  -H "Authorization: Bearer secret"
```

### 在 Python 中使用认证

```python
import httpx

# 方式1: 在请求头中添加认证
headers = {
    "Authorization": "Bearer secret"
}

response = httpx.get(
    "http://192.168.66.11:8019/api/v1/users/{user_id}",
    headers=headers
)

# 方式2: 使用 Memobase SDK（推荐）
from memobase import MemoBaseClient

client = MemoBaseClient(
    project_url="http://192.168.66.11:8019",
    api_key="secret"  # 你的 API Key
)

user = client.get_user("user_id")
```

---

## 常用 API 端点

### 1. 健康检查

**端点**: `GET /api/v1/healthcheck`

**认证**: 不需要

**请求**:
```bash
curl -X GET "http://192.168.66.11:8019/api/v1/healthcheck"
```

**响应**:
```json
{
  "data": null,
  "errno": 0,
  "errmsg": ""
}
```

---

### 2. 创建用户

**端点**: `POST /api/v1/users`

**认证**: 需要

**请求**:
```bash
curl -X POST "http://192.168.66.11:8019/api/v1/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret" \
  -d '{
    "id": "user-uuid-here",
    "data": {}
  }'
```

**响应**:
```json
{
  "data": {
    "id": "user-uuid-here"
  },
  "errno": 0,
  "errmsg": ""
}
```

---

### 3. 获取用户

**端点**: `GET /api/v1/users/{user_id}`

**认证**: 需要

**请求**:
```bash
curl -X GET "http://192.168.66.11:8019/api/v1/users/{user_id}" \
  -H "Authorization: Bearer secret"
```

**响应**:
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

---

## 在 Swagger UI 中测试 API

### 步骤1: 打开 Swagger UI

访问: `http://192.168.66.11:8019/docs`

### 步骤2: 设置认证

1. 点击右上角的 **"Authorize"** 按钮
2. 在 `Value` 字段中输入你的 API Key（默认是 `secret`）
3. 点击 **"Authorize"** 确认
4. 点击 **"Close"** 关闭对话框

### 步骤3: 测试 API

1. 展开你想要测试的 API 端点
2. 点击 **"Try it out"** 按钮
3. 填写请求参数（如果需要）
4. 点击 **"Execute"** 执行请求
5. 查看响应结果

### 示例: 测试健康检查

1. 找到 `GET /api/v1/healthcheck` 端点
2. 点击 **"Try it out"**
3. 点击 **"Execute"**
4. 查看响应:
   ```json
   {
     "data": null,
     "errno": 0,
     "errmsg": ""
   }
   ```

### 示例: 测试创建用户

1. 找到 `POST /api/v1/users` 端点
2. 点击 **"Try it out"**
3. 在请求体中输入:
   ```json
   {
     "id": "5e7e5f3b-6416-567a-80cb-4ee21a6a03ec",
     "data": {}
   }
   ```
4. 点击 **"Execute"**
5. 查看响应结果

---

## 错误处理

### 常见错误码

- `errno: 0` - 成功
- `errno: 404` - 资源不存在（如用户不存在）
- `errno: 401` - 认证失败（API Key 错误）
- `errno: 500` - 服务器错误

### 认证失败示例

如果 API Key 错误，会返回：

```json
{
  "detail": "Not authenticated"
}
```

**解决方法**: 检查 API Key 是否正确，确保在请求头中正确设置了 `Authorization: Bearer {your-api-key}`

---

## 配置 API Key

### 在 POC 项目中配置

编辑 `.env` 文件：

```bash
MEMOBASE_PROJECT_URL=http://192.168.66.11:8019
MEMOBASE_API_KEY=secret
```

### 在环境变量中配置

```bash
export MEMOBASE_PROJECT_URL="http://192.168.66.11:8019"
export MEMOBASE_API_KEY="secret"
```

---

## 完整示例

### 使用 curl 测试完整流程

```bash
# 1. 健康检查（不需要认证）
curl -X GET "http://192.168.66.11:8019/api/v1/healthcheck"

# 2. 创建用户（需要认证）
curl -X POST "http://192.168.66.11:8019/api/v1/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret" \
  -d '{
    "id": "5e7e5f3b-6416-567a-80cb-4ee21a6a03ec",
    "data": {}
  }'

# 3. 获取用户（需要认证）
curl -X GET "http://192.168.66.11:8019/api/v1/users/5e7e5f3b-6416-567a-80cb-4ee21a6a03ec" \
  -H "Authorization: Bearer secret"
```

### 使用 Python 测试

```python
import httpx
import uuid

# API 配置
BASE_URL = "http://192.168.66.11:8019"
API_KEY = "secret"

# 创建 HTTP 客户端
client = httpx.Client(
    base_url=BASE_URL,
    headers={"Authorization": f"Bearer {API_KEY}"}
)

# 1. 健康检查
response = client.get("/api/v1/healthcheck")
print("健康检查:", response.json())

# 2. 创建用户
user_id = str(uuid.uuid4())
response = client.post(
    "/api/v1/users",
    json={"id": user_id, "data": {}}
)
print("创建用户:", response.json())

# 3. 获取用户
response = client.get(f"/api/v1/users/{user_id}")
print("获取用户:", response.json())
```

---

## 注意事项

1. **API Key 安全**: 不要将 API Key 提交到代码仓库，使用环境变量或 `.env` 文件
2. **用户ID格式**: Memobase要求用户ID必须是UUID格式
3. **认证头格式**: 必须使用 `Bearer {token}` 格式，注意大小写
4. **Swagger UI**: 某些高级功能（如用户画像）主要通过SDK使用，REST API端点可能不直接暴露

---

## 参考资源

- **Memobase 官方文档**: https://docs.memobase.io/api-reference/overview
- **Memobase GitHub**: https://github.com/memodb-io/memobase
- **POC项目配置**: `projects/conversational-agent-poc/src/config.py`
- **Memobase客户端封装**: `projects/conversational-agent-poc/src/clients/memobase_client.py`

---

**文档生成时间**: 2025-12-18

