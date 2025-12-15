# JSON Prompt Fix - OpenAI API 错误修复

## 问题描述

当使用自定义 `custom_fact_extraction_prompt` 时，如果提示词中没有包含 "json" 这个词，OpenAI API 会报错：

```
openai.BadRequestError: Error code: 400 - {'error': {'message': "'messages' must contain the word 'json' in some form, to use 'response_format' of type 'json_object'.", 'type': 'invalid_request_error', 'param': 'messages', 'code': None}}
```

## 问题原因

Mem0 在调用 OpenAI API 时使用了 `response_format={"type": "json_object"}`，这是为了确保 LLM 返回 JSON 格式的响应。但是 OpenAI API 有一个要求：**当使用 `response_format: json_object` 时，提示词中必须包含 "json" 这个词**。

如果自定义的 `custom_fact_extraction_prompt` 中没有包含 "json" 这个词，就会触发这个错误。

## 解决方案

创建了一个补丁 `fix-json-prompt.patch`，在应用自定义提示词时自动检查并添加 "json" 相关说明：

1. **检查提示词**：如果自定义提示词中没有 "json" 这个词（不区分大小写）
2. **自动添加**：在提示词末尾添加 `"\n\nPlease respond in JSON format with a 'facts' array."`
3. **保持兼容**：如果提示词中已经包含 "json"，则不修改

## 补丁内容

补丁修改了两个位置（同步和异步的事实提取函数）：

```python
if self.config.custom_fact_extraction_prompt:
    # OpenAI requires "json" in the prompt when using response_format: json_object
    # Ensure the custom prompt includes "json" keyword
    if "json" not in self.config.custom_fact_extraction_prompt.lower():
        system_prompt = self.config.custom_fact_extraction_prompt + "\n\nPlease respond in JSON format with a 'facts' array."
    else:
        system_prompt = self.config.custom_fact_extraction_prompt
    user_prompt = f"Input:\n{parsed_messages}"
```

## 使用方法

### 自动应用

补丁会在构建 Mem0 API 镜像时自动应用（在 `Dockerfile` 中）。

### 手动应用

如果需要手动应用补丁：

```bash
cd /path/to/mem0
patch -p1 < deployment/mem0/patches/fix-json-prompt.patch
```

## 验证

### 测试自定义提示词

1. **不包含 "json" 的提示词**：
   ```bash
   CUSTOM_FACT_EXTRACTION_PROMPT="请保持记忆内容的原始语言，不要将中文翻译为英文。"
   ```
   补丁会自动添加 JSON 格式说明。

2. **已包含 "json" 的提示词**：
   ```bash
   CUSTOM_FACT_EXTRACTION_PROMPT="请以 JSON 格式返回事实列表。"
   ```
   补丁不会修改提示词。

### 测试 API 调用

```bash
curl -X POST "http://192.168.66.11:8888/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "我是湖北人，喜欢吃辣"}],
    "user_id": "test"
  }'
```

应该不再出现 400 错误。

## 最佳实践

### 自定义提示词建议

如果使用自定义 `custom_fact_extraction_prompt`，建议：

1. **包含 "json" 关键词**：在提示词中明确要求 JSON 格式
   ```
   "请以 JSON 格式返回提取的事实，包含 'facts' 数组。"
   ```

2. **明确格式要求**：说明期望的 JSON 结构
   ```
   "请返回 JSON 格式：{\"facts\": [...]}"
   ```

3. **保持语言一致性**：如果使用中文提示词，也要包含 "json"
   ```
   "请保持记忆内容的原始语言，不要将中文翻译为英文。请以 JSON 格式返回。"
   ```

## 相关配置

### 环境变量

```yaml
# docker-compose.1panel.yml
environment:
  CUSTOM_FACT_EXTRACTION_PROMPT: "请保持记忆内容的原始语言，不要将中文翻译为英文。"
```

### 配置示例

```python
# 正确的配置（包含 json）
CUSTOM_FACT_EXTRACTION_PROMPT = """
请从对话中提取关键事实。
请以 JSON 格式返回，包含 'facts' 数组。
保持原始语言，不要翻译。
"""

# 也可以不包含 json（补丁会自动添加）
CUSTOM_FACT_EXTRACTION_PROMPT = """
请从对话中提取关键事实。
保持原始语言，不要翻译。
"""
```

## 故障排查

### 问题 1：仍然出现 400 错误

**检查**：
1. 确认补丁已应用：检查构建日志
2. 确认提示词格式正确
3. 检查 OpenAI API 版本和模型是否支持 `response_format`

### 问题 2：补丁应用失败

**解决方法**：
```bash
# 检查补丁文件
cat deployment/mem0/patches/fix-json-prompt.patch

# 手动应用补丁
cd /app
patch -p1 < /tmp/fix-json-prompt.patch
```

### 问题 3：提示词被重复修改

**原因**：补丁只检查一次，不会重复添加。

**验证**：
```python
# 在代码中检查
if "json" not in prompt.lower():
    # 会添加一次
    prompt += "\n\nPlease respond in JSON format..."
```

## 参考

- [OpenAI API 文档 - JSON Mode](https://platform.openai.com/docs/guides/text-generation/json-mode)
- [Mem0 自定义提示词文档](https://docs.mem0.ai/open-source/features/custom-fact-extraction-prompt)
- [补丁文件](../deployment/mem0/patches/fix-json-prompt.patch)

