# Mem0 中文语言配置指南

## 问题描述

Mem0 使用 LLM 来处理和总结记忆内容，如果配置的 LLM 是英文模型，可能会将中文记忆翻译为英文。

**示例：**
- 输入：`我是湖北人`
- 存储：`User is from Hubei`

## 解决方案

### 方案 1：通过环境变量配置（推荐）

在 `docker-compose.1panel.yml` 或 `docker-compose.yml` 中配置环境变量：

```yaml
environment:
  # 使用支持中文的模型
  OPENAI_MODEL: gpt-4  # 或 gpt-4-turbo、gpt-3.5-turbo
  
  # 配置自定义事实提取提示词，要求保持原始语言
  CUSTOM_FACT_EXTRACTION_PROMPT: "请保持记忆内容的原始语言，不要将中文翻译为英文。如果输入是中文，输出也应该是中文。"
```

### 方案 2：使用 .env 文件

创建 `.env` 文件：

```env
OPENAI_MODEL=gpt-4
CUSTOM_FACT_EXTRACTION_PROMPT=请保持记忆内容的原始语言，不要将中文翻译为英文。如果输入是中文，输出也应该是中文。
```

### 方案 3：在 1Panel 中配置

在 1Panel 的应用配置中，添加环境变量：

- `OPENAI_MODEL`: `gpt-4`
- `CUSTOM_FACT_EXTRACTION_PROMPT`: `请保持记忆内容的原始语言，不要将中文翻译为英文。如果输入是中文，输出也应该是中文。`

## 环境变量说明

### OPENAI_MODEL

配置使用的 OpenAI 模型。

**推荐值：**
- `gpt-4` - 支持中文，性能好
- `gpt-4-turbo` - 支持中文，性能更好
- `gpt-3.5-turbo` - 支持中文，成本更低
- `gpt-4.1-nano-2025-04-14` - 默认值，可能不支持中文

### CUSTOM_FACT_EXTRACTION_PROMPT

配置自定义事实提取提示词，用于控制记忆处理行为。这是 Mem0 的标准配置项。

**中文保持提示词：**
```
请保持记忆内容的原始语言，不要将中文翻译为英文。如果输入是中文，输出也应该是中文。
```

**更详细的提示词：**
```
你是一个记忆提取系统。请从用户输入中提取关键信息并存储为记忆。
重要要求：
1. 保持记忆内容的原始语言，不要翻译
2. 如果输入是中文，输出也必须是中文
3. 只提取关键信息，不要添加额外的解释
4. 保持简洁和准确
```

## 配置步骤

### 1. 修改 docker-compose 文件

编辑 `deployment/mem0/docker-compose.1panel.yml`：

```yaml
environment:
  OPENAI_MODEL: gpt-4
  CUSTOM_FACT_EXTRACTION_PROMPT: "请保持记忆内容的原始语言，不要将中文翻译为英文。如果输入是中文，输出也应该是中文。"
```

### 2. 重新构建镜像（如果修改了代码）

如果修改了 patch 文件，需要重新构建：

```bash
cd /data/build/CozyMem0/deployment/mem0
./build.sh
```

### 3. 重启服务

```bash
docker-compose -f docker-compose.1panel.yml restart mem0-api
```

### 4. 验证配置

测试创建中文记忆：

```bash
curl -X POST "http://192.168.66.11:8888/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "我是湖北人"}
    ],
    "user_id": "test_user"
  }'

# 查看记忆
curl "http://192.168.66.11:8888/memories?user_id=test_user" | jq .
```

如果记忆内容保持为中文，说明配置成功。

## 技术实现

### Patch 文件

通过 `deployment/mem0/patches/chinese-language-support.patch` 修改 `main.py`：

1. 添加环境变量读取：
   - `OPENAI_MODEL` - 模型名称
   - `CUSTOM_FACT_EXTRACTION_PROMPT` - 自定义事实提取提示词

2. 修改 DEFAULT_CONFIG：
   - 使用环境变量中的模型名称
   - 如果设置了自定义提示词，添加到配置中（使用 Mem0 标准的 `custom_fact_extraction_prompt` 配置项）

### 代码变更

```python
# 读取环境变量
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-nano-2025-04-14")
CUSTOM_FACT_EXTRACTION_PROMPT = os.environ.get("CUSTOM_FACT_EXTRACTION_PROMPT", "")

# 配置 LLM
"llm": {
    "provider": "openai",
    "config": {
        "api_key": OPENAI_API_KEY,
        "temperature": 0.2,
        "model": OPENAI_MODEL
    }
}

# 配置自定义提示词（如果设置了）
**({"custom_fact_extraction_prompt": CUSTOM_FACT_EXTRACTION_PROMPT} if CUSTOM_FACT_EXTRACTION_PROMPT else {})
```

## 注意事项

1. **模型选择**：确保选择的模型支持中文
2. **提示词效果**：系统提示词的效果取决于 LLM 模型的能力
3. **成本考虑**：`gpt-4` 比 `gpt-4.1-nano` 成本更高
4. **重新构建**：修改 patch 后需要重新构建镜像
5. **重启服务**：修改环境变量后需要重启服务

## 故障排查

### 问题 1：配置后仍然翻译为英文

**可能原因：**
- 模型不支持中文
- 系统提示词未生效
- 服务未重启

**解决方法：**
1. 检查使用的模型是否支持中文
2. 查看服务日志确认配置是否加载
3. 重启服务

### 问题 2：自定义提示词不生效

**可能原因：**
- 提示词格式不正确
- 模型不支持中文

**解决方法：**
1. 检查提示词是否正确设置
2. 确保使用的模型支持中文（如 `gpt-4`）
3. 查看服务日志确认配置是否加载

## 参考

- [Mem0 配置文档](https://docs.mem0.ai)
- [OpenAI 模型列表](https://platform.openai.com/docs/models)
- [记忆语言问题分析](./MEMORY_LANGUAGE_ISSUE.md)

