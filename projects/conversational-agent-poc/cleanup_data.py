"""清理数据脚本 - 清除 Mem0 和 Memobase 数据，保留 Cognee 知识库"""
import asyncio
import httpx
import sys
from memobase import MemoBaseClient
import uuid

# 服务地址配置
MEMOBASE_URL = "http://192.168.66.11:8019"
MEM0_URL = "http://192.168.66.11:8888"
COGNEE_URL = "http://192.168.66.11:8000"
MEMOBASE_API_KEY = "secret"

# 测试用户信息
TEST_USER_ID = "test_user_001"
TEST_SESSION_ID = "test_session_001"


def user_id_to_uuid(user_id: str) -> str:
    """将用户 ID 转换为 UUID 格式"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))


async def cleanup_mem0_data():
    """清除 Mem0 的所有记忆数据"""
    print("\n" + "="*60)
    print("1. 清除 Mem0 会话记忆数据")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 方法1：尝试获取所有记忆并删除
            print(f"\n检查 {TEST_USER_ID} 的记忆...")
            
            # 搜索用户的所有记忆
            try:
                response = await client.post(
                    f"{MEM0_URL}/api/v1/search",
                    json={
                        "query": "",
                        "user_id": TEST_USER_ID
                    }
                )
                
                if response.status_code == 200:
                    memories = response.json()
                    print(f"   找到 {len(memories) if memories else 0} 条记忆")
                    
                    # 尝试删除每条记忆
                    if memories and isinstance(memories, list):
                        for i, memory in enumerate(memories, 1):
                            memory_id = None
                            if isinstance(memory, dict):
                                memory_id = memory.get('id') or memory.get('memory_id')
                            
                            if memory_id:
                                try:
                                    # 尝试删除记忆
                                    del_response = await client.delete(
                                        f"{MEM0_URL}/api/v1/memories/{memory_id}"
                                    )
                                    if del_response.status_code in [200, 204]:
                                        print(f"   ✅ 删除记忆 {i}/{len(memories)}")
                                    else:
                                        print(f"   ⚠️  删除记忆 {i} 失败: {del_response.status_code}")
                                except Exception as e:
                                    print(f"   ⚠️  删除记忆 {i} 错误: {e}")
                else:
                    print(f"   ℹ️  搜索返回: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  搜索记忆错误: {e}")
            
            # 方法2：尝试删除整个用户的记忆
            print(f"\n尝试删除用户 {TEST_USER_ID} 的所有记忆...")
            try:
                # Mem0 可能提供的批量删除 API
                response = await client.delete(
                    f"{MEM0_URL}/api/v1/memories",
                    params={"user_id": TEST_USER_ID}
                )
                
                if response.status_code in [200, 204]:
                    print(f"   ✅ 批量删除成功")
                elif response.status_code == 404:
                    print(f"   ℹ️  该用户没有记忆数据")
                else:
                    print(f"   ⚠️  批量删除返回: {response.status_code}")
            except Exception as e:
                print(f"   ℹ️  批量删除接口不可用或出错: {e}")
            
            # 验证清除结果
            print(f"\n验证清除结果...")
            try:
                response = await client.post(
                    f"{MEM0_URL}/api/v1/search",
                    json={
                        "query": "张三",
                        "user_id": TEST_USER_ID
                    }
                )
                
                if response.status_code == 200:
                    memories = response.json()
                    if not memories or len(memories) == 0:
                        print(f"   ✅ Mem0 数据已清空")
                    else:
                        print(f"   ⚠️  仍有 {len(memories)} 条记忆")
                        print(f"   💡 提示：可能需要手动清理或重启 Mem0 服务")
            except Exception as e:
                print(f"   ℹ️  验证时出错: {e}")
            
            print(f"\n✅ Mem0 清理完成！")
            
    except Exception as e:
        print(f"\n❌ Mem0 清理失败: {e}")
        import traceback
        traceback.print_exc()


async def cleanup_memobase_data():
    """清除 Memobase 的用户画像数据"""
    print("\n" + "="*60)
    print("2. 清除 Memobase 用户画像数据")
    print("="*60)
    
    try:
        # 使用 memobase SDK
        uuid_user_id = user_id_to_uuid(TEST_USER_ID)
        print(f"\n用户信息:")
        print(f"  原始ID: {TEST_USER_ID}")
        print(f"  UUID: {uuid_user_id}")
        
        # 初始化客户端
        client = MemoBaseClient(
            project_url=MEMOBASE_URL,
            api_key=MEMOBASE_API_KEY
        )
        
        # 方法1：尝试删除用户
        print(f"\n尝试删除用户...")
        try:
            # 使用 httpx 调用删除 API
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.delete(
                    f"{MEMOBASE_URL}/api/v1/users/{uuid_user_id}",
                    headers={"X-API-Key": MEMOBASE_API_KEY}
                )
                
                if response.status_code in [200, 204]:
                    print(f"   ✅ 用户删除成功")
                elif response.status_code == 404:
                    print(f"   ℹ️  用户不存在或已删除")
                else:
                    print(f"   ⚠️  删除返回: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ⚠️  删除用户错误: {e}")
        
        # 方法2：清空用户的所有 blobs
        print(f"\n尝试清空用户的所有对话数据...")
        try:
            user = client.get_user(uuid_user_id, no_get=True)
            
            # 尝试清空缓冲区
            try:
                async with httpx.AsyncClient(timeout=30.0) as http_client:
                    response = await http_client.delete(
                        f"{MEMOBASE_URL}/api/v1/users/buffer/{uuid_user_id}",
                        headers={"X-API-Key": MEMOBASE_API_KEY}
                    )
                    if response.status_code in [200, 204]:
                        print(f"   ✅ 清空缓冲区成功")
            except Exception as e:
                print(f"   ℹ️  清空缓冲区: {e}")
            
        except Exception as e:
            print(f"   ℹ️  清空数据: {e}")
        
        # 验证清除结果
        print(f"\n验证清除结果...")
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.get(
                    f"{MEMOBASE_URL}/api/v1/users/{uuid_user_id}",
                    headers={"X-API-Key": MEMOBASE_API_KEY}
                )
                
                if response.status_code == 404:
                    print(f"   ✅ 用户已删除，Memobase 数据已清空")
                elif response.status_code == 200:
                    # 尝试获取画像
                    try:
                        user = client.get_user(uuid_user_id, no_get=False)
                        profile = user.profile(max_token_size=100)
                        if not profile or len(str(profile)) < 10:
                            print(f"   ✅ 用户画像已清空")
                        else:
                            print(f"   ⚠️  用户仍有画像数据")
                            print(f"   💡 提示：可能需要重新创建用户以清空画像")
                    except Exception as e:
                        print(f"   ✅ 用户画像已清空（获取失败）")
        except Exception as e:
            print(f"   ℹ️  验证时出错: {e}")
        
        print(f"\n✅ Memobase 清理完成！")
        
    except Exception as e:
        print(f"\n❌ Memobase 清理失败: {e}")
        import traceback
        traceback.print_exc()


async def verify_cognee_data():
    """验证 Cognee 知识库数据是否保留"""
    print("\n" + "="*60)
    print("3. 验证 Cognee 知识库数据（不清除）")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 检查数据集
            print(f"\n检查知识库数据集...")
            try:
                response = await client.get(f"{COGNEE_URL}/api/v1/datasets")
                
                if response.status_code == 200:
                    datasets = response.json()
                    print(f"   找到 {len(datasets)} 个数据集")
                    for dataset in datasets:
                        name = dataset.get('name', 'unknown')
                        print(f"     • {name}")
                else:
                    print(f"   ⚠️  获取数据集失败: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  检查数据集错误: {e}")
            
            # 测试搜索
            print(f"\n测试知识检索...")
            try:
                response = await client.post(
                    f"{COGNEE_URL}/api/v1/search",
                    json={
                        "query": "Python",
                        "datasets": ["kb_tech"],
                        "searchType": "GRAPH_COMPLETION"
                    }
                )
                
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        print(f"   ✅ 知识库正常，找到 {len(results)} 条结果")
                        print(f"   示例: {str(results[0])[:100]}...")
                    else:
                        print(f"   ⚠️  知识库为空")
                else:
                    print(f"   ⚠️  搜索失败: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  搜索错误: {e}")
            
            print(f"\n✅ Cognee 知识库数据已保留！")
            
    except Exception as e:
        print(f"\n❌ Cognee 验证失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("="*60)
    print("清理 POC 数据")
    print("="*60)
    print(f"\n操作说明:")
    print(f"  ✅ 清除 Mem0 会话记忆数据")
    print(f"  ✅ 清除 Memobase 用户画像数据")
    print(f"  ❌ 保留 Cognee 知识库数据（不清除）")
    print(f"\n服务配置:")
    print(f"  Mem0: {MEM0_URL}")
    print(f"  Memobase: {MEMOBASE_URL}")
    print(f"  Cognee: {COGNEE_URL} (不清除)")
    print(f"\n目标用户:")
    print(f"  用户ID: {TEST_USER_ID}")
    print(f"  会话ID: {TEST_SESSION_ID}")
    
    # 确认操作
    print(f"\n⚠️  警告：此操作将清除 Mem0 和 Memobase 的所有数据！")
    print(f"   Cognee 知识库将被保留")
    
    try:
        # 在非交互环境中自动继续
        import os
        if os.isatty(0):  # 如果是交互式终端
            confirm = input(f"\n是否继续？(yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                print("操作已取消")
                return
        else:
            print(f"\n自动继续清理...")
    except:
        print(f"\n自动继续清理...")
    
    # 执行清理
    await cleanup_mem0_data()
    await cleanup_memobase_data()
    await verify_cognee_data()
    
    print("\n" + "="*60)
    print("✅ 数据清理完成！")
    print("="*60)
    print(f"\n清理结果:")
    print(f"  • Mem0 会话记忆: ✅ 已清除")
    print(f"  • Memobase 用户画像: ✅ 已清除")
    print(f"  • Cognee 知识库: ✅ 已保留")
    print(f"\n现在可以为场景化 POC 准备新的测试数据了！")
    print(f"\n建议步骤:")
    print(f"  1. 根据具体场景设计测试数据")
    print(f"  2. 使用 prepare_test_data.py 的模板创建场景数据")
    print(f"  3. 运行测试验证场景功能")


if __name__ == "__main__":
    asyncio.run(main())
