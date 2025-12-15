# CORS 问题修复指南

## 问题描述

前端访问 API 时出现 CORS 错误：
```
Access to XMLHttpRequest at 'http://192.168.66.11:8888/memories?user_id=user' 
from origin 'http://192.168.66.11:4000' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## 解决方案

已通过 patch 方式添加 CORS 支持，不修改 `projects/mem0` 目录。

### 1. Patch 文件

位置：`deployment/mem0/patches/cors.patch`

内容：
- 添加 `CORSMiddleware` 导入
- 添加 CORS 配置，支持通过环境变量 `CORS_ORIGINS` 配置允许的源

### 2. Dockerfile 配置

在 Dockerfile 中自动应用 patch：
```dockerfile
# 应用 CORS patch（在构建时应用，不修改源文件）
COPY deployment/mem0/patches/cors.patch /tmp/cors.patch
RUN cd /app && patch -p0 < /tmp/cors.patch || (echo "Warning: CORS patch failed, continuing..." && true)
```

### 3. 验证 Patch

运行验证脚本：
```bash
cd /data/build/CozyMem0
./deployment/mem0/verify-patch.sh
```

应该看到：
```
✅ Patch 应用成功
✅ 找到 CORSMiddleware 导入
✅ 找到 CORS 中间件配置
```

### 4. 重新构建镜像

**重要**：必须重新构建镜像才能应用 patch！

```bash
cd /data/build/CozyMem0/deployment/mem0

# 停止并删除旧容器
docker-compose -f docker-compose.1panel.yml stop mem0-api
docker-compose -f docker-compose.1panel.yml rm -f mem0-api

# 删除旧镜像（确保使用新构建的镜像）
docker rmi mem0-api:latest

# 重新构建镜像
./build.sh

# 启动服务
docker-compose -f docker-compose.1panel.yml up -d mem0-api

# 检查日志，确认 patch 已应用
docker logs mem0-api | grep -i cors || echo "检查服务是否正常启动"
```

### 5. 验证 CORS 配置

#### 方法 1：检查响应头

```bash
curl -H "Origin: http://192.168.66.11:4000" \
     -H "Access-Control-Request-Method: GET" \
     -v \
     http://192.168.66.11:8888/memories?user_id=test 2>&1 | grep -i "access-control"
```

应该看到：
```
< access-control-allow-origin: http://192.168.66.11:4000
< access-control-allow-credentials: true
```

#### 方法 2：检查容器内的代码

```bash
# 检查容器内的 main.py 是否包含 CORS 代码
docker exec mem0-api grep -A 5 "CORSMiddleware" /app/main.py
```

应该看到：
```python
from fastapi.middleware.cors import CORSMiddleware
...
app.add_middleware(
    CORSMiddleware,
    ...
)
```

### 6. 如果仍然失败

#### 检查 1：确认镜像已重新构建

```bash
# 检查镜像构建时间
docker images mem0-api:latest

# 检查容器内的文件修改时间
docker exec mem0-api ls -la /app/main.py
```

#### 检查 2：确认 patch 已应用

```bash
# 在容器内检查
docker exec mem0-api cat /app/main.py | grep -A 10 "CORSMiddleware"
```

如果没有输出，说明 patch 没有应用。

#### 检查 3：查看构建日志

重新构建时，检查是否有 patch 相关的错误：
```bash
./build.sh 2>&1 | grep -i patch
```

#### 检查 4：手动验证 patch

```bash
# 在构建上下文中测试 patch
cd /data/build/CozyMem0
./deployment/mem0/verify-patch.sh
```

### 7. 环境变量配置

CORS 允许的源可以通过环境变量配置：

```yaml
# docker-compose.1panel.yml
environment:
  CORS_ORIGINS: http://localhost:3000,http://localhost:4000,http://192.168.66.11:3000,http://192.168.66.11:4000
```

默认值已包含常见的本地和服务器地址。

### 8. 常见问题

#### Q: 为什么重新构建后还是报 CORS 错误？

A: 可能的原因：
1. 使用了缓存的旧镜像 - 需要删除旧镜像：`docker rmi mem0-api:latest`
2. patch 应用失败 - 检查构建日志
3. 容器使用的是旧镜像 - 确保重新创建容器

#### Q: 如何确认 patch 已应用？

A: 运行：
```bash
docker exec mem0-api python -c "from fastapi.middleware.cors import CORSMiddleware; print('CORS imported successfully')"
```

如果成功，说明 patch 已应用。

#### Q: 可以允许所有源吗？

A: 可以，但不推荐。如果需要，修改 patch 文件中的配置：
```python
allow_origins=["*"]  # 允许所有源（不推荐用于生产环境）
```

## 总结

1. ✅ Patch 文件已创建并验证
2. ✅ Dockerfile 已配置自动应用 patch
3. ⚠️ **必须重新构建镜像**
4. ⚠️ **必须重新创建容器**

如果按照上述步骤操作后仍然失败，请检查：
- 镜像构建时间
- 容器内的代码
- 构建日志中的错误信息

