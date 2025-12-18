# 青少年心理咨询场景化 POC 使用指南

## 📋 概述

本 POC 通过模拟心理咨询场景，对比验证三种记忆系统的效果：
- **Cognee (kb_psyc)**: 专业心理学知识库
- **Memobase**: 用户画像（个人信息、性格特点、困扰等）
- **Mem0**: 会话记忆（对话历史、咨询进展）

## 🎯 测试设计

### 用户设定
- **姓名**: 江小婉
- **年龄**: 15岁
- **学校**: 北京市某重点中学高一
- **性格**: 软弱、内向
- **困扰**: 学习压力大，与家人和同学沟通困难

### 三个会话场景
1. **会话1**: 初次咨询 - 建立信任关系（学业压力和焦虑）
2. **会话2**: 深入探索 - 处理核心问题（完美主义和自我接纳）
3. **会话3**: 巩固成长 - 社交技能提升（人际沟通）

每个会话10轮对话，共30轮。

### 三个测试组
| 测试组 | kb_psyc | Memobase | Mem0 | 说明 |
|--------|---------|----------|------|------|
| **对照组** | ❌ | ❌ | ❌ | 基础 LLM |
| **仅知识库组** | ✅ | ❌ | ❌ | 有专业知识 |
| **完整系统组** | ✅ | ✅ | ✅ | 三种记忆全开 |

## 🚀 快速开始

### 1. 确认代码已更新

核心代码修改已完成：
- ✅ `src/prompts/templates.py` - 添加心理咨询师 prompt
- ✅ `src/services/conversation_engine.py` - 支持角色参数
- ✅ `src/main.py` - API 接受 role 参数

### 2. 重启 POC 服务

```bash
# 如果服务正在运行，先停止（Ctrl+C）

# 重新启动
cd /Users/zhangjun/CursorProjects/CozyMem0/projects/conversational-agent-poc
./start_poc.sh
```

### 3. 准备测试数据

```bash
# 运行数据准备脚本
python3 prepare_psychology_poc.py

# 按提示输入 yes 确认
```

这将为完整系统组注入基础用户画像。

### 4. 运行自动化测试

```bash
# 运行测试（需要20-30分钟）
python3 run_psychology_poc.py
```

测试将自动进行：
- 3个测试组 × 3个会话 × 10轮对话 = 90次对话
- 结果保存在 `psychology_results/` 目录

### 5. 生成分析报告

```bash
# 分析测试结果
python3 analyze_psychology_results.py
```

将生成详细的 Markdown 对比报告。

## 📊 预期效果示例

### 会话2开场对比

**对照组**（无记忆）:
```
咨询师：你好，今天想聊些什么呢？
```

**仅知识库组**（有专业知识，无个人记忆）:
```
咨询师：你好，今天想聊些什么呢？作为心理咨询师，
我可以帮你处理学业压力、人际关系等青少年常见的困扰。
```

**完整系统组**（有知识+画像+记忆）:
```
咨询师：小婉你好，又见面了。上次我们聊到了你的学习压力，
特别是数学和物理让你感到焦虑。这周你尝试用画画来放松了吗？
感觉怎么样？
```

## 📁 文件结构

```
conversational-agent-poc/
├── psychology_sessions/          # 会话脚本
│   ├── session_1_initial_consultation.json
│   ├── session_2_deep_exploration.json
│   └── session_3_consolidation.json
├── psychology_results/            # 测试结果（自动生成）
│   ├── psychology_poc_results_*.json
│   └── psychology_poc_report_*.md
├── prepare_psychology_poc.py      # 数据准备脚本
├── run_psychology_poc.py          # 自动化测试脚本
├── analyze_psychology_results.py  # 结果分析脚本
└── PSYCHOLOGY_POC_README.md       # 本文档
```

## 🔍 测试指标

### 1. 专业性（知识库的作用）
- 是否使用心理学专业术语
- 是否引用认知行为疗法等技术
- 是否提供科学的应对策略

### 2. 个性化（用户画像的作用）
- 是否记住用户姓名、年龄、学校
- 是否记住用户的困扰和特点
- 回复是否体现对用户的了解

### 3. 连续性（会话记忆的作用）
- 跨会话时是否记得上次对话
- 是否追踪作业完成情况
- 是否体现咨询进展

## ⚠️ 注意事项

### 1. 测试时间
- 完整测试需要 20-30 分钟
- 每轮对话间隔 2 秒
- 会话间隔 5 秒

### 2. 服务要求
- POC 服务必须运行
- Cognee, Memobase, Mem0 服务必须可用
- 确保 OpenAI API 或兼容服务可用

### 3. 数据准备
- 完整系统组需要预先注入用户画像
- 对照组和仅知识库组使用新用户ID（自动为空）
- 确保 kb_psyc 知识库存在

### 4. 结果查看
- JSON 结果文件：完整的对话记录
- Markdown 报告：分析和对比
- 建议同时查看两个文件

## 🐛 故障排查

### 问题1：POC 服务未启动

```bash
# 检查服务状态
curl http://localhost:8080/health

# 如果失败，启动服务
./start_poc.sh
```

### 问题2：会话脚本找不到

```bash
# 检查文件是否存在
ls psychology_sessions/

# 应该看到3个 .json 文件
```

### 问题3：API 调用失败

- 检查 OpenAI API key 是否正确
- 检查网络连接
- 查看 POC 服务日志

### 问题4：Memobase 画像注入失败

- 检查 Memobase 服务是否运行
- 使用新用户ID（避免旧数据干扰）
- 查看 prepare 脚本的输出

## 📈 查看结果

### 1. 查看 JSON 结果

```bash
# 查找最新结果
ls -lt psychology_results/psychology_poc_results_*.json | head -1

# 查看结果
cat psychology_results/psychology_poc_results_20241218_HHMMSS.json | jq .
```

### 2. 查看 Markdown 报告

```bash
# 用文本编辑器打开
code psychology_results/psychology_poc_report_20241218_HHMMSS.md

# 或在终端查看
cat psychology_results/psychology_poc_report_20241218_HHMMSS.md
```

## 💡 下一步

1. **分析对比结果**
   - 对比三组的回复质量
   - 验证记忆系统的作用
   
2. **调整优化**
   - 根据结果优化 prompt
   - 调整知识库内容
   - 改进会话脚本

3. **扩展测试**
   - 增加更多会话
   - 测试其他场景
   - 引入人工评估

## 🎯 成功标准

✅ 测试成功的标志：
1. 三组测试全部完成（90轮对话）
2. 完整系统组在会话2/3中体现记忆连续性
3. 仅知识库组引用专业知识
4. 对照组与完整系统组有明显差异

## 📞 支持

如有问题，请检查：
1. 日志输出
2. API 响应
3. 服务状态

---

**祝测试顺利！** 🎉
