"""准备测试数据脚本 - 为三种记忆系统添加测试数据"""
import asyncio
import httpx
import json
import sys
from datetime import datetime

# 服务地址配置
COGNEE_URL = "http://192.168.66.11:8000"
MEMOBASE_URL = "http://192.168.66.11:8019"
MEM0_URL = "http://192.168.66.11:8888"
MEMOBASE_API_KEY = "secret"

# 测试用户信息
TEST_USER_ID = "test_user_001"
TEST_SESSION_ID = "test_session_001"
DATASET_NAME = "kb_tech"


async def prepare_cognee_data():
    """为 Cognee 准备知识库数据"""
    print("\n" + "="*60)
    print("1. 准备 Cognee 知识库数据")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 检查数据集是否存在
            print(f"\n检查数据集 '{DATASET_NAME}' 是否存在...")
            try:
                response = await client.get(f"{COGNEE_URL}/api/v1/datasets")
                datasets = response.json()
                dataset_exists = any(d.get("name") == DATASET_NAME for d in datasets)
                
                if dataset_exists:
                    print(f"✅ 数据集 '{DATASET_NAME}' 已存在")
                else:
                    print(f"📝 创建数据集 '{DATASET_NAME}'...")
                    # 先添加数据，Cognee 会自动创建数据集
            except Exception as e:
                print(f"⚠️  无法检查数据集: {e}")
            
            # 准备技术知识数据
            knowledge_texts = [
                """Python 是一种高级编程语言
                
Python 是一种解释型、面向对象、动态数据类型的高级程序设计语言。Python 由 Guido van Rossum 于 1989 年底发明，第一个公开发行版发行于 1991 年。

主要特点：
1. 简单易学：Python 极其容易上手，语法简洁清晰
2. 开源免费：Python 是开源的，可以自由使用和发布
3. 跨平台：支持 Windows、Linux、macOS 等操作系统
4. 丰富的库：拥有大量的第三方库和框架
5. 应用广泛：Web 开发、数据分析、人工智能、自动化等

常用框架：
- Django：全栈 Web 框架
- Flask：轻量级 Web 框架
- FastAPI：现代、快速的 Web 框架
- NumPy：科学计算库
- Pandas：数据分析库
- TensorFlow：机器学习框架
""",
                """人工智能和机器学习基础
                
人工智能（AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。

机器学习类型：
1. 监督学习：使用标注数据进行训练
   - 分类：预测离散标签
   - 回归：预测连续值
   
2. 无监督学习：从未标注数据中发现模式
   - 聚类：将数据分组
   - 降维：减少特征数量
   
3. 强化学习：通过与环境交互学习
   - 奖励机制
   - 策略优化

常用算法：
- 线性回归
- 逻辑回归
- 决策树
- 随机森林
- 神经网络
- 深度学习

应用领域：
- 计算机视觉
- 自然语言处理
- 语音识别
- 推荐系统
- 自动驾驶
""",
                """软件工程最佳实践
                
软件工程是将工程化方法应用于软件开发的学科。

开发流程：
1. 需求分析：理解和记录用户需求
2. 系统设计：架构设计和详细设计
3. 编码实现：按照设计编写代码
4. 测试验证：单元测试、集成测试、系统测试
5. 部署维护：发布和持续维护

最佳实践：
- 版本控制：使用 Git 进行版本管理
- 代码审查：团队成员互相审查代码
- 自动化测试：编写和运行自动化测试
- 持续集成：自动构建和测试
- 文档编写：保持文档与代码同步
- 敏捷开发：快速迭代和反馈

设计模式：
- 单例模式
- 工厂模式
- 观察者模式
- 策略模式
- 装饰器模式

代码质量：
- 可读性：清晰的命名和注释
- 可维护性：模块化和低耦合
- 可测试性：易于编写测试
- 性能：优化关键路径
"""
            ]
            
            # 添加知识到 Cognee
            for i, text in enumerate(knowledge_texts, 1):
                print(f"\n添加知识 {i}/{len(knowledge_texts)}...")
                try:
                    # 使用 Cognee 的 add 接口
                    response = await client.post(
                        f"{COGNEE_URL}/api/v1/add",
                        files={"data": (f"knowledge_{i}.txt", text.encode("utf-8"), "text/plain")},
                        data={"datasetName": DATASET_NAME}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ 知识 {i} 添加成功")
                    else:
                        print(f"   ⚠️  知识 {i} 添加失败: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"   ❌ 知识 {i} 添加错误: {e}")
            
            # 处理数据（cognify）
            print(f"\n处理知识库数据...")
            try:
                response = await client.post(
                    f"{COGNEE_URL}/api/v1/cognify",
                    json={"datasets": [DATASET_NAME]}
                )
                
                if response.status_code == 200:
                    print(f"   ✅ 知识库处理完成")
                else:
                    print(f"   ⚠️  知识库处理失败: {response.status_code}")
            except Exception as e:
                print(f"   ❌ 知识库处理错误: {e}")
            
            print(f"\n✅ Cognee 知识库数据准备完成！")
            print(f"   数据集名称: {DATASET_NAME}")
            print(f"   知识条数: {len(knowledge_texts)}")
            
    except Exception as e:
        print(f"\n❌ Cognee 数据准备失败: {e}")
        import traceback
        traceback.print_exc()


async def prepare_mem0_data():
    """为 Mem0 准备会话记忆数据"""
    print("\n" + "="*60)
    print("2. 准备 Mem0 会话记忆数据")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 准备对话记忆
            conversations = [
                # 第一组对话：自我介绍
                {
                    "messages": [
                        {"role": "user", "content": "你好，我叫张三，我是一名软件工程师"},
                        {"role": "assistant", "content": "你好张三！很高兴认识你。作为一名软件工程师，你一定对技术很感兴趣吧？"}
                    ],
                    "metadata": {"topic": "自我介绍", "timestamp": datetime.now().isoformat()}
                },
                # 第二组对话：兴趣爱好
                {
                    "messages": [
                        {"role": "user", "content": "我对 Python 编程特别感兴趣，经常用它做 Web 开发"},
                        {"role": "assistant", "content": "Python 确实是 Web 开发的好选择！你主要使用哪些框架呢？Django 还是 Flask？"}
                    ],
                    "metadata": {"topic": "技术兴趣", "timestamp": datetime.now().isoformat()}
                },
                # 第三组对话：工作经验
                {
                    "messages": [
                        {"role": "user", "content": "我主要用 FastAPI 和 Django，有 5 年的开发经验"},
                        {"role": "assistant", "content": "FastAPI 和 Django 都是很棒的框架！5 年经验已经很丰富了。"}
                    ],
                    "metadata": {"topic": "工作经验", "timestamp": datetime.now().isoformat()}
                },
                # 第四组对话：学习目标
                {
                    "messages": [
                        {"role": "user", "content": "最近在学习机器学习和 AI，特别是 LLM 相关的技术"},
                        {"role": "assistant", "content": "LLM 是目前非常热门的方向！你在学习哪些具体的技术栈呢？"}
                    ],
                    "metadata": {"topic": "学习目标", "timestamp": datetime.now().isoformat()}
                },
            ]
            
            # 添加对话记忆到 Mem0
            for i, conv in enumerate(conversations, 1):
                print(f"\n添加对话记忆 {i}/{len(conversations)}...")
                try:
                    payload = {
                        "messages": conv["messages"],
                        "user_id": TEST_USER_ID,
                        "agent_id": TEST_SESSION_ID,
                        "metadata": conv["metadata"]
                    }
                    
                    response = await client.post(
                        f"{MEM0_URL}/api/v1/memories",
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ 对话记忆 {i} 添加成功")
                        # 显示提取的记忆
                        if isinstance(result, dict) and "results" in result:
                            for memory in result["results"][:3]:
                                if isinstance(memory, dict) and "memory" in memory:
                                    print(f"      - {memory['memory']}")
                    else:
                        print(f"   ⚠️  对话记忆 {i} 添加失败: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"   ❌ 对话记忆 {i} 添加错误: {e}")
                
                # 等待一下让 Mem0 处理
                await asyncio.sleep(1)
            
            print(f"\n✅ Mem0 会话记忆数据准备完成！")
            print(f"   用户ID: {TEST_USER_ID}")
            print(f"   会话ID: {TEST_SESSION_ID}")
            print(f"   对话组数: {len(conversations)}")
            
            # 验证记忆是否保存成功
            print(f"\n验证记忆保存...")
            try:
                response = await client.post(
                    f"{MEM0_URL}/api/v1/search",
                    json={
                        "query": "张三的职业和兴趣",
                        "user_id": TEST_USER_ID,
                        "agent_id": TEST_SESSION_ID
                    }
                )
                
                if response.status_code == 200:
                    memories = response.json()
                    if memories:
                        print(f"   ✅ 找到 {len(memories)} 条记忆")
                        for i, mem in enumerate(memories[:3], 1):
                            if isinstance(mem, dict):
                                content = mem.get("memory", mem.get("content", ""))
                                print(f"      {i}. {content}")
                    else:
                        print(f"   ⚠️  未找到记忆（可能需要等待 Mem0 处理）")
                else:
                    print(f"   ⚠️  搜索失败: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  验证错误: {e}")
                
    except Exception as e:
        print(f"\n❌ Mem0 数据准备失败: {e}")
        import traceback
        traceback.print_exc()


async def prepare_memobase_data():
    """为 Memobase 准备用户画像数据"""
    print("\n" + "="*60)
    print("3. 准备 Memobase 用户画像数据")
    print("="*60)
    
    try:
        # 使用 memobase SDK
        from memobase import MemoBaseClient, ChatBlob
        import uuid
        
        # 将用户 ID 转换为 UUID 格式
        def user_id_to_uuid(user_id: str) -> str:
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))
        
        uuid_user_id = user_id_to_uuid(TEST_USER_ID)
        print(f"\n用户ID转换:")
        print(f"  原始ID: {TEST_USER_ID}")
        print(f"  UUID: {uuid_user_id}")
        
        # 初始化客户端
        client = MemoBaseClient(
            project_url=MEMOBASE_URL,
            api_key=MEMOBASE_API_KEY
        )
        
        # 创建或获取用户
        print(f"\n创建/获取用户...")
        try:
            # 尝试创建用户
            client.add_user(id=uuid_user_id, data={})
            print(f"   ✅ 用户创建成功")
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg or "409" in error_msg:
                print(f"   ✅ 用户已存在")
            else:
                print(f"   ⚠️  创建用户警告: {e}")
        
        # 获取用户对象
        user = client.get_user(uuid_user_id, no_get=True)
        
        # 准备对话数据（用于提取画像）
        conversations = [
            # 基本信息
            [
                {"role": "user", "content": "我叫张三，今年30岁"},
                {"role": "assistant", "content": "你好张三！"}
            ],
            # 职业信息
            [
                {"role": "user", "content": "我是一名软件工程师，有5年的Python开发经验"},
                {"role": "assistant", "content": "很棒的经验！"}
            ],
            # 技能和兴趣
            [
                {"role": "user", "content": "我擅长 FastAPI、Django、机器学习，对 AI 和 LLM 很感兴趣"},
                {"role": "assistant", "content": "这些都是很热门的技术！"}
            ],
            # 工作偏好
            [
                {"role": "user", "content": "我喜欢做后端开发和数据分析，平时用 Python 和 SQL 比较多"},
                {"role": "assistant", "content": "后端开发确实很有挑战性！"}
            ],
            # 学习目标
            [
                {"role": "user", "content": "我现在在学习大语言模型和向量数据库，想做 AI 应用开发"},
                {"role": "assistant", "content": "AI 应用开发是很好的方向！"}
            ],
            # 项目经验
            [
                {"role": "user", "content": "我做过电商系统、数据分析平台、智能客服系统等项目"},
                {"role": "assistant", "content": "项目经验很丰富啊！"}
            ],
        ]
        
        # 插入对话数据到 Memobase
        for i, messages in enumerate(conversations, 1):
            print(f"\n插入对话 {i}/{len(conversations)}...")
            try:
                blob = ChatBlob(messages=messages)
                user.insert(blob)
                print(f"   ✅ 对话 {i} 插入成功")
            except Exception as e:
                print(f"   ❌ 对话 {i} 插入失败: {e}")
        
        # 刷新以确保数据保存
        print(f"\n保存数据...")
        try:
            user.flush()
            print(f"   ✅ 数据保存成功")
        except Exception as e:
            print(f"   ⚠️  保存警告: {e}")
        
        # 等待一下让 Memobase 处理
        print(f"\n等待 Memobase 处理画像（5秒）...")
        await asyncio.sleep(5)
        
        # 获取用户画像验证
        print(f"\n获取用户画像验证...")
        try:
            profile = user.profile(max_token_size=500, prefer_topics=["basic_info", "interest", "work"])
            if profile:
                print(f"   ✅ 用户画像生成成功")
                print(f"\n用户画像内容:")
                print("-" * 60)
                print(profile)
                print("-" * 60)
            else:
                print(f"   ⚠️  画像为空（可能需要更多时间处理）")
        except Exception as e:
            print(f"   ⚠️  获取画像错误: {e}")
        
        print(f"\n✅ Memobase 用户画像数据准备完成！")
        print(f"   用户ID: {TEST_USER_ID} (UUID: {uuid_user_id})")
        print(f"   对话组数: {len(conversations)}")
        
    except Exception as e:
        print(f"\n❌ Memobase 数据准备失败: {e}")
        import traceback
        traceback.print_exc()


async def verify_data():
    """验证所有数据是否准备成功"""
    print("\n" + "="*60)
    print("4. 验证数据准备结果")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 验证 Cognee
        print(f"\n验证 Cognee 知识库...")
        try:
            response = await client.post(
                f"{COGNEE_URL}/api/v1/search",
                json={
                    "query": "Python 是什么",
                    "datasets": [DATASET_NAME],
                    "searchType": "GRAPH_COMPLETION"
                }
            )
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    print(f"   ✅ Cognee 有 {len(results)} 条知识")
                    print(f"      示例: {str(results[0])[:100]}...")
                else:
                    print(f"   ⚠️  Cognee 知识库为空")
            else:
                print(f"   ⚠️  Cognee 搜索失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Cognee 验证错误: {e}")
        
        # 验证 Mem0
        print(f"\n验证 Mem0 会话记忆...")
        try:
            response = await client.post(
                f"{MEM0_URL}/api/v1/search",
                json={
                    "query": "张三",
                    "user_id": TEST_USER_ID,
                    "agent_id": TEST_SESSION_ID
                }
            )
            
            if response.status_code == 200:
                memories = response.json()
                if memories:
                    print(f"   ✅ Mem0 有 {len(memories)} 条记忆")
                    for i, mem in enumerate(memories[:3], 1):
                        if isinstance(mem, dict):
                            content = mem.get("memory", mem.get("content", ""))
                            print(f"      {i}. {content}")
                else:
                    print(f"   ⚠️  Mem0 记忆为空")
            else:
                print(f"   ⚠️  Mem0 搜索失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Mem0 验证错误: {e}")
        
        # 验证 Memobase
        print(f"\n验证 Memobase 用户画像...")
        try:
            from memobase import MemoBaseClient
            import uuid
            
            uuid_user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, TEST_USER_ID))
            client_mb = MemoBaseClient(
                project_url=MEMOBASE_URL,
                api_key=MEMOBASE_API_KEY
            )
            
            user = client_mb.get_user(uuid_user_id, no_get=False)
            profile = user.profile(max_token_size=300)
            
            if profile:
                print(f"   ✅ Memobase 有用户画像")
                print(f"      内容: {str(profile)[:200]}...")
            else:
                print(f"   ⚠️  Memobase 画像为空")
        except Exception as e:
            print(f"   ❌ Memobase 验证错误: {e}")


async def main():
    """主函数"""
    print("="*60)
    print("准备 POC 测试数据")
    print("="*60)
    print(f"\n服务配置:")
    print(f"  Cognee: {COGNEE_URL}")
    print(f"  Memobase: {MEMOBASE_URL}")
    print(f"  Mem0: {MEM0_URL}")
    print(f"\n测试用户:")
    print(f"  用户ID: {TEST_USER_ID}")
    print(f"  会话ID: {TEST_SESSION_ID}")
    print(f"  数据集: {DATASET_NAME}")
    
    # 依次准备数据
    await prepare_cognee_data()
    await prepare_mem0_data()
    await prepare_memobase_data()
    await verify_data()
    
    print("\n" + "="*60)
    print("✅ 数据准备完成！")
    print("="*60)
    print(f"\n现在可以测试对话了：")
    print(f"  python3 quick_test.py")
    print(f"\n或使用 curl 测试：")
    print(f"""  curl -X POST "http://localhost:8080/api/v1/test/conversation" \\
    -H "Content-Type: application/json" \\
    -d '{{
      "user_id": "{TEST_USER_ID}",
      "session_id": "{TEST_SESSION_ID}",
      "message": "我之前说过我的职业是什么？",
      "dataset_names": ["{DATASET_NAME}"]
    }}'""")


if __name__ == "__main__":
    asyncio.run(main())
