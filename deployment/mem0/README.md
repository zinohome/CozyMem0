# Mem0 部署目录

本目录包含 Mem0 API 和 WebUI 的部署相关文件。

## 快速开始

### 构建镜像

```bash
# 构建 API 镜像
./build.sh

# 构建 WebUI 镜像
./build-webui.sh
```

### 启动服务

```bash
# 1Panel 部署
docker-compose -f docker-compose.1panel.yml up -d

# 本地开发
docker-compose up -d
```

## 目录结构

```
deployment/mem0/
├── README.md                    # 本文件（快速参考）
├── Dockerfile                   # Mem0 API Dockerfile
├── webui.Dockerfile            # Mem0 WebUI Dockerfile
├── docker-compose.yml           # 本地开发配置
├── docker-compose.1panel.yml   # 1Panel 部署配置
├── build.sh                     # API 镜像构建脚本
├── build-webui.sh              # WebUI 镜像构建脚本
├── patches/                     # 代码补丁
│   ├── README.md
│   └── cors.patch              # CORS 支持补丁
├── webui-adapters/             # WebUI API 适配器
│   └── *.ts                    # TypeScript 适配器文件
├── webui-patches/              # WebUI 代码补丁
│   ├── README.md
│   └── *.patch                 # UI 修改补丁
└── scripts/                    # 工具脚本
    ├── test-api.sh
    ├── test-api-response.sh
    ├── test-memory-language.sh
    ├── verify-patch.sh
    ├── rebuild-api.sh
    ├── rebuild-with-cors.sh
    └── force-pull.sh
```

## 详细文档

所有详细文档已移至 `docs/deployment/mem0/` 目录：

- [部署指南](docs/deployment/mem0/README.md)
- [API 对比分析](docs/deployment/mem0/API_COMPARISON_ANALYSIS.md)
- [CORS 修复指南](docs/deployment/mem0/CORS_FIX_GUIDE.md)
- [记忆语言问题](docs/deployment/mem0/MEMORY_LANGUAGE_ISSUE.md)
- [WebUI 适配说明](docs/deployment/mem0/WEBUI_ADAPTATION.md)
- [WebUI 部署清单](docs/deployment/mem0/WEBUI_DEPLOYMENT_CHECKLIST.md)
- [强制拉取指南](docs/deployment/mem0/FORCE_PULL_GUIDE.md)

## 常用命令

```bash
# 测试 API
./scripts/test-api.sh

# 验证补丁
./scripts/verify-patch.sh

# 强制重新构建（应用 CORS）
./scripts/rebuild-with-cors.sh
```

