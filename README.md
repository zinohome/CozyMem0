# CozyMem0

CozyMem0 项目用于研究和集成 Mem0 记忆管理系统。

## 项目结构

```
CozyMem0/
├── docs/                    # 文档目录
│   ├── research/            # 研究文档
│   └── poc/                 # POC 项目文档
├── projects/                # 项目目录
│   ├── mem0/                # Mem0 官方项目（本地开发用，不提交到 Git）
│   └── conversational-agent-poc/  # 对话智能体 POC
├── deployment/              # 部署配置
│   └── mem0/                # Mem0 部署配置
└── .cursorrules             # 项目规则
```

## 快速开始

### 1. 部署 Mem0 服务

参考 [部署指南](deployment/mem0/README.md)

### 2. 运行 POC 项目

参考 [对话智能体 POC](projects/conversational-agent-poc/README.md)

## 文档

- [项目分析](docs/research/projects-analysis.md)
- [性能分析](docs/research/performance-analysis.md)
- [POC 设计文档](docs/poc/conversational-agent-poc-design.md)

## 注意事项

- `projects/mem0/` 目录包含 Mem0 官方项目代码，不提交到 Git
- 使用 `projects/.gitkeep` 保持目录结构
- 参考 CozyCognee 的配置方式

