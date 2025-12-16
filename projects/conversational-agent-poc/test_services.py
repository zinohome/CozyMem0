"""测试服务连接和功能"""
import asyncio
import httpx
import json
from typing import Dict, Any, Optional

# 服务地址配置
COGNEE_URL = "http://192.168.66.11:8888"
MEMOBASE_URL = "http://192.168.66.11:8019"
MEM0_URL = "http://192.168.66.11:8000"
POC_URL = "http://localhost:8080"  # POC 服务地址


async def test_service_health(url: str, service_name: str) -> bool:
    """测试服务健康状态"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 尝试访问 /health 或 /docs
            endpoints = ["/health", "/docs", "/"]
            for endpoint in endpoints:
                try:
                    response = await client.get(f"{url}{endpoint}")
                    if response.status_code in [200, 404]:  # 404 也算服务可访问
                        print(f"✅ {service_name}: 服务可访问 ({url}{endpoint})")
                        return True
                except:
                    continue
            print(f"❌ {service_name}: 无法访问 ({url})")
            return False
    except Exception as e:
        print(f"❌ {service_name}: 连接失败 - {e}")
        return False


async def test_cognee_api() -> bool:
    """测试 Cognee API"""
    print("\n=== 测试 Cognee API ===")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试搜索接口
            response = await client.post(
                f"{COGNEE_URL}/api/v1/search",
                json={
                    "query": "test",
                    "search_type": "GRAPH_COMPLETION",
                    "top_k": 1
                }
            )
            if response.status_code == 200:
                print(f"✅ Cognee 搜索接口正常")
                return True
            elif response.status_code == 422:
                print(f"⚠️  Cognee API 需要更多参数，但服务可访问")
                return True
            else:
                print(f"❌ Cognee API 返回错误: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"❌ Cognee API 测试失败: {e}")
        return False


async def test_memobase_api() -> bool:
    """测试 Memobase API"""
    print("\n=== 测试 Memobase API ===")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试获取用户接口
            response = await client.get(
                f"{MEMOBASE_URL}/api/v1/users/test_user",
                headers={"X-API-Key": "secret"}
            )
            if response.status_code in [200, 404]:
                print(f"✅ Memobase API 可访问")
                return True
            else:
                print(f"⚠️  Memobase API 返回: {response.status_code}")
                return True  # 即使返回其他状态码，也认为服务可访问
    except Exception as e:
        print(f"❌ Memobase API 测试失败: {e}")
        return False


async def test_mem0_api() -> bool:
    """测试 Mem0 API"""
    print("\n=== 测试 Mem0 API ===")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 测试搜索接口
            response = await client.post(
                f"{MEM0_URL}/api/v1/memories/search",
                json={
                    "query": "test",
                    "user_id": "test_user",
                    "limit": 1
                }
            )
            if response.status_code in [200, 404, 422]:
                print(f"✅ Mem0 API 可访问")
                return True
            else:
                print(f"⚠️  Mem0 API 返回: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return True
    except Exception as e:
        print(f"❌ Mem0 API 测试失败: {e}")
        return False


async def test_poc_service() -> bool:
    """测试 POC 服务"""
    print("\n=== 测试 POC 服务 ===")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{POC_URL}/health")
            if response.status_code == 200:
                print(f"✅ POC 服务运行正常")
                return True
            else:
                print(f"❌ POC 服务返回: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ POC 服务未运行或无法访问: {e}")
        print(f"   请确保 POC 服务已启动在 {POC_URL}")
        return False


async def test_conversation() -> Dict[str, Any]:
    """测试对话功能"""
    print("\n=== 测试对话功能 ===")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 第一次对话
            print("发送第一次对话...")
            response = await client.post(
                f"{POC_URL}/api/v1/test/conversation",
                json={
                    "user_id": "test_user_001",
                    "session_id": "test_session_001",
                    "message": "你好，我是张三，我是一名软件工程师，对Python编程很感兴趣",
                    "dataset_names": []  # 暂时不指定数据集
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 对话成功")
                print(f"   响应: {result.get('response', '')[:100]}...")
                print(f"   用户画像: {json.dumps(result.get('context', {}).get('user_profile', {}), indent=2, ensure_ascii=False)}")
                return result
            else:
                print(f"❌ 对话失败: {response.status_code}")
                print(f"   错误: {response.text[:500]}")
                return {}
    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {}


async def test_user_profile(user_id: str) -> Dict[str, Any]:
    """测试获取用户画像"""
    print(f"\n=== 测试获取用户画像 (user_id: {user_id}) ===")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{POC_URL}/api/v1/users/{user_id}/profile")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 获取用户画像成功")
                print(f"   画像: {json.dumps(result.get('profile', {}), indent=2, ensure_ascii=False)}")
                return result
            else:
                print(f"❌ 获取用户画像失败: {response.status_code}")
                print(f"   错误: {response.text[:500]}")
                return {}
    except Exception as e:
        print(f"❌ 获取用户画像失败: {e}")
        return {}


async def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试服务连接和功能")
    print("=" * 60)
    
    # 1. 测试服务健康状态
    print("\n【步骤 1】测试服务健康状态")
    cognee_ok = await test_service_health(COGNEE_URL, "Cognee")
    memobase_ok = await test_service_health(MEMOBASE_URL, "Memobase")
    mem0_ok = await test_service_health(MEM0_URL, "Mem0")
    poc_ok = await test_poc_service()
    
    # 2. 测试 API 功能
    print("\n【步骤 2】测试 API 功能")
    await test_cognee_api()
    await test_memobase_api()
    await test_mem0_api()
    
    # 3. 测试 POC 对话功能（如果 POC 服务运行）
    if poc_ok:
        print("\n【步骤 3】测试 POC 对话功能")
        conversation_result = await test_conversation()
        
        if conversation_result:
            user_id = conversation_result.get("user_id", "test_user_001")
            await test_user_profile(user_id)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 总结
    print("\n【测试总结】")
    print(f"Cognee:   {'✅' if cognee_ok else '❌'}")
    print(f"Memobase: {'✅' if memobase_ok else '❌'}")
    print(f"Mem0:     {'✅' if mem0_ok else '❌'}")
    print(f"POC:      {'✅' if poc_ok else '❌'}")


if __name__ == "__main__":
    asyncio.run(main())
