# WebUI 部署检查清单

## 前端可用性检查

### ✅ 已完成的工作

1. **适配代码已创建**
   - ✅ `useMemoriesApi.mem0.ts` - 记忆管理适配
   - ✅ `useAppsApi.mem0.ts` - 应用管理适配
   - ✅ `useFiltersApi.mem0.ts` - 过滤功能适配
   - ✅ `useStats.mem0.ts` - 统计功能适配
   - ✅ `useConfig.mem0.ts` - 配置管理适配

2. **Dockerfile 已配置**
   - ✅ `webui.Dockerfile` - WebUI 构建配置
   - ✅ 适配代码会自动复制到正确位置
   - ✅ 环境变量已配置

3. **Docker Compose 已配置**
   - ✅ `docker-compose.1panel.yml` - 1Panel 部署配置
   - ✅ `docker-compose.yml` - 本地开发配置
   - ✅ 网络配置正确
   - ✅ 环境变量已设置

4. **构建脚本已创建**
   - ✅ `build-webui.sh` - WebUI 镜像构建脚本

### ⚠️ 需要执行的操作

#### 1. 构建 WebUI 镜像

```bash
cd /data/build/CozyMem0/deployment/mem0
./build-webui.sh
```

**预计时间**：5-10 分钟（首次构建需要下载依赖）

**注意事项**：
- 确保有足够的磁盘空间（镜像约 500MB-1GB）
- 构建过程需要网络连接（下载 npm 包）
- 如果构建失败，检查 `projects/mem0/openmemory/ui/` 目录是否存在

#### 2. 启动 WebUI 服务

**使用 Docker Compose（推荐）**：
```bash
cd /data/build/CozyMem0/deployment/mem0
docker-compose -f docker-compose.1panel.yml up -d mem0-webui
```

**或使用 1Panel**：
- 在 1Panel 中导入 `docker-compose.1panel.yml`
- 启动 `mem0-webui` 服务

#### 3. 验证 WebUI 访问

```bash
# 检查服务状态
docker ps | grep mem0-webui

# 检查日志
docker logs mem0-webui

# 访问 WebUI
# 浏览器打开: http://192.168.66.11:3000
```

### 🔍 配置检查

#### API URL 配置

**当前配置**：
- Dockerfile 构建时：`NEXT_PUBLIC_API_URL=http://mem0-api:8000`（容器内部）
- Docker Compose 运行时：`NEXT_PUBLIC_API_URL=http://mem0-api:8000`（容器内部）

**如果需要从外部访问**：
如果 WebUI 需要从浏览器直接访问 API（而不是通过容器网络），需要修改：

```yaml
# docker-compose.1panel.yml
mem0-webui:
  environment:
    NEXT_PUBLIC_API_URL: http://192.168.66.11:8888  # 使用外部 IP
```

**注意**：`NEXT_PUBLIC_*` 环境变量会在构建时嵌入到前端代码中。如果修改了环境变量，需要重新构建镜像。

### 📋 功能检查清单

部署后，检查以下功能：

- [ ] **页面加载**
  - 访问 `http://192.168.66.11:3000` 能正常打开
  - 没有 JavaScript 错误

- [ ] **记忆列表**
  - 能显示记忆列表
  - 分页功能正常
  - 搜索功能正常

- [ ] **创建记忆**
  - 能创建新记忆
  - 创建后能立即显示在列表中

- [ ] **编辑记忆**
  - 能编辑记忆内容
  - 保存后更新正确

- [ ] **删除记忆**
  - 能删除记忆
  - 删除后从列表中移除

- [ ] **错误处理**
  - API 错误时显示友好提示
  - 网络错误时显示提示

### 🐛 常见问题

#### 1. WebUI 无法访问 API

**症状**：页面加载但无法获取数据

**检查**：
```bash
# 检查 API 是否可访问
curl http://192.168.66.11:8888/docs

# 检查 WebUI 日志
docker logs mem0-webui

# 检查网络连接
docker exec mem0-webui ping mem0-api
```

**解决方案**：
- 确保 `mem0-api` 服务正在运行
- 检查网络配置（都在 `1panel-network` 中）
- 检查环境变量 `NEXT_PUBLIC_API_URL`

#### 2. 构建失败

**常见原因**：
- `projects/mem0/openmemory/ui/` 目录不存在
- npm 包下载失败（网络问题）
- 磁盘空间不足

**解决方案**：
```bash
# 检查目录
ls -la projects/mem0/openmemory/ui/

# 清理构建缓存
docker builder prune

# 重新构建
./build-webui.sh
```

#### 3. 适配代码未生效

**检查**：
```bash
# 检查镜像中的适配代码
docker run --rm mem0-webui:latest cat /app/hooks/useMemoriesApi.ts | head -20
```

**解决方案**：
- 确保构建时使用了正确的 Dockerfile
- 检查适配代码文件是否存在

### 📊 当前状态

**API 服务**：✅ 已部署在 `192.168.66.11:8888`
- 响应格式已验证
- 适配代码已更新

**WebUI 服务**：⚠️ 需要构建和部署
- 适配代码已准备
- Dockerfile 已配置
- 需要执行构建和部署

### 🚀 快速部署命令

```bash
# 1. 构建 WebUI 镜像
cd /data/build/CozyMem0/deployment/mem0
./build-webui.sh

# 2. 启动 WebUI 服务
docker-compose -f docker-compose.1panel.yml up -d mem0-webui

# 3. 检查状态
docker ps | grep mem0-webui
docker logs mem0-webui

# 4. 访问 WebUI
# 浏览器打开: http://192.168.66.11:3000
```

### ✅ 总结

**前端代码状态**：✅ 已准备就绪
- 所有适配代码已创建
- 配置已正确设置
- 响应格式已适配

**部署状态**：⚠️ 需要执行构建和部署
- 需要构建 WebUI 镜像
- 需要启动 WebUI 服务
- 需要验证功能

**下一步**：执行构建和部署命令，然后访问 `http://192.168.66.11:3000` 测试功能。

