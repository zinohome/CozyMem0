"""完整测试所有服务"""
import asyncio
import httpx
import json
import os
from typing import Dict, Any, Optional

# 服务地址配置（根据您提供的地址）
COGNEE_URL = "http://192.168.66.11:8888"
MEMOBASE_URL = "http://192.168.66.11:8019"
MEM0_URL = "http://192.168.66.11:8000"
POC_URL = "http://localhost:8080"


async def test_service_endpoint(url: str, method: str = "GET", json_data: Optional[Dict] = None, headers: Optional[Dict] = None) -> tuple[bool, int, str]:
    """测试服务端点"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, json=json_data, headers=headers)
            return True, response.status_code, response.text[:500]
    except Exception as e:
        return False, 0, str(e)


async def test_cognee():
    """测试 Cognee 服务"""
    print("\n" + "="*60)
    print("测试 Cognee 服务")
    print("="*60)
    
    # 测试健康检查
    ok, status, text = await test_service_endpoint(f"{COGNEE_URL}/health")
    print(f"健康检查: {'✅' if ok and status == 200 else '❌'} (状态码: {status})")
    
    # 测试文档页面
    ok, status, text = await test_service_endpoint(f"{COGNEE_URL}/docs")
    print(f"API文档: {'✅' if ok else '❌'} (状态码: {status})")
    
    # 测试搜索接口（可能需要数据集）
    ok, status, text = await test_service_endpoint(
        f"{COGNEE_URL}/api/v1/search",
        method="POST",
        json_data={"query": "test", "search_type": "GRAPH_COMPLETION", "top_k": 1}
    )
    print(f"搜索接口: {'✅' if ok else '❌'} (状态码: {status})")
    if not ok or status not in [200, 422]:
        print(f"  响应: {text[:200]}")


async def test_memobase():
    """测试 Memobase 服务"""
    print("\n" + "="*60)
    print("测试 Memobase 服务")
    print("="*60)
    
    # 测试健康检查
    ok, status, text = await test_service_endpoint(f"{MEMOBASE_URL}/health")
    print(f"健康检查: {'✅' if ok and status == 200 else '❌'} (状态码: {status})")
    
    # 测试文档页面
    ok, status, text = await test_service_endpoint(f"{MEMOBASE_URL}/docs")
    print(f"API文档: {'✅' if ok else '❌'} (状态码: {status})")
    
    # 测试用户接口
    headers = {"X-API-Key": "secret"}
    ok, status, text = await test_service_endpoint(
        f"{MEMOBASE_URL}/api/v1/users/test_user",
        headers=headers
    )
    print(f"用户接口: {'✅' if ok else '❌'} (状态码: {status})")


async def test_mem0():
    """测试 Mem0 服务"""
    print("\n" + "="*60)
    print("测试 Mem0 服务")
    print("="*60)
    
    # 测试健康检查
    ok, status, text = await test_service_endpoint(f"{MEM0_URL}/health")
    print(f"健康检查: {'✅' if ok and status == 200 else '❌'} (状态码: {status})")
    
    # 测试文档页面
    ok, status, text = await test_service_endpoint(f"{MEM0_URL}/docs")
    print(f"API文档: {'✅' if ok else '❌'} (状态码: {status})")
    
    # 测试搜索接口
    ok, status, text = await test_service_endpoint(
        f"{MEM0_URL}/api/v1/memories/search",
        method="POST",
        json_data={"query": "test", "user_id": "test_user", "limit": 1}
    )
    print(f"搜索接口: {'✅' if ok else '❌'} (状态码: {status})")


async def test_poc_service():
    """测试 POC 服务"""
    print("\n" + "="*60)
    print("测试 POC 服务")
    print("="*60)
    
    # 测试健康检查
    ok, status, text = await test_service_endpoint(f"{POC_URL}/health")
    if ok and status == 200:
        print(f"健康检查: ✅ (状态码: {status})")
        
        # 测试根路径
        ok, status, text = await test_service_endpoint(f"{POC_URL}/")
        print(f"根路径: {'✅' if ok else '❌'} (状态码: {status})")
        
        # 测试文档
        ok, status, text = await test_service_endpoint(f"{POC_URL}/docs")
        print(f"API文档: {'✅' if ok else '❌'} (状态码: {status})")
        
        return True
    else:
        print(f"健康检查: ❌ POC 服务未运行")
        print(f"\n💡 提示：要启动 POC 服务，请运行：")
        print(f"   cd {os.getcwd()}")
        print(f"   # 1. 创建 .env 文件并配置 OPENAI_API_KEY")
        print(f"   # 2. 设置服务地址：")
        print(f"   export COGNEE_API_URL={COGNEE_URL}")
        print(f"   export MEMOBASE_PROJECT_URL={MEMOBASE_URL}")
        print(f"   export MEM0_API_URL={MEM0_URL}")
        print(f"   # 3. 启动服务：")
        print(f"   python3 -m src.main")
        print(f"   # 或")
        print(f"   uvicorn src.main:app --host 0.0.0.0 --port 8080")
        return False


async def test_poc_conversation():
    """测试 POC 对话功能"""
    print("\n" + "="*60)
    print("测试 POC 对话功能")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 第一次对话
            print("发送测试对话...")
            response = await client.post(
                f"{POC_URL}/api/v1/test/conversation",
                json={
                    "user_id": "test_user_001",
                    "session_id": "test_session_001",
                    "message": "你好，我是张三，我是一名软件工程师，对Python编程很感兴趣",
                    "dataset_names": []
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 对话成功")
                print(f"\n用户消息: {result.get('message', '')}")
                print(f"\nAI响应: {result.get('response', '')[:200]}...")
                
                context = result.get('context', {})
                print(f"\n上下文信息:")
                print(f"  - 用户画像: {json.dumps(context.get('user_profile', {}), indent=2, ensure_ascii=False)}")
                print(f"  - 会话记忆数量: {context.get('session_memories_count', 0)}")
                print(f"  - 知识数量: {context.get('knowledge_count', 0)}")
                
                return result
            else:
                print(f"❌ 对话失败: {response.status_code}")
                print(f"错误: {response.text[:500]}")
                return None
    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主测试函数"""
    print("="*60)
    print("开始完整测试所有服务")
    print("="*60)
    
    # 测试三个基础服务
    await test_cognee()
    await test_memobase()
    await test_mem0()
    
    # 测试 POC 服务
    poc_running = await test_poc_service()
    
    # 如果 POC 服务运行，测试对话功能
    if poc_running:
        result = await test_poc_conversation()
        
        if result:
            # 测试获取用户画像
            print("\n" + "="*60)
            print("测试获取用户画像")
            print("="*60)
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    user_id = result.get("user_id", "test_user_001")
                    response = await client.get(f"{POC_URL}/api/v1/users/{user_id}/profile")
                    if response.status_code == 200:
                        profile_result = response.json()
                        print("✅ 获取用户画像成功")
                        print(f"画像: {json.dumps(profile_result.get('profile', {}), indent=2, ensure_ascii=False)}")
                    else:
                        print(f"❌ 获取用户画像失败: {response.status_code}")
            except Exception as e:
                print(f"❌ 获取用户画像失败: {e}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
