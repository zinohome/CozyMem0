# 服务测试报告

## 测试时间
2024年测试

## 服务地址配置

根据您提供的信息，服务地址如下：
- **Cognee**: http://192.168.66.11:8888
- **Memobase**: http://192.168.66.11:8019
- **Mem0**: http://192.168.66.11:8000
- **POC服务**: http://localhost:8080 (需要启动)

## 测试结果

### ✅ 服务连接测试

| 服务 | 状态 | API文档 | 说明 |
|------|------|---------|------|
| Cognee | ✅ 可访问 | ✅ 正常 | API文档可访问，服务运行正常 |
| Memobase | ✅ 可访问 | ✅ 正常 | API文档可访问，服务运行正常 |
| Mem0 | ✅ 可访问 | ✅ 正常 | 健康检查和API文档都正常 |

### ⚠️ 注意事项

1. **Cognee API端点**: 搜索接口返回404，可能需要检查API路径或需要先创建数据集
2. **Memobase API**: 用户接口返回401，可能需要正确的API密钥
3. **Mem0 API**: 搜索接口返回404，可能需要先添加记忆数据

### ❌ POC服务

POC服务目前未运行，需要启动后才能进行完整测试。

## 下一步操作

### 1. 启动 POC 服务

#### 方法一：使用启动脚本（推荐）

```bash
cd /Users/zhangjun/CursorProjects/CozyMem0/projects/conversational-agent-poc

# 设置 OpenAI API Key
export OPENAI_API_KEY='your-api-key-here'

# 启动服务
./start_poc.sh
```

#### 方法二：手动启动

```bash
cd /Users/zhangjun/CursorProjects/CozyMem0/projects/conversational-agent-poc

# 设置环境变量
export COGNEE_API_URL="http://192.168.66.11:8888"
export MEMOBASE_PROJECT_URL="http://192.168.66.11:8019"
export MEM0_API_URL="http://192.168.66.11:8000"
export OPENAI_API_KEY="your-api-key-here"

# 启动服务
python3 -m src.main
# 或
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

### 2. 运行测试

#### 完整服务测试

```bash
python3 test_all_services.py
```

#### 快速对话测试（需要POC服务运行）

```bash
python3 quick_test.py
```

#### 使用 curl 测试

```bash
# 健康检查
curl http://localhost:8080/health

# 测试对话
curl -X POST "http://localhost:8080/api/v1/test/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "session_id": "test_session_001",
    "message": "你好，我是张三，我是一名软件工程师，对Python编程很感兴趣",
    "dataset_names": []
  }'

# 获取用户画像
curl "http://localhost:8080/api/v1/users/test_user_001/profile"
```

## 测试脚本说明

### test_all_services.py
完整测试所有服务的连接和功能，包括：
- 服务健康检查
- API文档访问
- API端点测试
- POC服务测试（如果运行）

### quick_test.py
快速测试POC对话功能，包括：
- 对话测试
- 记忆测试
- 用户画像测试

### start_poc.sh
启动POC服务的便捷脚本，自动配置服务地址。

## 预期测试流程

1. **第一次对话**：用户介绍自己
   - 系统应该提取用户信息并保存到Memobase
   - 对话内容保存到Mem0

2. **第二次对话**：询问之前的信息
   - 系统应该能够从Mem0检索之前的对话记忆
   - 系统应该能够从Memobase获取用户画像

3. **跨会话测试**：新会话中询问之前的信息
   - 系统应该能够从Mem0检索跨会话记忆
   - 系统应该能够从Memobase获取用户画像

## 故障排查

### POC服务无法启动

1. 检查依赖是否安装：
   ```bash
   pip3 install -r requirements.txt
   ```

2. 检查环境变量是否正确设置

3. 检查端口8080是否被占用：
   ```bash
   lsof -i :8080
   ```

### 服务连接失败

1. 检查服务地址是否正确
2. 检查网络连接
3. 检查防火墙设置

### API调用失败

1. 检查API密钥是否正确
2. 检查服务是否正常运行
3. 查看服务日志

## 测试检查清单

- [ ] Cognee服务可访问
- [ ] Memobase服务可访问
- [ ] Mem0服务可访问
- [ ] POC服务已启动
- [ ] OpenAI API Key已配置
- [ ] 第一次对话测试成功
- [ ] 记忆功能测试成功
- [ ] 用户画像功能测试成功
- [ ] 跨会话记忆测试成功
