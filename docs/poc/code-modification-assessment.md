# 心理咨询 POC 代码改动评估

## 🎯 结论：几乎不需要改动核心代码！

### ✅ 现有架构已经支持所需功能

当前 `conversational-agent-poc` 项目的架构完全支持这个 POC：

```
✅ 支持 Cognee 知识库 (kb_psyc)
✅ 支持 Memobase 用户画像
✅ 支持 Mem0 会话记忆
✅ 支持自定义 system prompt
✅ 支持多用户、多会话
✅ 支持知识库选择控制
```

## 📊 改动程度评估

### 需要改动的代码（最小化改动）

#### 1. 修改 Prompt 模板（唯一必需的代码改动）

**文件**: `src/prompts/templates.py`

**改动**: 添加心理咨询师专用的 system prompt

```python
# 改动前
def get_system_prompt() -> str:
    """获取系统 Prompt"""
    return """你是一个智能助手，能够：
    1. 基于用户画像提供个性化回答
    2. 利用专业知识库回答专业问题
    3. 记住并参考历史对话内容
    4. 提供友好、专业的服务
    
    请根据用户画像、相关记忆和专业知识，提供准确、有用的回答。"""

# 改动后（添加参数支持）
def get_system_prompt(role: str = "default") -> str:
    """获取系统 Prompt"""
    if role == "psychology_counselor":
        return PSYCHOLOGY_COUNSELOR_PROMPT
    else:
        return DEFAULT_PROMPT
```

**改动行数**: 约 50-100 行（添加心理咨询师 prompt）

**影响范围**: 仅影响 system prompt，不影响其他逻辑

#### 2. 可选：添加角色配置（可选改动）

**文件**: `src/config.py`

**改动**: 添加角色配置选项

```python
class Settings(BaseSettings):
    # 现有配置...
    
    # 新增：角色配置（可选）
    counselor_role: str = "default"  # 或 "psychology_counselor"
```

**改动行数**: 1-2 行

**影响范围**: 无，完全向后兼容

#### 3. 可选：在 conversation_engine.py 中传递角色（可选）

**文件**: `src/services/conversation_engine.py`

**改动**: 传递角色参数到 prompt

```python
# 在 process_message 方法中
response = await self.openai.chat.completions.create(
    model=settings.openai_model,
    messages=[
        {"role": "system", "content": get_system_prompt("psychology_counselor")},  # 添加角色参数
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)
```

**改动行数**: 1 行

**影响范围**: 无，完全向后兼容

### 不需要改动的代码（0 行改动）

以下功能无需任何代码改动，通过配置和数据控制：

#### ✅ 三种记忆系统的开关控制

**方法**: 通过 API 参数控制

```python
# 对照组：不使用任何记忆
{
    "user_id": "xiaowan_baseline",
    "dataset_names": [],  # 不使用知识库
    # Memobase/Mem0 通过使用新用户ID自动为空
}

# 仅知识库组：只使用 kb_psyc
{
    "user_id": "xiaowan_kb_only", 
    "dataset_names": ["kb_psyc"],  # 使用知识库
    # 新用户ID，Memobase/Mem0 为空
}

# 完整系统组：使用全部功能
{
    "user_id": "xiaowan_full",
    "dataset_names": ["kb_psyc"],
    # 使用有历史数据的用户ID
}
```

**代码改动**: 0 行

#### ✅ 用户画像注入

**方法**: 使用 Memobase SDK 注入基础画像

```python
# 使用现有的 memobase client
from memobase import MemoBaseClient, ChatBlob

# 注入基础画像（已有功能）
blob = ChatBlob(messages=[...])
user.insert(blob)
user.flush()
```

**代码改动**: 0 行（使用现有功能）

#### ✅ 会话记忆管理

**方法**: 使用现有的 Mem0 API

```python
# 保存会话（已有功能）
await mem0_client.save_conversation(
    user_id=user_id,
    session_id=session_id,
    messages=[...]
)

# 检索记忆（已有功能）
memories = await mem0_client.get_conversation_context(
    user_id=user_id,
    session_id=session_id,
    query=message
)
```

**代码改动**: 0 行（使用现有功能）

## 📝 改动总结

| 改动类型 | 文件 | 改动内容 | 行数 | 必需性 |
|---------|------|---------|------|--------|
| **代码改动** | `templates.py` | 添加心理咨询师 prompt | ~50-100 | ✅ 必需 |
| **代码改动** | `config.py` | 添加角色配置 | ~2 | ⚪ 可选 |
| **代码改动** | `conversation_engine.py` | 传递角色参数 | ~1 | ⚪ 可选 |
| **新增脚本** | `prepare_psychology_*.py` | 数据准备脚本 | ~200 | ✅ 必需 |
| **新增脚本** | `run_psychology_poc.py` | 自动化测试 | ~300 | ✅ 必需 |
| **新增文档** | 会话脚本 JSON | 对话内容 | ~1000 | ✅ 必需 |

**核心代码改动总计**: 约 50-100 行（主要是添加 prompt）  
**新增脚本和文档**: 约 1500 行（不影响现有代码）

## 🎯 实施策略：最小侵入原则

### 方案 A：零代码改动（推荐）

**完全不改动现有代码**，通过以下方式实现：

1. **System Prompt**: 在测试脚本中动态注入
   ```python
   # 在调用 API 前，通过环境变量或配置注入
   import os
   os.environ['COUNSELOR_SYSTEM_PROMPT'] = psychology_prompt
   ```

2. **角色控制**: 通过用户 ID 和数据集参数控制
   ```python
   # 不同的用户ID = 不同的测试组
   baseline_user = "xiaowan_baseline"
   kb_only_user = "xiaowan_kb_only"
   full_user = "xiaowan_full"
   ```

3. **测试执行**: 完全通过外部脚本控制
   ```python
   # 调用现有 API，不改动内部代码
   response = await client.post("/api/v1/test/conversation", json={...})
   ```

**优点**:
- ✅ 零风险，不影响现有功能
- ✅ 易于回滚
- ✅ 不需要重启服务

**缺点**:
- ⚠️ System prompt 可能无法完全自定义

### 方案 B：最小改动（推荐）

**只改动 templates.py**，添加心理咨询师 prompt

```python
# templates.py
PSYCHOLOGY_COUNSELOR_PROMPT = """
你是一位专业的青少年心理咨询师...
（完整的心理咨询师提示词）
"""

def get_system_prompt(role: str = "default") -> str:
    if role == "psychology_counselor":
        return PSYCHOLOGY_COUNSELOR_PROMPT
    return DEFAULT_PROMPT
```

然后在环境变量中设置角色：
```bash
export COUNSELOR_ROLE="psychology_counselor"
```

**优点**:
- ✅ 改动最小（50-100 行）
- ✅ 完全控制 prompt
- ✅ 向后兼容

**缺点**:
- ⚠️ 需要重启服务

## 🚀 推荐实施方案

### 第一阶段：零改动验证（1 小时）

1. 使用现有代码测试基本功能
2. 通过脚本注入数据和控制参数
3. 验证三种记忆系统是否正常工作

### 第二阶段：最小改动优化（30 分钟）

1. 只修改 `templates.py` 添加心理咨询师 prompt
2. 重启服务
3. 执行完整测试

### 第三阶段：结果分析（1 小时）

1. 运行三组对比测试
2. 收集数据
3. 生成分析报告

## 📊 改动风险评估

| 风险项 | 风险等级 | 影响范围 | 缓解措施 |
|--------|---------|---------|---------|
| 修改 prompt 模板 | 🟢 低 | 仅影响回复内容 | 保留原 prompt 作为默认值 |
| 添加配置项 | 🟢 低 | 完全向后兼容 | 使用默认值 |
| 新增测试脚本 | 🟢 低 | 不影响现有代码 | 独立文件 |

**总体风险**: 🟢 **极低**

## ✅ 结论

### 核心代码改动：极少（50-100 行）

- ✅ 只需修改 `templates.py` 添加心理咨询师 prompt
- ✅ 可选修改 `config.py` 和 `conversation_engine.py`（2-3 行）
- ✅ 所有改动都是**增加式**，不破坏现有功能

### 主要工作量：数据准备和测试脚本（新增文件）

- 📝 准备 3 个会话场景的对话脚本（~1000 行 JSON）
- 📝 编写数据准备脚本（~200 行 Python）
- 📝 编写自动化测试脚本（~300 行 Python）
- 📝 编写分析报告生成器（~200 行 Python）

### 工作量分布

```
代码改动:     10%  (50-100 行)
数据准备:     40%  (1000 行对话脚本)
测试脚本:     30%  (500 行自动化脚本)
文档报告:     20%  (分析和文档)
```

### 时间估算

```
代码修改:     30 分钟
数据准备:     2 小时
脚本开发:     2 小时
测试执行:     1 小时
报告生成:     1 小时
-------------------
总计:        6-7 小时
```

## 🎯 建议

**推荐采用"最小改动"方案**：

1. ✅ 只修改 `templates.py`（50-100 行）
2. ✅ 其他全部通过脚本和数据控制
3. ✅ 保持现有代码的完整性和稳定性

这样既能实现所有 POC 需求，又能保持代码的简洁和可维护性。

---

**准备好了吗？我可以立即开始实施！** 🚀
