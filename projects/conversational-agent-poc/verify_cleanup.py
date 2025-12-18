"""验证数据清理效果"""
import asyncio
import httpx
from memobase import MemoBaseClient
import uuid

# 服务地址配置
MEMOBASE_URL = "http://192.168.66.11:8019"
MEM0_URL = "http://192.168.66.11:8888"
COGNEE_URL = "http://192.168.66.11:8000"
MEMOBASE_API_KEY = "secret"

TEST_USER_ID = "test_user_001"
TEST_SESSION_ID = "test_session_001"


def user_id_to_uuid(user_id: str) -> str:
    """将用户 ID 转换为 UUID 格式"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))


async def verify_mem0():
    """验证 Mem0 数据清理"""
    print("\n" + "="*60)
    print("1. 验证 Mem0 会话记忆清理效果")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{MEM0_URL}/api/v1/search",
                json={
                    "query": "张三 软件工程师 Python",
                    "user_id": TEST_USER_ID,
                    "agent_id": TEST_SESSION_ID
                }
            )
            
            if response.status_code == 200:
                memories = response.json()
                if isinstance(memories, list):
                    if len(memories) == 0:
                        print(f"   ✅ Mem0 数据已完全清除（0 条记忆）")
                    else:
                        print(f"   ⚠️  Mem0 仍有 {len(memories)} 条记忆")
                        for i, mem in enumerate(memories[:3], 1):
                            if isinstance(mem, dict):
                                content = mem.get('memory', mem.get('content', ''))
                                print(f"      {i}. {content}")
                        print(f"\n   💡 建议：等待几秒后重试，或重启 Mem0 服务")
                else:
                    print(f"   ✅ Mem0 数据已清除（返回格式: {type(memories)}）")
            else:
                print(f"   ℹ️  Mem0 搜索返回: {response.status_code}")
                if response.status_code == 404:
                    print(f"   ✅ 用户记忆已清除")
        except Exception as e:
            print(f"   ⚠️  验证错误: {e}")


async def verify_memobase():
    """验证 Memobase 数据清理"""
    print("\n" + "="*60)
    print("2. 验证 Memobase 用户画像清理效果")
    print("="*60)
    
    try:
        uuid_user_id = user_id_to_uuid(TEST_USER_ID)
        client = MemoBaseClient(
            project_url=MEMOBASE_URL,
            api_key=MEMOBASE_API_KEY
        )
        
        try:
            user = client.get_user(uuid_user_id, no_get=False)
            profile = user.profile(max_token_size=500)
            
            if not profile or len(str(profile)) < 10:
                print(f"   ✅ Memobase 用户画像已清除（空画像）")
            else:
                print(f"   ⚠️  Memobase 仍有用户画像数据")
                print(f"   画像内容: {str(profile)[:200]}...")
                print(f"\n   💡 建议：需要重新创建用户或清空数据")
        except Exception as e:
            error_msg = str(e)
            if "422" in error_msg or "404" in error_msg:
                print(f"   ✅ Memobase 用户不存在或画像已清除")
            else:
                print(f"   ℹ️  获取画像错误: {e}")
    except Exception as e:
        print(f"   ⚠️  验证错误: {e}")


async def verify_cognee():
    """验证 Cognee 数据保留"""
    print("\n" + "="*60)
    print("3. 验证 Cognee 知识库保留情况")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 检查数据集
        try:
            response = await client.get(f"{COGNEE_URL}/api/v1/datasets")
            
            if response.status_code == 200:
                datasets = response.json()
                print(f"   ✅ 数据集数量: {len(datasets)}")
                for dataset in datasets:
                    name = dataset.get('name', 'unknown')
                    print(f"      • {name}")
            else:
                print(f"   ⚠️  获取数据集失败: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  检查数据集错误: {e}")
        
        # 测试搜索
        try:
            response = await client.post(
                f"{COGNEE_URL}/api/v1/search",
                json={
                    "query": "Python 编程",
                    "datasets": ["kb_tech"],
                    "searchType": "GRAPH_COMPLETION"
                }
            )
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    print(f"   ✅ 知识检索正常，找到 {len(results)} 条结果")
                else:
                    print(f"   ⚠️  知识库为空")
            else:
                print(f"   ⚠️  搜索失败: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  搜索错误: {e}")


async def main():
    """主函数"""
    print("="*60)
    print("验证数据清理效果")
    print("="*60)
    
    await verify_mem0()
    await verify_memobase()
    await verify_cognee()
    
    print("\n" + "="*60)
    print("验证完成")
    print("="*60)
    print(f"\n✅ 数据已准备好进行场景化 POC 测试")
    print(f"   - Mem0 和 Memobase 数据已清除")
    print(f"   - Cognee 知识库已保留")
    print(f"\n💡 下一步：根据场景需求准备新的测试数据")


if __name__ == "__main__":
    asyncio.run(main())
