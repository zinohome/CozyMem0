# Mem0 WebUI 适配说明

## 概述

Mem0 WebUI 是基于 OpenMemory UI 剪裁适配的版本，将 OpenMemory UI 的接口调用适配到 Mem0 REST API。

## 适配方案

### 1. 接口差异分析

**OpenMemory API** vs **Mem0 API**：

| 功能 | OpenMemory API | Mem0 API | 适配方案 |
|------|---------------|----------|---------|
| 获取记忆列表 | `POST /api/v1/memories/filter` (分页、过滤) | `GET /memories` (简单列表) | 前端实现分页和过滤 |
| 创建记忆 | `POST /api/v1/memories/` (text) | `POST /memories` (messages) | 转换格式 |
| 删除记忆 | `DELETE /api/v1/memories/` (批量) | `DELETE /memories/{id}` (单个) | 循环删除 |
| 更新记忆 | `PUT /api/v1/memories/{id}` | `PUT /memories/{id}` | 格式转换 |
| 搜索记忆 | `POST /api/v1/memories/filter` | `POST /search` | 使用搜索接口 |
| 应用管理 | `GET /api/v1/apps/` | ❌ 不支持 | 返回默认应用 |
| 分类管理 | `GET /api/v1/memories/categories` | ❌ 不支持 | 返回空列表 |
| 访问日志 | `GET /api/v1/memories/{id}/access-log` | ❌ 不支持 | 返回空数组 |
| 相关记忆 | `GET /api/v1/memories/{id}/related` | ❌ 不支持 | 使用搜索代替 |
| 状态管理 | `POST /api/v1/memories/actions/pause` | ❌ 不支持 | 仅支持删除 |
| 统计 | `GET /api/v1/stats` | ❌ 不支持 | 通过获取所有记忆计算 |
| 配置 | `GET/PUT /api/v1/config` | `POST /configure` | 格式转换 |

### 2. 适配文件

所有适配文件位于 `deployment/mem0/webui-adapters/`：

- `useMemoriesApi.mem0.ts` - 记忆管理适配
- `useAppsApi.mem0.ts` - 应用管理适配（简化）
- `useFiltersApi.mem0.ts` - 过滤适配（简化）
- `useStats.mem0.ts` - 统计适配
- `useConfig.mem0.ts` - 配置适配

### 3. 构建过程

1. **复制 OpenMemory UI 源代码**到构建环境
2. **替换 hooks 文件**：将适配文件复制到 `hooks/` 目录，覆盖原始文件
3. **构建 Next.js 应用**
4. **生成 Docker 镜像**

## 功能支持情况

### ✅ 完全支持

- 记忆的创建、查看、更新、删除
- 记忆搜索
- 前端分页
- 前端过滤（应用、分类）
- 前端排序

### ⚠️ 部分支持

- **应用管理**：显示默认的 "Mem0" 应用，不支持多应用
- **分类管理**：返回空列表，分类过滤功能不可用
- **状态管理**：不支持暂停/归档，只有删除功能
- **配置管理**：部分配置功能可能受限

### ❌ 不支持

- **访问日志**：Mem0 API 不支持访问日志记录
- **相关记忆**：使用搜索功能代替
- **应用详情**：不支持应用级别的统计和管理

## 使用方法

### 构建镜像

```bash
./build-webui.sh
```

### 运行服务

WebUI 服务已包含在 `docker-compose.yml` 和 `docker-compose.1panel.yml` 中：

```bash
# 1Panel 部署
docker-compose -f docker-compose.1panel.yml up -d

# 本地开发部署
docker-compose up -d
```

### 访问 WebUI

- WebUI: http://localhost:3000
- API: http://localhost:8888

## 环境变量

- `NEXT_PUBLIC_API_URL`: Mem0 API 地址（默认: `http://mem0-api:8000`）

在 docker-compose 中，WebUI 通过容器名 `mem0-api` 访问 API。

## 注意事项

1. **数据格式差异**：Mem0 API 使用 `messages` 数组创建记忆，而 OpenMemory 使用 `text` 字符串
2. **分页实现**：分页在前端实现，可能在大数据量时性能较差
3. **过滤功能**：过滤在前端实现，不支持服务端过滤
4. **功能限制**：部分 OpenMemory UI 的功能在 Mem0 API 中不可用

## 未来改进

1. 在 Mem0 API 中添加分页支持
2. 在 Mem0 API 中添加过滤支持
3. 优化前端分页和过滤性能
4. 添加更多 Mem0 API 特有的功能

