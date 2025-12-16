"""快速测试对话功能"""
import asyncio
import httpx
import json
import sys

POC_URL = "http://localhost:8080"


async def test_conversation(user_id: str, session_id: str, message: str, dataset_names: list = None):
    """测试对话"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"\n📤 发送消息: {message}")
            print(f"   用户ID: {user_id}, 会话ID: {session_id}")
            
            response = await client.post(
                f"{POC_URL}/api/v1/test/conversation",
                json={
                    "user_id": user_id,
                    "session_id": session_id,
                    "message": message,
                    "dataset_names": dataset_names or []
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ 对话成功")
                print(f"\n🤖 AI响应:")
                print(f"   {result.get('response', '')}")
                
                context = result.get('context', {})
                if context:
                    print(f"\n📊 上下文信息:")
                    print(f"   - 会话记忆数量: {context.get('session_memories_count', 0)}")
                    print(f"   - 知识数量: {context.get('knowledge_count', 0)}")
                    
                    user_profile = context.get('user_profile', {})
                    if user_profile:
                        print(f"\n👤 用户画像:")
                        print(json.dumps(user_profile, indent=2, ensure_ascii=False))
                
                return result
            else:
                print(f"\n❌ 对话失败: {response.status_code}")
                print(f"错误: {response.text}")
                return None
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return None


async def test_user_profile(user_id: str):
    """测试获取用户画像"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{POC_URL}/api/v1/users/{user_id}/profile")
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ 获取用户画像成功")
                print(json.dumps(result.get('profile', {}), indent=2, ensure_ascii=False))
                return result
            else:
                print(f"\n❌ 获取用户画像失败: {response.status_code}")
                return None
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return None


async def main():
    """主函数"""
    print("="*60)
    print("快速测试对话功能")
    print("="*60)
    
    # 检查服务是否运行
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{POC_URL}/health")
            if response.status_code != 200:
                print(f"❌ POC 服务未运行或无法访问 ({POC_URL})")
                print("\n请先启动 POC 服务：")
                print("  ./start_poc.sh")
                print("  或")
                print("  python3 -m src.main")
                sys.exit(1)
    except:
        print(f"❌ POC 服务未运行或无法访问 ({POC_URL})")
        print("\n请先启动 POC 服务：")
        print("  ./start_poc.sh")
        print("  或")
        print("  python3 -m src.main")
        sys.exit(1)
    
    print("✅ POC 服务运行正常\n")
    
    # 测试对话
    user_id = "test_user_001"
    session_id = "test_session_001"
    
    # 第一次对话
    print("\n" + "="*60)
    print("测试 1: 第一次对话（介绍自己）")
    print("="*60)
    result1 = await test_conversation(
        user_id=user_id,
        session_id=session_id,
        message="你好，我是张三，我是一名软件工程师，对Python编程很感兴趣"
    )
    
    if result1:
        # 等待一下，让记忆保存完成
        await asyncio.sleep(2)
        
        # 第二次对话（测试记忆）
        print("\n" + "="*60)
        print("测试 2: 第二次对话（测试记忆）")
        print("="*60)
        result2 = await test_conversation(
            user_id=user_id,
            session_id=session_id,
            message="我之前说过我的职业是什么？"
        )
        
        # 获取用户画像
        print("\n" + "="*60)
        print("测试 3: 获取用户画像")
        print("="*60)
        await test_user_profile(user_id)
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
