#!/usr/bin/env python3
"""
Memobase 用户画像生成测试脚本

这个脚本演示如何：
1. 创建用户
2. 插入对话数据
3. 刷新数据（触发画像生成）
4. 获取用户画像
"""
import asyncio
import uuid
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from memobase import MemoBaseClient, ChatBlob
from src.config import settings


def user_id_to_uuid(user_id: str) -> str:
    """将任意用户ID转换为UUID v5格式"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_json(data, title: str = "数据"):
    """格式化打印JSON数据"""
    print(f"\n{title}:")
    # 处理UserProfile对象
    if hasattr(data, '__dict__'):
        # 尝试转换为字典
        try:
            if hasattr(data, 'dict'):
                data = data.dict()
            elif hasattr(data, 'model_dump'):
                data = data.model_dump()
            else:
                # 手动转换
                data = {k: str(v) for k, v in data.__dict__.items()}
        except:
            data = str(data)
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def test_profile_generation():
    """测试用户画像生成"""
    
    print_section("Memobase 用户画像生成测试")
    
    # 1. 初始化客户端
    print("\n[1] 初始化 Memobase 客户端")
    # 使用实际的服务地址
    project_url = "http://192.168.66.11:8019"
    api_key = settings.memobase_api_key
    print(f"   Project URL: {project_url}")
    print(f"   API Key: {api_key[:10]}..." if len(api_key) > 10 else f"   API Key: {api_key}")
    
    client = MemoBaseClient(
        project_url=project_url,
        api_key=api_key
    )
    
    # 测试连接
    try:
        ping_result = client.ping()
        print(f"   ✓ 连接成功: {ping_result}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
        return
    
    # 2. 创建测试用户
    print("\n[2] 创建/获取测试用户")
    test_user_id = "profile_test_user_001"
    uuid_user_id = user_id_to_uuid(test_user_id)
    print(f"   原始用户ID: {test_user_id}")
    print(f"   UUID格式: {uuid_user_id}")
    
    try:
        # 尝试获取用户
        try:
            user = client.get_user(uuid_user_id, no_get=False)
            print("   ✓ 用户已存在，获取成功")
        except Exception as e:
            # 用户不存在，创建新用户
            print("   ℹ 用户不存在，创建新用户...")
            created_id = client.add_user(id=uuid_user_id, data={
                "name": "测试用户",
                "source": "profile_test"
            })
            print(f"   ✓ 用户创建成功: {created_id}")
            user = client.get_user(uuid_user_id, no_get=True)
    except Exception as e:
        print(f"   ✗ 创建/获取用户失败: {e}")
        return
    
    # 3. 检查初始画像（应该为空）
    print("\n[3] 检查初始用户画像")
    try:
        initial_profile = user.profile(max_token_size=500)
        if initial_profile:
            print_json(initial_profile, "初始画像")
        else:
            print("   初始画像为空（正常，因为还没有对话数据）")
    except Exception as e:
        print(f"   ℹ 获取初始画像: {e}")
    
    # 4. 插入对话数据
    print("\n[4] 插入对话数据（用于生成画像）")
    
    # 准备多轮对话，包含丰富的用户信息
    conversations = [
        # 第一轮：基本信息
        [
            {"role": "user", "content": "你好，我是张三，今年28岁，是一名软件工程师，在北京工作。"},
            {"role": "assistant", "content": "很高兴认识你，张三！作为一名软件工程师，你的工作一定很有趣。你在北京工作多久了？"}
        ],
        # 第二轮：兴趣爱好
        [
            {"role": "user", "content": "我在北京工作3年了。我喜欢编程，特别是Python和JavaScript。业余时间我喜欢阅读和打篮球。"},
            {"role": "assistant", "content": "听起来很棒！Python和JavaScript都是很流行的语言。你平时读什么类型的书？"}
        ],
        # 第三轮：工作相关
        [
            {"role": "user", "content": "我喜欢读技术书籍和科幻小说。我在一家互联网公司做后端开发，主要负责API设计和数据库优化。"},
            {"role": "assistant", "content": "后端开发是很有挑战性的工作。你在工作中遇到的最大挑战是什么？"}
        ],
        # 第四轮：个人偏好
        [
            {"role": "user", "content": "最大的挑战是处理高并发场景。我比较喜欢使用Docker和Kubernetes来部署应用。另外，我习惯用MacBook Pro进行开发。"},
            {"role": "assistant", "content": "高并发确实是个挑战。Docker和K8s是现代开发的标准工具。你还有什么其他想分享的吗？"}
        ],
        # 第五轮：更多信息
        [
            {"role": "user", "content": "我还喜欢学习新技术，最近在研究机器学习和AI。我的邮箱是zhangsan@example.com，电话是13800138000。"},
            {"role": "assistant", "content": "机器学习是个很有前景的领域。感谢你分享这些信息！"}
        ]
    ]
    
    print(f"   准备插入 {len(conversations)} 轮对话...")
    
    for i, messages in enumerate(conversations, 1):
        try:
            blob = ChatBlob(messages=messages)
            user.insert(blob)
            print(f"   ✓ 第 {i} 轮对话插入成功")
        except Exception as e:
            print(f"   ✗ 第 {i} 轮对话插入失败: {e}")
    
    # 5. 刷新数据（同步处理，触发画像生成）
    print("\n[5] 刷新数据（同步处理，触发画像生成）")
    print("   注意：使用 sync=True 确保数据立即处理...")
    
    try:
        user.flush(sync=True)
        print("   ✓ 数据刷新成功，画像应该已经生成")
    except Exception as e:
        print(f"   ✗ 数据刷新失败: {e}")
        return
    
    # 等待一下，确保处理完成
    import time
    print("   等待 3 秒，确保画像处理完成...")
    time.sleep(3)
    
    # 6. 获取生成的画像
    print("\n[6] 获取生成的用户画像")
    
    try:
        # 尝试不同的参数获取画像
        print("\n   尝试1: 使用need_json=True（推荐）")
        try:
            profile1 = user.profile(need_json=True)
            if profile1:
                print_json(profile1, "用户画像（JSON格式）")
            else:
                print("   画像为空")
        except Exception as e:
            print(f"   获取JSON格式画像失败: {e}")
            # 如果need_json不支持，尝试其他方式
        
        print("\n   尝试2: 使用默认参数，然后转换为字符串")
        try:
            profile2 = user.profile()
            if profile2:
                # UserProfile对象，尝试转换为可读格式
                print(f"   画像类型: {type(profile2)}")
                if hasattr(profile2, 'dict'):
                    print_json(profile2.dict(), "用户画像（字典格式）")
                elif hasattr(profile2, 'model_dump'):
                    print_json(profile2.model_dump(), "用户画像（Pydantic格式）")
                else:
                    print(f"   画像内容: {str(profile2)}")
            else:
                print("   画像为空")
        except Exception as e:
            print(f"   获取画像失败: {e}")
        
        print("\n   尝试3: 指定max_token_size和prefer_topics")
        try:
            profile3 = user.profile(
                max_token_size=1000,
                prefer_topics=["basic_info", "interest", "work", "contact"]
            )
            if profile3:
                if hasattr(profile3, 'dict'):
                    print_json(profile3.dict(), "用户画像（指定参数）")
                elif hasattr(profile3, 'model_dump'):
                    print_json(profile3.model_dump(), "用户画像（指定参数）")
                else:
                    print(f"   画像内容: {str(profile3)}")
            else:
                print("   画像为空")
        except Exception as e:
            print(f"   获取画像失败: {e}")
        
    except Exception as e:
        print(f"   ✗ 获取画像失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. 再次刷新并获取（确保数据已处理）
    print("\n[7] 再次刷新并获取画像（确保数据已完全处理）")
    
    try:
        user.flush(sync=True)
        time.sleep(2)
        
        # 使用need_json=True获取最终画像
        try:
            final_profile = user.profile(need_json=True, max_token_size=1000)
            if final_profile:
                print_json(final_profile, "最终用户画像")
                print("\n✓ 画像生成成功！")
            else:
                print("\n⚠ 画像仍然为空，可能需要更多对话数据或检查配置")
        except:
            # 如果need_json不支持，尝试普通方式
            final_profile = user.profile(max_token_size=1000)
            if final_profile:
                if hasattr(final_profile, 'dict'):
                    print_json(final_profile.dict(), "最终用户画像")
                elif hasattr(final_profile, 'model_dump'):
                    print_json(final_profile.model_dump(), "最终用户画像")
                else:
                    print(f"\n最终画像: {str(final_profile)}")
                print("\n✓ 画像生成成功！")
            else:
                print("\n⚠ 画像仍然为空，可能需要更多对话数据或检查配置")
    except Exception as e:
        print(f"   ✗ 最终获取失败: {e}")
    
    # 8. 获取用户事件历史（验证数据已插入）
    print("\n[8] 验证：获取用户事件历史")
    
    try:
        events = user.event()
        if events:
            print(f"   ✓ 找到 {len(events)} 个事件")
            print(f"   最新事件: {events[0] if events else '无'}")
        else:
            print("   ℹ 事件列表为空")
    except Exception as e:
        print(f"   ℹ 获取事件失败: {e}")
    
    print_section("测试完成")
    print(f"\n用户ID: {test_user_id}")
    print(f"UUID: {uuid_user_id}")
    print(f"\n你可以通过以下方式查看用户画像：")
    print(f"1. 使用SDK: user.profile()")
    print(f"2. 通过POC API: GET /api/v1/users/{test_user_id}/profile")
    print(f"3. 通过Memobase API: GET /api/v1/users/{uuid_user_id}/profile (如果支持)")


if __name__ == "__main__":
    try:
        test_profile_generation()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
