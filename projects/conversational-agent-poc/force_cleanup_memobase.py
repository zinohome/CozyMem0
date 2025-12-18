"""强制清理 Memobase 用户数据"""
import asyncio
import httpx
from memobase import MemoBaseClient
import uuid

# 服务地址配置
MEMOBASE_URL = "http://192.168.66.11:8019"
MEMOBASE_API_KEY = "secret"
TEST_USER_ID = "test_user_001"


def user_id_to_uuid(user_id: str) -> str:
    """将用户 ID 转换为 UUID 格式"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))


async def force_cleanup_memobase():
    """强制清理 Memobase 用户数据"""
    print("="*60)
    print("强制清理 Memobase 用户数据")
    print("="*60)
    
    uuid_user_id = user_id_to_uuid(TEST_USER_ID)
    print(f"\n用户信息:")
    print(f"  原始ID: {TEST_USER_ID}")
    print(f"  UUID: {uuid_user_id}")
    
    client = MemoBaseClient(
        project_url=MEMOBASE_URL,
        api_key=MEMOBASE_API_KEY
    )
    
    # 方法1：删除并重新创建用户
    print(f"\n方法1: 删除并重新创建用户...")
    try:
        # 先删除用户（使用 SDK）
        print(f"  正在删除用户...")
        try:
            # 尝试通过 API 删除
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                # 使用正确的认证方式
                headers = {"x-api-key": MEMOBASE_API_KEY}
                response = await http_client.delete(
                    f"{MEMOBASE_URL}/api/v1/users/{uuid_user_id}",
                    headers=headers
                )
                
                if response.status_code in [200, 204]:
                    print(f"  ✅ 用户删除成功")
                elif response.status_code == 404:
                    print(f"  ℹ️  用户不存在")
                else:
                    print(f"  ⚠️  删除返回: {response.status_code}")
                    print(f"     {response.text}")
        except Exception as e:
            print(f"  ⚠️  删除失败: {e}")
        
        # 等待一下
        await asyncio.sleep(2)
        
        # 重新创建干净的用户
        print(f"  正在创建新用户...")
        try:
            client.add_user(id=uuid_user_id, data={})
            print(f"  ✅ 新用户创建成功（空白状态）")
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg or "409" in error_msg:
                print(f"  ℹ️  用户已存在")
            else:
                print(f"  ⚠️  创建失败: {e}")
        
    except Exception as e:
        print(f"  ❌ 方法1失败: {e}")
    
    # 方法2：清空用户的所有内容
    print(f"\n方法2: 清空用户的所有内容...")
    try:
        user = client.get_user(uuid_user_id, no_get=True)
        
        # 清空缓冲区
        print(f"  清空缓冲区...")
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                headers = {"x-api-key": MEMOBASE_API_KEY}
                
                # 尝试清空聊天缓冲区
                response = await http_client.delete(
                    f"{MEMOBASE_URL}/api/v1/users/buffer/{uuid_user_id}/chat",
                    headers=headers
                )
                if response.status_code in [200, 204]:
                    print(f"  ✅ 聊天缓冲区已清空")
                
                # 尝试清空所有缓冲区
                response = await http_client.delete(
                    f"{MEMOBASE_URL}/api/v1/users/buffer/{uuid_user_id}",
                    headers=headers
                )
                if response.status_code in [200, 204]:
                    print(f"  ✅ 所有缓冲区已清空")
        except Exception as e:
            print(f"  ℹ️  清空缓冲区: {e}")
        
        # 尝试重置用户画像
        print(f"  重置用户画像...")
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                headers = {"x-api-key": MEMOBASE_API_KEY}
                
                # 尝试清空画像
                response = await http_client.delete(
                    f"{MEMOBASE_URL}/api/v1/users/profile/{uuid_user_id}",
                    headers=headers
                )
                if response.status_code in [200, 204]:
                    print(f"  ✅ 用户画像已清空")
                else:
                    print(f"  ℹ️  画像清空返回: {response.status_code}")
        except Exception as e:
            print(f"  ℹ️  重置画像: {e}")
        
    except Exception as e:
        print(f"  ❌ 方法2失败: {e}")
    
    # 等待 Memobase 处理
    print(f"\n等待 Memobase 处理（3秒）...")
    await asyncio.sleep(3)
    
    # 验证清理结果
    print(f"\n验证清理结果...")
    try:
        user = client.get_user(uuid_user_id, no_get=False)
        profile = user.profile(max_token_size=500)
        
        if not profile:
            print(f"  ✅ 用户画像已完全清空（None）")
        elif len(str(profile)) < 10:
            print(f"  ✅ 用户画像已清空（空数据）")
        else:
            print(f"  ⚠️  用户画像仍有数据:")
            print(f"     {str(profile)[:200]}...")
            print(f"\n  💡 提示：Memobase 可能需要更多时间处理，或需要手动清理")
    except Exception as e:
        error_msg = str(e)
        if "422" in error_msg or "404" in error_msg:
            print(f"  ✅ 用户不存在或画像已清空")
        else:
            print(f"  ⚠️  验证错误: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Memobase 强制清理完成")
    print(f"{'='*60}")
    print(f"\n建议:")
    print(f"  1. 如果仍有残留数据，可能需要在 Memobase 管理界面手动清理")
    print(f"  2. 或者使用不同的用户ID进行新的场景测试")
    print(f"  3. 运行 verify_cleanup.py 再次验证")


async def main():
    await force_cleanup_memobase()


if __name__ == "__main__":
    asyncio.run(main())
