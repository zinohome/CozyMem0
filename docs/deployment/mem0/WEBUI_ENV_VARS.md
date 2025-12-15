# WebUI 环境变量配置说明

## 关键问题：NEXT_PUBLIC_API_URL 修改后是否需要重新构建？

### 答案：**理论上不需要，但建议重新构建以确保可靠性**

## 机制分析

### Next.js 的 NEXT_PUBLIC_* 环境变量

Next.js 的 `NEXT_PUBLIC_*` 环境变量是**特殊的**：

1. **构建时替换**：在构建时，`process.env.NEXT_PUBLIC_API_URL` 会被替换为**构建时的实际值**
2. **客户端可见**：这些值会被打包到浏览器端代码
3. **默认需要重建**：修改这些变量通常需要重新构建

### entrypoint.sh 的运行时替换机制

**OpenMemory UI 实现了运行时替换**：

```bash
# entrypoint.sh 在容器启动时执行
# 查找所有 NEXT_PUBLIC_* 环境变量
# 并在 .next/ 目录的文件中替换它们
printenv | grep NEXT_PUBLIC_ | while read -r line ; do
  key=$(echo $line | cut -d "=" -f1)      # 例如：NEXT_PUBLIC_API_URL
  value=$(echo $line | cut -d "=" -f2)    # 例如：http://new-api:8000
  
  # 在所有 .next/ 文件中替换变量名为新值
  find .next/ -type f -exec sed -i "s|$key|$value|g" {} \;
done
```

### ⚠️ 替换机制的限制

**问题**：
- `entrypoint.sh` 查找的是**变量名**（如 `NEXT_PUBLIC_API_URL`），而不是构建时的值
- 如果构建产物中**没有变量名字符串**，替换不会生效
- Next.js 构建时会将 `process.env.NEXT_PUBLIC_API_URL` 替换为**实际值**，而不是保留变量名

**实际情况**：
- 如果构建时设置了 `NEXT_PUBLIC_API_URL=http://192.168.66.11:8888`
- 构建产物中会是：`"http://192.168.66.11:8888"`（不是 `NEXT_PUBLIC_API_URL`）
- `entrypoint.sh` 查找 `NEXT_PUBLIC_API_URL` 字符串，但构建产物中可能没有这个字符串
- **替换可能不会生效**

## 结论和建议

### ✅ **推荐做法：重新构建（最可靠）**

**原因**：
1. 确保环境变量正确嵌入构建产物
2. 不依赖可能不稳定的运行时替换
3. 更符合 Next.js 的设计理念

**步骤**：
```bash
cd /data/build/CozyMem0/deployment/mem0

# 1. 修改 docker-compose.1panel.yml 中的环境变量（可选，用于运行时）
# 2. 重新构建镜像
./build-webui.sh

# 3. 重启服务
docker-compose -f docker-compose.1panel.yml up -d mem0-webui
```

### ⚠️ **尝试方式：仅重启容器（可能不生效）**

**如果不想重建，可以尝试**：

```bash
# 1. 修改 docker-compose.1panel.yml 中的环境变量
# 2. 重启容器
docker-compose -f docker-compose.1panel.yml restart mem0-webui

# 3. 检查日志，看 entrypoint.sh 是否执行
docker logs mem0-webui | grep "Done replacing"

# 4. 验证是否生效（打开浏览器检查网络请求）
```

**如果重启后不生效**，说明 `entrypoint.sh` 的替换机制不适用于这个场景，需要重新构建。

## 环境变量对比

### NEXT_PUBLIC_API_URL

| 配置方式 | 是否需要重建 | 可靠性 | 说明 |
|---------|------------|--------|------|
| **构建时 ENV**（Dockerfile） | ✅ 需要 | ⭐⭐⭐⭐⭐ | 最可靠 |
| **运行时 ENV**（docker-compose） | ⚠️ 可能不需要 | ⭐⭐⭐ | 依赖 entrypoint.sh |

### NEXT_PUBLIC_USER_ID

| 配置方式 | 是否需要重建 | 可靠性 | 说明 |
|---------|------------|--------|------|
| **构建时 ENV**（Dockerfile） | ✅ 需要 | ⭐⭐⭐⭐⭐ | 最可靠 |
| **运行时 ENV**（docker-compose） | ⚠️ 可能不需要 | ⭐⭐⭐ | 依赖 entrypoint.sh |

## 最佳实践

### 方案 1：构建时配置（推荐用于生产环境）

**webui.Dockerfile**：
```dockerfile
# 构建时设置环境变量
ENV NEXT_PUBLIC_API_URL=http://mem0-api:8000
ENV NEXT_PUBLIC_USER_ID=admin

# 构建应用
RUN pnpm build
```

**优点**：
- ✅ 最可靠，值直接嵌入构建产物
- ✅ 不依赖运行时替换
- ✅ 符合 Next.js 标准做法

**缺点**：
- ❌ 修改需要重新构建镜像

### 方案 2：运行时配置（用于开发/测试）

**docker-compose.1panel.yml**：
```yaml
mem0-webui:
  environment:
    NEXT_PUBLIC_API_URL: http://mem0-api:8000
    NEXT_PUBLIC_USER_ID: admin
```

**优点**：
- ✅ 灵活，易于修改
- ✅ 无需重新构建（理论上）

**缺点**：
- ⚠️ 依赖 entrypoint.sh 的替换机制
- ⚠️ 可能不生效，需要重新构建

### 方案 3：混合方式（推荐）

**构建时设置默认值，运行时可以覆盖**：

```dockerfile
# webui.Dockerfile - 设置默认值
ENV NEXT_PUBLIC_API_URL=http://192.168.66.11:8888
ENV NEXT_PUBLIC_USER_ID=user
```

```yaml
# docker-compose.1panel.yml - 运行时覆盖（如果 entrypoint.sh 支持）
environment:
  NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://mem0-api:8000}
  NEXT_PUBLIC_USER_ID: ${NEXT_PUBLIC_USER_ID:-user}
```

## 验证方法

### 验证 1：检查环境变量

```bash
docker exec mem0-webui env | grep NEXT_PUBLIC
```

### 验证 2：检查 entrypoint.sh 是否执行

```bash
docker logs mem0-webui | grep "Done replacing"
```

### 验证 3：检查构建产物中的值

```bash
# 检查构建产物中是否包含 API URL
docker exec mem0-webui find .next -name "*.js" -exec grep -l "api.*url\|API.*URL" {} \; | head -3

# 查看具体内容
docker exec mem0-webui cat .next/standalone/.next/static/chunks/*.js | grep -i "http.*8888\|http.*8000" | head -3
```

### 验证 4：浏览器检查

1. 打开 WebUI
2. 打开浏览器开发者工具（F12）
3. 查看 Network 标签
4. 检查 API 请求的 URL 是否正确

## 故障排查

### 问题 1：修改环境变量后不生效

**可能原因**：
1. `entrypoint.sh` 替换失败（构建产物中没有变量名字符串）
2. 环境变量格式不正确
3. 容器缓存问题

**解决方法**：
```bash
# 1. 检查环境变量
docker exec mem0-webui env | grep NEXT_PUBLIC

# 2. 检查 entrypoint.sh 日志
docker logs mem0-webui | grep -i "replacing\|env"

# 3. 如果替换失败，重新构建镜像
cd /data/build/CozyMem0/deployment/mem0
./build-webui.sh
docker-compose -f docker-compose.1panel.yml up -d mem0-webui
```

### 问题 2：entrypoint.sh 替换不准确

**原因**：`sed` 替换可能替换了不应该替换的内容

**解决方法**：重新构建镜像，使用构建时环境变量

## 总结

### ✅ **最终建议**

1. **修改 `NEXT_PUBLIC_API_URL` 后，建议重新构建镜像**（最可靠）
2. **如果时间紧急，可以先尝试重启容器**（可能不生效）
3. **如果重启不生效，必须重新构建**

### 📝 **快速参考**

```bash
# 方式 1：重新构建（推荐）
cd /data/build/CozyMem0/deployment/mem0
./build-webui.sh
docker-compose -f docker-compose.1panel.yml up -d mem0-webui

# 方式 2：仅重启（可能不生效）
docker-compose -f docker-compose.1panel.yml restart mem0-webui
docker logs mem0-webui | grep "Done replacing"  # 检查是否执行
```

## 参考

- [Next.js 环境变量文档](https://nextjs.org/docs/basic-features/environment-variables)
- [entrypoint.sh](../projects/mem0/openmemory/ui/entrypoint.sh)
- [webui.Dockerfile](../webui.Dockerfile)
