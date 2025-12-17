"""测试 mem0 AsyncMemoryClient 的实际 API 路径"""
import asyncio
from mem0 import AsyncMemoryClient

async def test_mem0_client():
    """测试 AsyncMemoryClient 使用的 API 路径"""
    # 使用您的 mem0 服务地址
    host = "http://192.168.66.11:8000"
    
    print(f"测试 AsyncMemoryClient 配置")
    print(f"Host: {host}")
    print()
    
    # 创建客户端（不需要 api_key，因为 mem0 服务器可能不需要）
    client = AsyncMemoryClient(host=host)
    
    # 检查客户端的内部配置
    print("检查客户端属性:")
    for attr in dir(client):
        if not attr.startswith('_') and 'url' in attr.lower() or 'base' in attr.lower() or 'host' in attr.lower():
            try:
                value = getattr(client, attr)
                if not callable(value):
                    print(f"  {attr}: {value}")
            except:
                pass
    
    # 尝试搜索（这会触发实际的 API 调用）
    print("\n尝试搜索（测试 API 路径）:")
    try:
        result = await client.search(
            query="test",
            user_id="test_user",
            limit=1
        )
        print(f"✅ 搜索成功，返回 {len(result)} 条结果")
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_mem0_client())
