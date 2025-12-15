# 构建脚本同步说明

## 脚本概览

### 1. `build.sh` - 标准构建脚本

**位置**：`deployment/mem0/build.sh`

**功能**：
- 标准构建 Mem0 API 镜像
- 自动应用 CORS 和中文语言支持补丁（通过 Dockerfile）
- 验证补丁文件存在
- 验证补丁是否成功应用

**使用场景**：
- 日常构建
- 首次构建
- 不需要清理缓存的构建

**补丁支持**：
- ✅ CORS 补丁（`cors.patch`）
- ✅ 中文语言支持补丁（`chinese-language-support.patch`）

### 2. `rebuild-api.sh` - 强制重建脚本

**位置**：`deployment/mem0/scripts/rebuild-api.sh`

**功能**：
- 强制重新构建（清理缓存）
- 停止并删除旧容器
- 删除旧镜像
- 验证 `psycopg[pool]` 安装
- 验证 Dockerfile 系统依赖

**使用场景**：
- 依赖更新后需要清理缓存
- `psycopg` 相关问题
- 需要确保使用最新配置

**补丁支持**：
- ✅ CORS 补丁（通过 Dockerfile）
- ✅ 中文语言支持补丁（通过 Dockerfile）

### 3. `rebuild-with-cors.sh` - CORS 专用重建脚本

**位置**：`deployment/mem0/scripts/rebuild-with-cors.sh`

**功能**：
- 强制重新构建（清理缓存）
- 验证 CORS 补丁文件
- 验证补丁可以应用
- 详细验证 CORS 代码是否包含
- 验证 CORS 中间件配置

**使用场景**：
- CORS 相关问题
- 需要详细验证 CORS 补丁
- 调试 CORS 配置

**补丁支持**：
- ✅ CORS 补丁（详细验证）
- ✅ 中文语言支持补丁（通过 Dockerfile）

## 同步状态

### ✅ **所有脚本都已同步**

所有三个脚本都使用**同一个 Dockerfile**（`deployment/mem0/Dockerfile`），该 Dockerfile 包含：

```dockerfile
# 应用补丁（在构建时应用，不修改源文件）
COPY deployment/mem0/patches/cors.patch /tmp/cors.patch
COPY deployment/mem0/patches/chinese-language-support.patch /tmp/chinese-language-support.patch
RUN cd /app && \
    patch -p0 < /tmp/cors.patch || (echo "Warning: CORS patch failed, continuing..." && true) && \
    patch -p0 < /tmp/chinese-language-support.patch || (echo "Warning: Chinese language support patch failed, continuing..." && true)
```

因此，**所有脚本都会自动应用相同的补丁**。

## 脚本对比

| 特性 | `build.sh` | `rebuild-api.sh` | `rebuild-with-cors.sh` |
|------|-----------|------------------|----------------------|
| **补丁应用** | ✅ 自动（Dockerfile） | ✅ 自动（Dockerfile） | ✅ 自动（Dockerfile） |
| **清理缓存** | ❌ | ✅ | ✅ |
| **删除旧容器** | ❌ | ✅ | ✅ |
| **删除旧镜像** | ❌ | ✅ | ✅ |
| **验证补丁文件** | ✅ 基本验证 | ❌ | ✅ 详细验证 |
| **验证补丁应用** | ✅ 基本验证 | ❌ | ✅ 详细验证 |
| **验证 CORS 代码** | ✅ 基本验证 | ❌ | ✅ 详细验证 |
| **验证 psycopg** | ❌ | ✅ | ❌ |
| **构建日志** | 标准输出 | 标准输出 | 保存到文件 |

## 使用建议

### 日常构建

```bash
# 使用标准构建脚本
cd /data/build/CozyMem0/deployment/mem0
./build.sh
```

### 依赖更新后

```bash
# 使用强制重建脚本（清理缓存）
cd /data/build/CozyMem0/deployment/mem0
./scripts/rebuild-api.sh
```

### CORS 问题调试

```bash
# 使用 CORS 专用重建脚本（详细验证）
cd /data/build/CozyMem0/deployment/mem0
./scripts/rebuild-with-cors.sh
```

## 补丁文件位置

所有补丁文件位于：`deployment/mem0/patches/`

- `cors.patch` - CORS 支持补丁
- `chinese-language-support.patch` - 中文语言支持补丁
- `README.md` - 补丁说明文档

## 验证方法

### 验证补丁是否应用

```bash
# 方法 1：检查镜像中的 main.py
docker run --rm mem0-api:latest grep -q "app.add_middleware" /app/main.py && echo "✅ CORS 已应用"

# 方法 2：检查 CORS 模块
docker run --rm mem0-api:latest python -c "from fastapi.middleware.cors import CORSMiddleware; print('✅ CORS 模块可用')"

# 方法 3：检查中文语言支持
docker run --rm mem0-api:latest grep -q "CUSTOM_FACT_EXTRACTION_PROMPT" /app/main.py && echo "✅ 中文支持已应用"
```

### 验证补丁文件

```bash
# 检查补丁文件是否存在
ls -la deployment/mem0/patches/

# 应该看到：
# - cors.patch
# - chinese-language-support.patch
# - README.md
```

## 常见问题

### Q: `build.sh` 会应用 CORS 补丁吗？

**A**: ✅ **是的**。`build.sh` 使用 `Dockerfile`，而 `Dockerfile` 会自动应用所有补丁。

### Q: 三个脚本的补丁应用是否一致？

**A**: ✅ **完全一致**。所有脚本都使用同一个 `Dockerfile`，因此补丁应用完全相同。

### Q: 什么时候使用哪个脚本？

**A**: 
- **日常构建**：使用 `build.sh`
- **依赖更新**：使用 `rebuild-api.sh`
- **CORS 调试**：使用 `rebuild-with-cors.sh`

### Q: 补丁应用失败怎么办？

**A**: 
1. 检查补丁文件是否存在：`ls -la deployment/mem0/patches/`
2. 检查构建日志中的警告信息
3. 使用 `rebuild-with-cors.sh` 进行详细验证
4. 检查 `projects/mem0/server/main.py` 是否已被修改（补丁无法应用到已修改的文件）

## 总结

### ✅ **同步状态：已同步**

- 所有脚本使用同一个 `Dockerfile`
- `Dockerfile` 包含所有补丁应用逻辑
- 所有脚本都会自动应用相同的补丁
- 补丁应用逻辑集中在 `Dockerfile` 中，易于维护

### 📝 **建议**

1. **保持 Dockerfile 作为单一来源**：所有补丁应用逻辑都在 `Dockerfile` 中
2. **使用合适的脚本**：根据场景选择最合适的脚本
3. **定期验证**：构建后验证补丁是否成功应用

## 参考

- [Dockerfile](../deployment/mem0/Dockerfile)
- [build.sh](../deployment/mem0/build.sh)
- [rebuild-api.sh](../deployment/mem0/scripts/rebuild-api.sh)
- [rebuild-with-cors.sh](../deployment/mem0/scripts/rebuild-with-cors.sh)
- [补丁说明](../deployment/mem0/patches/README.md)

