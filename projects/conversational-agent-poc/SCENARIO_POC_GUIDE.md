# 场景化 POC 快速启动指南

## 📋 当前状态

✅ **数据已准备就绪**

| 系统 | 状态 | 说明 |
|------|------|------|
| **Mem0** | ✅ 已清空 | 可以添加新场景数据 |
| **Memobase** | ⚠️ 有旧数据残留 | 建议使用新用户ID |
| **Cognee** | ✅ 知识库完整 | kb_psyc + kb_tech |

## 🎯 推荐方案：使用新用户 ID

为避免旧数据干扰，**强烈建议为每个场景使用新的用户 ID**。

## 📝 场景配置

### 场景1：心理咨询助手

```python
PSYCHOLOGY_SCENARIO = {
    "user_id": "psyc_user_001",
    "session_id": "psyc_session_001",
    "dataset": "kb_psyc",
    "description": "为有心理压力的用户提供咨询服务"
}
```

**用户画像**:
- 姓名：李四
- 年龄：28岁
- 职业：公司白领
- 困扰：工作压力大、焦虑情绪

**示例对话**:
1. "最近工作压力很大，经常失眠，该怎么办？"
2. "我总是很焦虑，担心工作做不好"
3. "如何平衡工作和生活？"

### 场景2：技术支持助手

```python
TECH_SCENARIO = {
    "user_id": "tech_user_001",
    "session_id": "tech_session_001",
    "dataset": "kb_tech",
    "description": "为开发者提供技术支持和编程帮助"
}
```

**用户画像**:
- 姓名：王五
- 职业：Python 开发工程师
- 技能：FastAPI、Django
- 需求：技术咨询、问题排查

**示例对话**:
1. "如何优化 FastAPI 的性能？"
2. "Python 中如何实现异步编程？"
3. "推荐一些机器学习的学习资源"

### 场景3：综合智能助手

```python
GENERAL_SCENARIO = {
    "user_id": "general_user_001",
    "session_id": "general_session_001",
    "dataset": ["kb_psyc", "kb_tech"],
    "description": "提供综合性帮助，覆盖多个领域"
}
```

**用户画像**:
- 姓名：赵六
- 职业：创业者
- 需求：技术咨询 + 压力管理

**示例对话**:
1. "创业压力很大，如何保持心理健康？"
2. "需要搭建一个 Web 应用，用什么技术栈好？"
3. "如何平衡技术学习和心理调节？"

## 🚀 快速开始

### 步骤1：创建场景数据准备脚本

```bash
cd /Users/zhangjun/CursorProjects/CozyMem0/projects/conversational-agent-poc

# 复制模板
cp prepare_test_data.py prepare_scenario_psyc.py
```

### 步骤2：修改配置

编辑 `prepare_scenario_psyc.py`，修改用户信息：

```python
# 修改用户ID（重要！）
TEST_USER_ID = "psyc_user_001"  # 新用户
TEST_SESSION_ID = "psyc_session_001"  # 新会话
DATASET_NAME = "kb_psyc"  # 使用心理学知识库

# 修改对话内容为场景相关
conversations = [
    {
        "messages": [
            {"role": "user", "content": "我叫李四，28岁，是一名公司白领"},
            {"role": "assistant", "content": "你好李四！"}
        ],
        "metadata": {"topic": "自我介绍"}
    },
    {
        "messages": [
            {"role": "user", "content": "最近工作压力很大，经常失眠，感觉很焦虑"},
            {"role": "assistant", "content": "我理解你的困扰，工作压力确实会影响睡眠和情绪..."}
        ],
        "metadata": {"topic": "压力管理"}
    },
    # 添加更多场景对话...
]
```

### 步骤3：准备场景数据

```bash
# 准备心理咨询场景数据
python3 prepare_scenario_psyc.py
```

### 步骤4：测试场景

```bash
# 使用 curl 测试
curl -X POST "http://localhost:8080/api/v1/test/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "psyc_user_001",
    "session_id": "psyc_session_001",
    "message": "我之前说过我的主要困扰是什么？",
    "dataset_names": ["kb_psyc"]
  }'

# 或使用 Python 脚本
python3 test_with_data.py
```

### 步骤5：验证三种记忆系统

检查返回的 context：

```json
{
  "context": {
    "user_profile": {
      "基本信息": {"姓名": "李四", "年龄": "28"},
      "工作": {"职称": "公司白领"},
      "困扰": {"压力": "工作压力大", "情绪": "焦虑"}
    },
    "session_memories": [
      {"content": "工作压力大", "type": "semantic"},
      {"content": "经常失眠", "type": "semantic"},
      {"content": "感觉焦虑", "type": "semantic"}
    ],
    "knowledge": [
      {"content": "压力管理的方法...", "source": "kb_psyc"}
    ]
  }
}
```

## 📊 场景对比测试

### 测试矩阵

| 场景 | 用户ID | 知识库 | 测试点 |
|------|--------|--------|--------|
| 心理咨询 | psyc_user_001 | kb_psyc | 压力管理、情绪调节 |
| 技术支持 | tech_user_001 | kb_tech | 编程问题、技术选型 |
| 综合助手 | general_user_001 | kb_psyc + kb_tech | 跨领域问题 |

### 验证清单

对每个场景验证：

- [ ] Memobase 用户画像是否正确提取？
- [ ] Mem0 会话记忆是否准确保存？
- [ ] Cognee 知识检索是否返回相关知识？
- [ ] AI 响应是否个性化且准确？

## 💡 最佳实践

### 1. 为每个场景使用独立用户

```python
# ✅ 推荐
psyc_user = "psyc_user_001"
tech_user = "tech_user_001"

# ❌ 不推荐（会混淆数据）
user = "test_user_001"  # 所有场景用同一个
```

### 2. 设计真实的对话流程

```python
# ✅ 好的对话设计
conversations = [
    # 1. 建立信任
    {"user": "你好，我想咨询一些问题", "assistant": "..."},
    # 2. 了解背景
    {"user": "我是...", "assistant": "..."},
    # 3. 提出问题
    {"user": "我的困扰是...", "assistant": "..."},
    # 4. 深入讨论
    {"user": "具体来说...", "assistant": "..."},
]
```

### 3. 准备足够的测试数据

- **最少**: 3-5 组对话
- **推荐**: 8-10 组对话
- **完整**: 15+ 组对话

### 4. 使用有意义的元数据

```python
metadata = {
    "topic": "压力管理",
    "timestamp": "2024-12-18T16:00:00",
    "scenario": "psychology",
    "importance": "high"
}
```

## 🔧 调试技巧

### 查看详细日志

```bash
# 设置日志级别为 DEBUG
export LOG_LEVEL=DEBUG
python3 -m src.main
```

### 单独测试各个系统

```python
# 测试 Memobase
python3 test_memobase_profile.py

# 测试 Mem0
python3 test_mem0_client.py

# 测试 Cognee
# 使用 curl 或浏览器访问 Swagger
open http://192.168.66.11:8000/docs
```

### 验证数据准备

```bash
# 运行验证脚本
python3 verify_cleanup.py

# 检查特定用户
python3 -c "
from memobase import MemoBaseClient
import uuid
client = MemoBaseClient('http://192.168.66.11:8019', 'secret')
user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'psyc_user_001'))
user = client.get_user(user_id)
print(user.profile(max_token_size=500))
"
```

## 📚 示例场景脚本

### 心理咨询场景完整示例

见文件：`examples/psychology_scenario.py`（可以创建）

### 技术支持场景完整示例

见文件：`examples/tech_support_scenario.py`（可以创建）

## ⚠️ 注意事项

### 1. Memobase 旧数据

如果使用了旧的测试用户 `test_user_001`：
- ⚠️ 可能有残留的用户画像数据
- ✅ 使用新用户ID可以避免此问题

### 2. Mem0 处理时间

- Mem0 提取记忆需要一些时间（5-10秒）
- 建议在对话之间添加短暂延迟

### 3. Cognee 数据集

确保使用正确的数据集名称：
- `kb_psyc` - 心理学知识
- `kb_tech` - 技术知识

### 4. API 响应时间

- 首次对话可能较慢（需要初始化）
- 后续对话会更快

## 🎉 开始场景化 POC

现在一切准备就绪！选择一个场景开始：

```bash
# 场景1：心理咨询
python3 prepare_scenario_psyc.py

# 场景2：技术支持
python3 prepare_scenario_tech.py

# 场景3：综合助手
python3 prepare_scenario_general.py
```

祝测试顺利！🚀
