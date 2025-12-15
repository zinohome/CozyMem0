# WebUI 用户配置指南

## 默认用户

WebUI 默认使用用户 ID `"user"`。所有通过 WebUI 创建的记忆都会使用这个用户 ID。

## 如何更改默认用户

### 方法 1：通过环境变量配置（推荐）

在 `docker-compose.1panel.yml` 或 `docker-compose.yml` 中配置：

```yaml
mem0-webui:
  environment:
    # 配置默认用户 ID
    NEXT_PUBLIC_USER_ID: your-custom-user-id
```

**示例**：

```yaml
environment:
  NEXT_PUBLIC_API_URL: http://mem0-api:8000
  NEXT_PUBLIC_USER_ID: admin  # 使用 "admin" 作为默认用户
```

### 方法 2：使用 .env 文件

创建 `.env` 文件：

```env
NEXT_PUBLIC_USER_ID=your-custom-user-id
```

然后在 `docker-compose.yml` 中引用：

```yaml
env_file:
  - .env
```

### 方法 3：在 1Panel 中配置

在 1Panel 的应用配置中，添加环境变量：

- 变量名：`NEXT_PUBLIC_USER_ID`
- 变量值：你想要的用户 ID（例如：`admin`、`user001` 等）

## 配置说明

### 环境变量

- **变量名**：`NEXT_PUBLIC_USER_ID`
- **默认值**：`"user"`
- **说明**：所有通过 WebUI 创建的记忆都会使用此用户 ID

### 使用场景

1. **多用户环境**：如果需要支持多个用户，可以为每个用户部署独立的 WebUI 实例
2. **生产环境**：使用有意义的用户 ID，如 `admin`、`system` 等
3. **开发环境**：可以使用默认的 `user` 或自定义 ID

## 注意事项

### 1. 需要重新构建镜像（如果使用构建时环境变量）

如果用户名是在构建时设置的（在 `webui.Dockerfile` 中），需要重新构建镜像：

```bash
cd /data/build/CozyMem0/deployment/mem0
./build-webui.sh
```

### 2. 运行时环境变量（推荐）

使用运行时环境变量（在 `docker-compose` 中配置）更灵活，**无需重新构建镜像**，只需重启容器：

```bash
docker-compose -f docker-compose.1panel.yml restart mem0-webui
```

### 3. 用户 ID 的作用

- 所有通过 WebUI 创建的记忆都会使用此用户 ID
- 所有通过 WebUI 查询的记忆都会过滤此用户 ID
- 用户 ID 用于区分不同用户的记忆数据

### 4. 用户 ID 格式

- 可以是任何字符串
- 建议使用有意义的名称（如：`admin`、`user001`、`system`）
- 避免使用特殊字符（虽然技术上支持）

## 配置示例

### 示例 1：使用 "admin" 作为默认用户

```yaml
mem0-webui:
  environment:
    NEXT_PUBLIC_API_URL: http://mem0-api:8000
    NEXT_PUBLIC_USER_ID: admin
```

### 示例 2：使用环境变量

```yaml
mem0-webui:
  environment:
    NEXT_PUBLIC_API_URL: http://mem0-api:8000
    NEXT_PUBLIC_USER_ID: ${WEBUI_USER_ID:-user}  # 从环境变量读取，默认 "user"
```

然后在 `.env` 文件中：

```env
WEBUI_USER_ID=admin
```

### 示例 3：多用户部署

如果需要支持多个用户，可以部署多个 WebUI 实例：

```yaml
mem0-webui-admin:
  image: mem0-webui:latest
  environment:
    NEXT_PUBLIC_API_URL: http://mem0-api:8000
    NEXT_PUBLIC_USER_ID: admin
  ports:
    - "3000:3000"

mem0-webui-user1:
  image: mem0-webui:latest
  environment:
    NEXT_PUBLIC_API_URL: http://mem0-api:8000
    NEXT_PUBLIC_USER_ID: user1
  ports:
    - "3001:3000"
```

## 验证配置

配置后，验证：

1. **检查环境变量**：
```bash
docker exec mem0-webui env | grep NEXT_PUBLIC_USER_ID
```

2. **检查 WebUI 行为**：
   - 打开 WebUI
   - 创建一个记忆
   - 检查 API 日志，确认记忆使用了正确的用户 ID

3. **通过 API 验证**：
```bash
curl "http://192.168.66.11:8888/memories?user_id=your-user-id" | jq .
```

## 相关代码

用户名配置在以下文件中：

- `projects/mem0/openmemory/ui/store/profileSlice.ts` - Redux store，读取环境变量
- `projects/mem0/openmemory/ui/hooks/useMemoriesApi.ts` - 使用用户 ID 调用 API
- `deployment/mem0/webui-adapters/useMemoriesApi.mem0.ts` - Mem0 API 适配器

## 参考

- [Next.js 环境变量文档](https://nextjs.org/docs/basic-features/environment-variables)
- [Redux Toolkit 文档](https://redux-toolkit.js.org/)

