"""诊断脚本：检查服务连接和配置"""
import asyncio
import httpx
import json
import sys

POC_URL = "http://localhost:8080"


async def check_service_status():
    """检查服务状态"""
    print("="*60)
    print("检查 POC 服务状态")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{POC_URL}/api/v1/debug/status")
            if response.status_code == 200:
                data = response.json()
                print("\n✅ 服务状态:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                services = data.get("services", {})
                
                # 检查各个服务
                print("\n" + "="*60)
                print("服务初始化状态检查")
                print("="*60)
                
                cognee = services.get("cognee", {})
                print(f"\nCognee:")
                print(f"  URL: {cognee.get('url')}")
                print(f"  初始化: {'✅' if cognee.get('initialized') else '❌'}")
                
                memobase = services.get("memobase", {})
                print(f"\nMemobase:")
                print(f"  URL: {memobase.get('url')}")
                print(f"  初始化: {'✅' if memobase.get('initialized') else '❌'}")
                
                mem0 = services.get("mem0", {})
                print(f"\nMem0:")
                print(f"  URL: {mem0.get('url')}")
                print(f"  初始化: {'✅' if mem0.get('initialized') else '❌'}")
                
                openai = services.get("openai", {})
                print(f"\nOpenAI:")
                print(f"  模型: {openai.get('model')}")
                print(f"  Base URL: {openai.get('base_url')}")
                
                return data
            else:
                print(f"❌ 无法获取服务状态: {response.status_code}")
                print(f"响应: {response.text}")
                return None
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return None


async def test_individual_services():
    """测试各个服务的连接"""
    print("\n" + "="*60)
    print("测试各个服务连接")
    print("="*60)
    
    # 从服务状态获取 URL
    status = await check_service_status()
    if not status:
        return
    
    services = status.get("services", {})
    
    # 测试 Cognee
    cognee_url = services.get("cognee", {}).get("url")
    if cognee_url:
        print(f"\n测试 Cognee ({cognee_url}):")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{cognee_url}/docs")
                print(f"  {'✅' if response.status_code == 200 else '❌'} 文档页面: {response.status_code}")
        except Exception as e:
            print(f"  ❌ 连接失败: {e}")
    
    # 测试 Memobase
    memobase_url = services.get("memobase", {}).get("url")
    if memobase_url:
        print(f"\n测试 Memobase ({memobase_url}):")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{memobase_url}/docs")
                print(f"  {'✅' if response.status_code == 200 else '❌'} 文档页面: {response.status_code}")
        except Exception as e:
            print(f"  ❌ 连接失败: {e}")
    
    # 测试 Mem0
    mem0_url = services.get("mem0", {}).get("url")
    if mem0_url:
        print(f"\n测试 Mem0 ({mem0_url}):")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # 测试健康检查
                response = await client.get(f"{mem0_url}/health")
                print(f"  {'✅' if response.status_code == 200 else '❌'} 健康检查: {response.status_code}")
                
                # 测试 API 端点
                response = await client.post(
                    f"{mem0_url}/api/v1/search",
                    json={"query": "test", "user_id": "test_user"}
                )
                print(f"  {'✅' if response.status_code in [200, 404, 422] else '❌'} 搜索 API: {response.status_code}")
        except Exception as e:
            print(f"  ❌ 连接失败: {e}")


async def test_conversation_with_debug():
    """测试对话并查看调试信息"""
    print("\n" + "="*60)
    print("测试对话（带调试信息）")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{POC_URL}/api/v1/test/conversation",
                json={
                    "user_id": "test_user_diagnose",
                    "session_id": "test_session_diagnose",
                    "message": "你好，我是测试用户",
                    "dataset_names": []
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ 对话成功")
                print(f"\n响应: {result.get('response', '')[:100]}...")
                
                context = result.get("context", {})
                print(f"\n上下文信息:")
                print(f"  用户画像字段数: {len(context.get('user_profile', {}))}")
                print(f"  会话记忆数量: {context.get('session_memories_count', 0)}")
                print(f"  知识数量: {context.get('knowledge_count', 0)}")
                
                # 显示调试信息
                debug = context.get("debug")
                if debug:
                    print(f"\n⚠️  调试信息（发现错误）:")
                    if debug.get("profile_error"):
                        print(f"  用户画像错误: {debug['profile_error']}")
                    if debug.get("memories_error"):
                        print(f"  记忆错误: {debug['memories_error']}")
                    if debug.get("knowledge_error"):
                        print(f"  知识检索错误: {debug['knowledge_error']}")
                else:
                    print("\n✅ 没有发现错误")
                
                # 显示详细信息
                if context.get("user_profile"):
                    print(f"\n用户画像: {json.dumps(context['user_profile'], indent=2, ensure_ascii=False)}")
                if context.get("session_memories"):
                    print(f"\n会话记忆: {json.dumps(context['session_memories'], indent=2, ensure_ascii=False)}")
                if context.get("knowledge"):
                    print(f"\n知识: {json.dumps(context['knowledge'], indent=2, ensure_ascii=False)}")
            else:
                print(f"\n❌ 对话失败: {response.status_code}")
                print(f"错误: {response.text}")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("="*60)
    print("POC 服务诊断工具")
    print("="*60)
    
    # 1. 检查服务状态
    await check_service_status()
    
    # 2. 测试各个服务连接
    await test_individual_services()
    
    # 3. 测试对话
    await test_conversation_with_debug()
    
    print("\n" + "="*60)
    print("诊断完成")
    print("="*60)
    print("\n💡 提示:")
    print("1. 如果服务未初始化，请检查环境变量配置")
    print("2. 如果连接失败，请确认服务是否正在运行")
    print("3. 查看服务日志获取更详细的错误信息")


if __name__ == "__main__":
    asyncio.run(main())
