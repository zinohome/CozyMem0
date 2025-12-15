# Mem0 部署文档

本目录包含 Mem0 API 和 WebUI 的完整部署文档。

## 📚 文档索引

### 部署指南
- [部署指南](./README.md) - 完整的部署说明（本文件）

### 配置文档
- [中文语言配置](./CHINESE_LANGUAGE_CONFIG.md) - 如何配置 Mem0 保持中文记忆

### 问题解决
- [CORS 修复指南](./CORS_FIX_GUIDE.md) - CORS 问题解决方案
- [记忆语言问题](./MEMORY_LANGUAGE_ISSUE.md) - 记忆被翻译为英文的问题分析
- [强制拉取指南](./FORCE_PULL_GUIDE.md) - Git 强制覆盖本地更改

### API 分析
- [API 对比分析](./API_COMPARISON_ANALYSIS.md) - OpenMemory API vs Mem0 REST API
- [API 响应分析](./API_RESPONSE_ANALYSIS.md) - API 响应格式分析

### WebUI 相关
- [WebUI 适配说明](./WEBUI_ADAPTATION.md) - WebUI 适配 Mem0 API 的说明
- [WebUI 部署清单](./WEBUI_DEPLOYMENT_CHECKLIST.md) - WebUI 部署检查清单
- [WebUI 验证计划](./WEBUI_VALIDATION_PLAN.md) - WebUI 验证步骤

## 🚀 快速开始

### 1. 构建镜像

```bash
cd deployment/mem0
./build.sh              # 构建 API 镜像
./build-webui.sh        # 构建 WebUI 镜像
```

### 2. 配置环境变量

在 `docker-compose.1panel.yml` 中配置：

```yaml
environment:
  OPENAI_API_KEY: your-key-here
  OPENAI_MODEL: gpt-4  # 使用支持中文的模型
  LLM_SYSTEM_PROMPT: "请保持记忆内容的原始语言，不要将中文翻译为英文。"
```

### 3. 启动服务

```bash
docker-compose -f docker-compose.1panel.yml up -d
```

## 📖 详细文档

请查看各个文档文件获取详细信息。
