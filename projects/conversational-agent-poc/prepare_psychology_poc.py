"""准备心理咨询 POC 数据

为三个测试组准备基础用户画像：
1. 对照组 (baseline) - 不注入任何数据
2. 仅知识库组 (kb_only) - 不注入画像，只使用 kb_psyc
3. 完整系统组 (full) - 注入基础画像，使用所有系统
"""
import asyncio
import json
from memobase import MemoBaseClient, ChatBlob
import uuid

# 服务配置
MEMOBASE_URL = "http://192.168.66.11:8019"
MEMOBASE_API_KEY = "secret"

# 用户配置
BASE_USER_PROFILE = {
    "name": "江小婉",
    "age": 15,
    "gender": "女",
    "location": "北京市",
    "school": "某重点中学",
    "grade": "高一",
    "personality": "软弱、内向",
    "main_challenges": "学习压力大，与家人和同学沟通困难"
}

# 三个测试组的用户ID
USERS = {
    "baseline": "xiaowan_baseline",  # 对照组
    "kb_only": "xiaowan_kb_only",    # 仅知识库组
    "full": "xiaowan_full"             # 完整系统组
}


def user_id_to_uuid(user_id: str) -> str:
    """将用户 ID 转换为 UUID 格式"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))


async def prepare_base_profile(user_id: str):
    """为用户注入基础画像"""
    print(f"\n{'='*60}")
    print(f"为用户 {user_id} 注入基础画像")
    print(f"{'='*60}")
    
    uuid_user_id = user_id_to_uuid(user_id)
    print(f"  原始ID: {user_id}")
    print(f"  UUID: {uuid_user_id}")
    
    try:
        client = MemoBaseClient(
            project_url=MEMOBASE_URL,
            api_key=MEMOBASE_API_KEY
        )
        
        # 创建用户
        print(f"\n  创建用户...")
        try:
            client.add_user(id=uuid_user_id, data={})
            print(f"  ✅ 用户创建成功")
        except Exception as e:
            if "already exists" in str(e) or "409" in str(e):
                print(f"  ℹ️  用户已存在")
            else:
                print(f"  ⚠️  创建用户警告: {e}")
        
        # 获取用户对象
        user = client.get_user(uuid_user_id, no_get=True)
        
        # 准备基础画像对话
        print(f"\n  注入基础画像数据...")
        base_conversations = [
            # 基本信息（模拟用户自我介绍）
            [
                {"role": "user", "content": f"你好老师，我叫{BASE_USER_PROFILE['name']}，是个{BASE_USER_PROFILE['gender']}孩子，今年{BASE_USER_PROFILE['age']}岁"},
                {"role": "assistant", "content": f"你好{BASE_USER_PROFILE['name']}，很高兴认识你。欢迎来到咨询室。"}
            ],
            # 学校信息
            [
                {"role": "user", "content": f"我在{BASE_USER_PROFILE['location']}{BASE_USER_PROFILE['school']}上学，现在读{BASE_USER_PROFILE['grade']}"},
                {"role": "assistant", "content": "高中阶段确实是压力比较大的时期，很多同学都会有各种困扰。"}
            ],
            # 性格特点
            [
                {"role": "user", "content": f"我性格比较{BASE_USER_PROFILE['personality']}，很多时候不太会表达自己的情绪"},
                {"role": "assistant", "content": "谢谢你愿意跟我分享这些。每个人都有自己的性格特点，这很正常。"}
            ],
            # 主要困扰
            [
                {"role": "user", "content": f"最近{BASE_USER_PROFILE['main_challenges']}，感觉压力很大"},
                {"role": "assistant", "content": "我理解你的感受。我们可以一起来看看如何应对这些困扰。"}
            ]
        ]
        
        # 插入对话
        for i, messages in enumerate(base_conversations, 1):
            try:
                blob = ChatBlob(messages=messages)
                user.insert(blob)
                print(f"    ✅ 基础信息 {i}/{len(base_conversations)} 注入成功")
            except Exception as e:
                print(f"    ❌ 基础信息 {i} 注入失败: {e}")
        
        # 刷新保存
        print(f"\n  保存数据...")
        try:
            user.flush()
            print(f"  ✅ 数据保存成功")
        except Exception as e:
            print(f"  ⚠️  保存警告: {e}")
        
        # 等待处理
        print(f"\n  等待 Memobase 处理（3秒）...")
        await asyncio.sleep(3)
        
        # 验证画像
        print(f"\n  验证画像生成...")
        try:
            profile = user.profile(max_token_size=300)
            if profile:
                print(f"  ✅ 用户画像生成成功")
                print(f"\n  画像内容预览:")
                print(f"  {str(profile)[:200]}...")
            else:
                print(f"  ⚠️  画像为空")
        except Exception as e:
            print(f"  ⚠️  获取画像错误: {e}")
        
        print(f"\n✅ 用户 {user_id} 基础画像准备完成")
        
    except Exception as e:
        print(f"\n❌ 准备失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("="*60)
    print("心理咨询 POC 数据准备")
    print("="*60)
    
    print(f"\n将准备以下测试组：")
    print(f"  1. 对照组 (baseline): {USERS['baseline']}")
    print(f"     - 不使用知识库")
    print(f"     - 不注入画像（新用户，空画像）")
    print(f"     - 不使用记忆（新会话，空记忆）")
    
    print(f"\n  2. 仅知识库组 (kb_only): {USERS['kb_only']}")
    print(f"     - 使用 kb_psyc 知识库")
    print(f"     - 不注入画像（新用户，空画像）")
    print(f"     - 不使用记忆（新会话，空记忆）")
    
    print(f"\n  3. 完整系统组 (full): {USERS['full']}")
    print(f"     - 使用 kb_psyc 知识库")
    print(f"     - 注入基础画像")
    print(f"     - 会话记忆自动积累")
    
    # 基础画像内容
    print(f"\n基础画像内容：")
    print(json.dumps(BASE_USER_PROFILE, indent=2, ensure_ascii=False))
    
    # 确认
    print(f"\n{'='*60}")
    confirm = input("是否继续准备数据？(yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("操作已取消")
        return
    
    # 准备数据
    print(f"\n开始准备数据...\n")
    
    # 为所有测试组创建 Memobase 用户（必须！否则会有外键约束错误）
    print(f"{'='*60}")
    print(f"为所有测试组创建 Memobase 用户")
    print(f"{'='*60}")
    
    client = MemoBaseClient(
        project_url=MEMOBASE_URL,
        api_key=MEMOBASE_API_KEY
    )
    
    # 1. 对照组 - 只创建用户，不注入数据
    print(f"\n1. 对照组: {USERS['baseline']}")
    try:
        uuid_baseline = user_id_to_uuid(USERS['baseline'])
        client.add_user(id=uuid_baseline, data={})
        print(f"  ✅ 用户创建成功（空画像）")
    except Exception as e:
        if "already exists" in str(e) or "409" in str(e):
            print(f"  ℹ️  用户已存在")
        else:
            print(f"  ⚠️  创建失败: {e}")
    
    # 2. 仅知识库组 - 只创建用户，不注入数据
    print(f"\n2. 仅知识库组: {USERS['kb_only']}")
    try:
        uuid_kb_only = user_id_to_uuid(USERS['kb_only'])
        client.add_user(id=uuid_kb_only, data={})
        print(f"  ✅ 用户创建成功（空画像）")
    except Exception as e:
        if "already exists" in str(e) or "409" in str(e):
            print(f"  ℹ️  用户已存在")
        else:
            print(f"  ⚠️  创建失败: {e}")
    
    # 3. 完整系统组：创建用户并注入基础画像
    print(f"\n3. 完整系统组:")
    await prepare_base_profile(USERS['full'])
    
    print(f"\n{'='*60}")
    print(f"✅ 数据准备完成！")
    print(f"{'='*60}")
    
    print(f"\n下一步：")
    print(f"  1. 运行自动化测试: python3 run_psychology_poc.py")
    print(f"  2. 查看对比报告")


if __name__ == "__main__":
    asyncio.run(main())
