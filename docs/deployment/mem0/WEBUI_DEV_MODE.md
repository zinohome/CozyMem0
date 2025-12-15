# WebUI 开发模式部署指南

## 概述

使用 `npm run dev` 启动 WebUI，可以在运行时读取环境变量，**无需重新构建镜像**。

## 开发模式 vs 生产模式

### 开发模式（npm run dev）

**优点**：
- ✅ **运行时环境变量**：修改环境变量后只需重启容器
- ✅ **无需重新构建**：修改 `NEXT_PUBLIC_*` 变量后立即生效
- ✅ **热重载支持**：如果挂载源代码，支持代码热重载
- ✅ **开发友好**：适合开发和测试

**缺点**：
- ⚠️ **性能较慢**：开发模式比生产模式慢
- ⚠️ **内存占用高**：开发模式占用更多内存
- ⚠️ **不适合生产**：仅用于开发/测试环境

### 生产模式（npm run build + node server.js）

**优点**：
- ✅ **性能最优**：生产模式经过优化
- ✅ **资源占用低**：更少的内存和 CPU 占用
- ✅ **适合生产**：生产环境推荐

**缺点**：
- ❌ **需要重新构建**：修改 `NEXT_PUBLIC_*` 变量需要重新构建镜像

## 使用方法

### 方式 1：使用开发模式 Dockerfile

#### 1. 构建开发模式镜像

```bash
cd /data/build/CozyMem0/deployment/mem0
./build-webui-dev.sh
```

#### 2. 使用开发模式 docker-compose

```bash
# 使用开发模式配置
docker-compose -f docker-compose.dev.yml up -d mem0-webui-dev
```

#### 3. 修改环境变量（无需重建）

```yaml
# docker-compose.dev.yml
environment:
  NEXT_PUBLIC_API_URL: http://new-api:8000  # 修改后只需重启
  NEXT_PUBLIC_USER_ID: admin
```

```bash
# 重启容器即可生效
docker-compose -f docker-compose.dev.yml restart mem0-webui-dev
```

### 方式 2：修改现有 docker-compose（开发模式）

在 `docker-compose.1panel.yml` 中修改：

```yaml
mem0-webui:
  build:
    context: ../..
    dockerfile: deployment/mem0/webui.dev.Dockerfile
  # 或使用已构建的镜像
  # image: mem0-webui-dev:latest
  command: pnpm run dev  # 使用开发模式
  environment:
    NEXT_PUBLIC_API_URL: http://mem0-api:8000
    NEXT_PUBLIC_USER_ID: admin
```

## 配置说明

### 开发模式 Dockerfile

`webui.dev.Dockerfile` 的特点：

1. **不执行构建**：只安装依赖，不运行 `pnpm build`
2. **使用开发模式**：`CMD ["pnpm", "run", "dev"]`
3. **支持环境变量**：运行时读取 `NEXT_PUBLIC_*` 环境变量

### 环境变量

开发模式下，环境变量在运行时生效：

```yaml
environment:
  # 这些变量在运行时读取，修改后只需重启容器
  NEXT_PUBLIC_API_URL: http://mem0-api:8000
  NEXT_PUBLIC_USER_ID: admin
```

## 性能对比

### 开发模式

- **启动时间**：5-10 秒
- **内存占用**：~500MB
- **响应时间**：较慢（首次请求可能 1-2 秒）
- **适用场景**：开发、测试

### 生产模式

- **启动时间**：1-2 秒
- **内存占用**：~200MB
- **响应时间**：快（< 100ms）
- **适用场景**：生产环境

## 使用场景

### ✅ 适合使用开发模式

1. **开发和测试环境**
2. **需要频繁修改环境变量**
3. **需要代码热重载**
4. **性能要求不高**

### ❌ 不适合使用开发模式

1. **生产环境**（性能要求高）
2. **资源受限环境**（内存/CPU 有限）
3. **高并发场景**

## 完整示例

### 开发模式部署

```bash
cd /data/build/CozyMem0/deployment/mem0

# 1. 构建开发模式镜像
./build-webui-dev.sh

# 2. 启动服务（使用开发模式配置）
docker-compose -f docker-compose.dev.yml up -d

# 3. 修改环境变量
# 编辑 docker-compose.dev.yml，修改 NEXT_PUBLIC_API_URL

# 4. 重启容器（无需重建）
docker-compose -f docker-compose.dev.yml restart mem0-webui-dev
```

### 验证

```bash
# 检查容器是否运行
docker ps | grep mem0-webui-dev

# 检查日志
docker logs mem0-webui-dev --tail 20

# 检查环境变量
docker exec mem0-webui-dev env | grep NEXT_PUBLIC

# 访问 WebUI
# http://192.168.66.11:3000
```

## 热重载（可选）

如果需要代码热重载，可以挂载源代码：

```yaml
mem0-webui-dev:
  volumes:
    - ../../projects/mem0/openmemory/ui:/app
    - /app/node_modules  # 防止覆盖 node_modules
    - /app/.next         # 防止覆盖构建缓存
```

**注意**：挂载源代码后，容器内的修改会同步到主机，但需要确保文件权限正确。

## 故障排查

### 问题 1：开发模式启动失败

**检查**：
```bash
docker logs mem0-webui-dev
```

**可能原因**：
- 依赖未安装
- 端口被占用
- 环境变量配置错误

### 问题 2：环境变量不生效

**检查**：
```bash
# 检查环境变量
docker exec mem0-webui-dev env | grep NEXT_PUBLIC

# 检查 Next.js 是否读取
docker logs mem0-webui-dev | grep -i "env\|NEXT_PUBLIC"
```

### 问题 3：性能问题

**如果开发模式太慢**：
- 考虑使用生产模式
- 或优化开发模式配置

## 总结

### ✅ **开发模式的优势**

1. **运行时环境变量**：修改 `NEXT_PUBLIC_*` 变量后只需重启容器
2. **无需重新构建**：大大简化开发和测试流程
3. **灵活配置**：可以快速切换不同的配置

### 📝 **推荐使用场景**

- ✅ **开发环境**：使用开发模式
- ✅ **测试环境**：使用开发模式
- ❌ **生产环境**：使用生产模式（构建后的镜像）

## 参考

- [Next.js 开发模式文档](https://nextjs.org/docs/getting-started/installation)
- [webui.dev.Dockerfile](../webui.dev.Dockerfile)
- [docker-compose.dev.yml](../docker-compose.dev.yml)

