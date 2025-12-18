# Memobase 用户画像生成指南

## 问题说明

在使用Memobase时，可能会遇到获取用户画像返回空的情况。这是因为**用户画像需要从对话数据中提取生成**，而不是自动创建的。

## 解决方案

### 关键步骤

1. **插入对话数据** - 使用 `ChatBlob` 插入包含用户信息的对话
2. **刷新数据** - 使用 `user.flush(sync=True)` 同步处理数据
3. **获取画像** - 使用 `user.profile(need_json=True)` 获取JSON格式的画像

### 完整示例

```python
from memobase import MemoBaseClient, ChatBlob
import uuid

# 1. 初始化客户端
client = MemoBaseClient(
    project_url="http://192.168.66.11:8019",
    api_key="secret"
)

# 2. 创建或获取用户
user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "test_user_001"))
user = client.get_or_create_user(user_id)

# 3. 插入包含用户信息的对话数据
messages = [
    {"role": "user", "content": "你好，我是张三，今年28岁，是一名软件工程师，在北京工作。"},
    {"role": "assistant", "content": "很高兴认识你，张三！作为一名软件工程师，你的工作一定很有趣。"}
]

blob = ChatBlob(messages=messages)
user.insert(blob)

# 4. 刷新数据（同步处理，触发画像生成）
user.flush(sync=True)  # ⚠️ 关键：必须使用 sync=True

# 5. 获取生成的画像
profile = user.profile(need_json=True)  # ⚠️ 关键：使用 need_json=True
print(profile)
```

## 测试脚本

运行测试脚本：

```bash
cd projects/conversational-agent-poc
python3 test_memobase_profile.py
```

这个脚本会：
1. 创建测试用户
2. 插入5轮包含丰富信息的对话
3. 刷新数据生成画像
4. 显示生成的画像内容

## 生成的画像结构

成功生成的画像包含以下分类：

```json
{
  "基本信息": {
    "姓名": "张三",
    "年龄": "28"
  },
  "工作": {
    "职称": "软件工程师",
    "工作地点": "北京",
    "工作经验": "3年",
    "工作技能": "Python、JavaScript、Docker、Kubernetes",
    "参与项目": "后端开发，主要负责API设计和数据库优化"
  },
  "兴趣爱好": {
    "书籍": "技术书籍、科幻小说",
    "运动": "打篮球"
  },
  "联系信息": {
    "电话": "13800138000",
    "电子邮件": "zhangsan@example.com"
  },
  "心理特征": {
    "动力": "喜欢学习新技术，最近在研究机器学习和AI"
  }
}
```

## 常见问题

### Q1: 为什么获取的画像总是空的？

**A**: 可能的原因：
1. **没有插入对话数据** - 画像需要从对话中提取
2. **没有调用 flush()** - 数据需要刷新才能处理
3. **没有使用 sync=True** - 异步处理可能还没完成
4. **对话数据不够丰富** - 需要包含足够的用户信息

### Q2: 必须使用 sync=True 吗？

**A**: 是的，推荐使用 `sync=True`：
- `sync=False` (默认): 异步处理，可能需要等待
- `sync=True`: 同步处理，立即完成，确保数据已处理

### Q3: 如何获取JSON格式的画像？

**A**: 使用 `need_json=True` 参数：
```python
profile = user.profile(need_json=True)  # 返回字典
```

如果不使用 `need_json=True`，会返回 `UserProfile` 对象，需要手动转换：
```python
profile = user.profile()
if hasattr(profile, 'dict'):
    profile_dict = profile.dict()
elif hasattr(profile, 'model_dump'):
    profile_dict = profile.model_dump()
```

### Q4: 需要多少对话数据才能生成画像？

**A**: 没有固定要求，但建议：
- 至少包含用户的基本信息（姓名、职业等）
- 包含多个话题的信息（工作、兴趣、联系方式等）
- 对话要自然，包含足够的信息量

### Q5: 画像生成需要多长时间？

**A**: 
- 使用 `sync=True`: 通常几秒内完成
- 使用 `sync=False`: 可能需要更长时间，建议等待几秒后再获取

## 在POC项目中的使用

POC项目中的 `MemobaseClientWrapper` 已经实现了画像生成功能：

```python
from src.clients.memobase_client import MemobaseClientWrapper

client = MemobaseClientWrapper()

# 更新用户画像（自动插入数据并刷新）
messages = [
    {"role": "user", "content": "你好，我是张三，是一名软件工程师"},
    {"role": "assistant", "content": "很高兴认识你！"}
]
client.extract_and_update_profile("test_user_001", messages)

# 获取用户画像
profile = client.get_user_profile("test_user_001", max_token_size=500)
```

## 最佳实践

1. **插入对话后立即刷新**
   ```python
   user.insert(blob)
   user.flush(sync=True)  # 立即刷新
   ```

2. **使用 need_json=True 获取JSON格式**
   ```python
   profile = user.profile(need_json=True)
   ```

3. **等待处理完成**
   ```python
   user.flush(sync=True)
   import time
   time.sleep(2)  # 等待2秒确保处理完成
   profile = user.profile(need_json=True)
   ```

4. **包含丰富的用户信息**
   - 基本信息：姓名、年龄、性别
   - 工作信息：职业、公司、技能
   - 兴趣爱好：运动、阅读、音乐等
   - 联系方式：邮箱、电话
   - 个人特征：性格、偏好等

## 测试结果

运行 `test_memobase_profile.py` 后，成功生成的画像包含：

✅ **基本信息**: 姓名、年龄  
✅ **工作信息**: 职称、工作地点、工作经验、工作技能、参与项目  
✅ **兴趣爱好**: 书籍、运动  
✅ **联系信息**: 电话、电子邮件  
✅ **心理特征**: 动力、学习偏好  

## 参考

- **测试脚本**: `projects/conversational-agent-poc/test_memobase_profile.py`
- **客户端封装**: `projects/conversational-agent-poc/src/clients/memobase_client.py`
- **Memobase官方文档**: https://docs.memobase.io/api-reference/profiles/profile

---

**文档生成时间**: 2025-12-18
