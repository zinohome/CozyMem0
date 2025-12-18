"""测试三种记忆系统都有数据返回"""
import asyncio
import httpx
import json

POC_URL = "http://localhost:8080"
TEST_USER_ID = "test_user_001"
TEST_SESSION_ID = "test_session_001"
DATASET_NAME = "kb_tech"


async def test_conversation_with_data():
    """测试对话 - 验证三种记忆系统都有数据"""
    print("="*60)
    print("测试三种记忆系统的数据返回")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"\n📤 发送测试消息...")
            print(f"   用户ID: {TEST_USER_ID}")
            print(f"   会话ID: {TEST_SESSION_ID}")
            print(f"   消息: 我之前说过我的职业是什么？")
            print(f"   知识库: {DATASET_NAME}")
            
            response = await client.post(
                f"{POC_URL}/api/v1/test/conversation",
                json={
                    "user_id": TEST_USER_ID,
                    "session_id": TEST_SESSION_ID,
                    "message": "我之前说过我的职业是什么？",
                    "dataset_names": [DATASET_NAME]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n✅ 对话成功！")
                print(f"\n{'='*60}")
                print(f"🤖 AI 响应:")
                print(f"{'='*60}")
                print(f"{result.get('response', '')}")
                
                context = result.get('context', {})
                
                # 1. Memobase 用户画像
                print(f"\n{'='*60}")
                print(f"📊 1. Memobase 用户画像")
                print(f"{'='*60}")
                user_profile = context.get('user_profile', {})
                status = context.get('user_profile_status', '')
                print(f"状态: {status}")
                
                if user_profile:
                    print(f"\n详细画像:")
                    for category, items in user_profile.items():
                        print(f"\n  【{category}】")
                        if isinstance(items, dict):
                            for key, value in items.items():
                                if isinstance(value, dict):
                                    content = value.get('content', '')
                                    print(f"    • {key}: {content}")
                                else:
                                    print(f"    • {key}: {value}")
                else:
                    print("  ⚠️  无用户画像数据")
                
                # 2. Mem0 会话记忆
                print(f"\n{'='*60}")
                print(f"💭 2. Mem0 会话记忆")
                print(f"{'='*60}")
                memories_count = context.get('session_memories_count', 0)
                memories_status = context.get('session_memories_status', '')
                print(f"状态: {memories_status}")
                print(f"总数: {memories_count} 条")
                
                session_memories = context.get('session_memories', [])
                if session_memories:
                    print(f"\n前 5 条记忆:")
                    for i, memory in enumerate(session_memories[:5], 1):
                        content = memory.get('content', '')
                        session_type = memory.get('session', '')
                        memory_type = memory.get('type', '')
                        print(f"  {i}. [{session_type}/{memory_type}] {content}")
                else:
                    print("  ⚠️  无会话记忆数据")
                
                # 3. Cognee 专业知识
                print(f"\n{'='*60}")
                print(f"📚 3. Cognee 专业知识")
                print(f"{'='*60}")
                knowledge_count = context.get('knowledge_count', 0)
                knowledge_status = context.get('knowledge_status', '')
                print(f"状态: {knowledge_status}")
                print(f"总数: {knowledge_count} 条")
                
                knowledge = context.get('knowledge', [])
                if knowledge:
                    print(f"\n知识内容:")
                    for i, item in enumerate(knowledge, 1):
                        content = item.get('content', '')
                        source = item.get('source', '')
                        score = item.get('score', 0.0)
                        print(f"  {i}. [{source}] (相关度: {score:.2f})")
                        print(f"     {content[:200]}{'...' if len(content) > 200 else ''}")
                else:
                    print("  ⚠️  无专业知识数据")
                
                # 总结
                print(f"\n{'='*60}")
                print(f"✅ 测试结果总结")
                print(f"{'='*60}")
                print(f"1. Memobase 用户画像: {'✅ 有数据' if user_profile else '❌ 无数据'} ({len(user_profile)} 个分类)")
                print(f"2. Mem0 会话记忆: {'✅ 有数据' if session_memories else '❌ 无数据'} ({memories_count} 条记忆)")
                print(f"3. Cognee 专业知识: {'✅ 有数据' if knowledge else '❌ 无数据'} ({knowledge_count} 条知识)")
                
                all_have_data = bool(user_profile) and bool(session_memories) and bool(knowledge)
                if all_have_data:
                    print(f"\n🎉 成功！三种记忆系统都返回了真实数据！")
                else:
                    print(f"\n⚠️  部分系统无数据，可能需要重新准备数据")
                
                return result
            else:
                print(f"\n❌ 对话失败: {response.status_code}")
                print(f"错误: {response.text}")
                return None
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主函数"""
    # 检查服务状态
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{POC_URL}/health")
            if response.status_code != 200:
                print(f"❌ POC 服务未运行")
                return
    except:
        print(f"❌ POC 服务未运行")
        return
    
    print("✅ POC 服务运行正常\n")
    
    # 测试对话
    await test_conversation_with_data()


if __name__ == "__main__":
    asyncio.run(main())
