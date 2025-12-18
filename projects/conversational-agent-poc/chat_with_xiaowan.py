"""与江小婉进行心理咨询对话（使用完整记忆系统）

使用完整的三种记忆系统：
- Cognee (kb_psyc): 专业心理学知识
- Memobase: 用户画像
- Mem0: 会话记忆
"""
import asyncio
import httpx
import json
from datetime import datetime

# 配置
POC_URL = "http://localhost:8080"

# ========================================
# 选择测试组（请只取消一组的注释）
# ========================================

# 【对照组】基础 LLM - 不使用任何记忆系统
# USER_ID = "xiaowan_baseline"
# DATASET_NAMES = []  # ❌ 不使用知识库

# 【仅知识库组】LLM + kb_psyc
# USER_ID = "xiaowan_kb_only"
# DATASET_NAMES = ["kb_psyc"]  # ✅ 使用知识库

# 【完整系统组】LLM + kb_psyc + Memobase + Mem0（推荐）
USER_ID = "xiaowan_full"
DATASET_NAMES = ["kb_psyc"]  # ✅ 使用知识库

SESSION_ID = f"manual_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
ROLE = "psychology_counselor"  # 心理咨询师角色


async def send_message(message: str):
    """发送消息并获取回复"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{POC_URL}/api/v1/test/conversation",
                json={
                    "user_id": USER_ID,
                    "session_id": SESSION_ID,
                    "message": message,
                    "dataset_names": DATASET_NAMES,
                    "role": ROLE
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API 错误: {response.status_code}")
                print(f"   {response.text}")
                return None
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return None


def display_context(context: dict):
    """显示上下文信息（三种记忆系统的使用情况）- 简要版"""
    print(f"\n{'='*60}")
    print(f"📊 三种记忆系统使用情况（简要）")
    print(f"{'='*60}")
    
    # 1. Memobase 用户画像
    print(f"\n🎭 Memobase 用户画像:")
    status = context.get('user_profile_status', '未知')
    print(f"   状态: {status}")
    
    if context.get('user_profile'):
        profile = context['user_profile']
        print(f"   画像字段数: {len(profile)} 个")
        for key, value in list(profile.items())[:3]:  # 只显示前3个
            print(f"   - {key}: {str(value)[:50]}...")
    
    # 2. Mem0 会话记忆
    print(f"\n💭 Mem0 会话记忆:")
    mem_count = context.get('session_memories_count', 0)
    mem_status = context.get('session_memories_status', '未知')
    print(f"   状态: {mem_status}")
    print(f"   记忆数: {mem_count} 条")
    
    if context.get('session_memories'):
        memories = context['session_memories']
        print(f"   最近记忆:")
        for i, mem in enumerate(memories[:2], 1):  # 只显示前2条
            content = mem.get('content', '')
            print(f"   {i}. {content[:60]}...")
    
    # 3. Cognee 知识库
    print(f"\n📚 Cognee 知识库:")
    kb_count = context.get('knowledge_count', 0)
    kb_status = context.get('knowledge_status', '未知')
    print(f"   状态: {kb_status}")
    print(f"   知识数: {kb_count} 条")
    
    if context.get('knowledge'):
        knowledge = context['knowledge']
        print(f"   检索到的知识:")
        for i, item in enumerate(knowledge[:2], 1):  # 只显示前2条
            content = item.get('content', '')
            score = item.get('score', 0)
            print(f"   {i}. (相关度: {score:.2f}) {content[:50]}...")
    
    print(f"\n💡 输入 'full' 查看完整内容")
    print(f"{'='*60}\n")


def display_full_context(context: dict):
    """显示完整的上下文信息（三种记忆系统的详细内容）"""
    print(f"\n{'='*60}")
    print(f"📋 三种记忆系统完整内容")
    print(f"{'='*60}")
    
    # 1. Memobase 用户画像 - 完整
    print(f"\n🎭 【Memobase 用户画像】完整内容")
    print(f"{'─'*60}")
    status = context.get('user_profile_status', '未知')
    print(f"状态: {status}\n")
    
    if context.get('user_profile'):
        profile = context['user_profile']
        print(f"共 {len(profile)} 个字段:\n")
        for key, value in profile.items():
            print(f"📌 {key}:")
            if isinstance(value, (dict, list)):
                import json
                print(json.dumps(value, ensure_ascii=False, indent=2))
            else:
                print(f"   {value}")
            print()
    else:
        print("   暂无画像数据\n")
    
    # 2. Mem0 会话记忆 - 完整
    print(f"\n💭 【Mem0 会话记忆】完整内容")
    print(f"{'─'*60}")
    mem_count = context.get('session_memories_count', 0)
    mem_status = context.get('session_memories_status', '未知')
    print(f"状态: {mem_status}")
    print(f"总记忆数: {mem_count} 条\n")
    
    if context.get('session_memories'):
        memories = context['session_memories']
        print(f"显示前 {len(memories)} 条记忆:\n")
        for i, mem in enumerate(memories, 1):
            content = mem.get('content', '')
            memory_type = mem.get('type', 'unknown')
            session = mem.get('session', 'unknown')
            print(f"记忆 #{i}")
            print(f"  类型: {memory_type}")
            print(f"  会话: {session}")
            print(f"  内容: {content}")
            print()
    else:
        print("   暂无记忆数据\n")
    
    # 3. Cognee 知识库 - 完整
    print(f"\n📚 【Cognee 知识库】完整内容")
    print(f"{'─'*60}")
    kb_count = context.get('knowledge_count', 0)
    kb_status = context.get('knowledge_status', '未知')
    print(f"状态: {kb_status}")
    print(f"总知识数: {kb_count} 条\n")
    
    if context.get('knowledge'):
        knowledge = context['knowledge']
        print(f"显示 {len(knowledge)} 条检索结果:\n")
        for i, item in enumerate(knowledge, 1):
            content = item.get('content', '')
            score = item.get('score', 0)
            source = item.get('source', 'unknown')
            print(f"知识 #{i}")
            print(f"  来源: {source}")
            print(f"  相关度: {score:.4f}")
            print(f"  内容:")
            # 限制显示长度，避免太长
            if len(content) > 500:
                print(f"    {content[:500]}...")
                print(f"    ... (完整内容共 {len(content)} 字符)")
            else:
                print(f"    {content}")
            print()
    else:
        print("   暂无知识数据\n")
    
    print(f"{'='*60}\n")


async def main():
    """主函数"""
    global SESSION_ID  # 声明全局变量
    
    print("="*60)
    print("🌸 江小婉心理咨询对话系统")
    print("="*60)
    
    # 显示当前配置
    print(f"\n📋 当前配置:")
    print(f"  用户ID: {USER_ID}")
    print(f"  会话ID: {SESSION_ID}")
    print(f"  知识库: {DATASET_NAMES if DATASET_NAMES else '❌ 不使用'}")
    print(f"  角色: {ROLE}")
    
    # 显示测试组说明
    if USER_ID == "xiaowan_baseline":
        print(f"\n  🔵 当前模式: 对照组（基础LLM）")
        print(f"     - ❌ 不使用知识库")
        print(f"     - ❌ 不使用用户画像")
        print(f"     - ❌ 不使用会话记忆")
    elif USER_ID == "xiaowan_kb_only":
        print(f"\n  🟡 当前模式: 仅知识库组（LLM + 知识库）")
        print(f"     - ✅ 使用知识库 (kb_psyc)")
        print(f"     - ❌ 不使用用户画像")
        print(f"     - ❌ 不使用会话记忆")
    elif USER_ID == "xiaowan_full":
        print(f"\n  🟢 当前模式: 完整系统组（三种记忆全开）")
        print(f"     - ✅ 使用知识库 (kb_psyc)")
        print(f"     - ✅ 使用用户画像 (Memobase)")
        print(f"     - ✅ 使用会话记忆 (Mem0)")
    else:
        print(f"\n  ⚪ 当前模式: 自定义")
        print(f"     - 知识库: {'✅' if DATASET_NAMES else '❌'}")
        print(f"     - 用户画像: 取决于用户ID")
        print(f"     - 会话记忆: 取决于用户ID")
    
    print(f"\n{'='*60}")
    print("📋 使用说明")
    print("="*60)
    print("1. 输入你的消息（作为江小婉）")
    print("2. 系统会调用三种记忆系统")
    print("3. 心理咨询师（陈老师）会回复你")
    print("4. 输入 'exit' 或 'quit' 退出")
    print("5. 输入 'context' 查看记忆系统简要信息")
    print("6. 输入 'full' 查看记忆系统完整内容（包括所有记忆和知识）")
    print("7. 输入 'clear' 开始新会话")
    
    print(f"\n{'='*60}")
    print("💡 建议开场白")
    print("="*60)
    print("- 你好老师，我是江小婉，最近学习压力特别大")
    print("- 陈老师，我又来了，最近好一些了")
    print("- 老师，我按你说的做了，想跟你说说")
    
    print(f"\n{'='*60}\n")
    
    conversation_count = 0
    last_context = None
    
    while True:
        try:
            # 获取用户输入
            user_input = input("🙋 小婉: ")
            
            # 处理特殊命令
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 咨询结束，祝你一切顺利！")
                break
            
            if user_input.lower() == 'context':
                if last_context:
                    display_context(last_context)
                else:
                    print("⚠️  还没有对话记录")
                continue
            
            if user_input.lower() == 'full':
                if last_context:
                    display_full_context(last_context)
                else:
                    print("⚠️  还没有对话记录")
                continue
            
            if user_input.lower() == 'clear':
                SESSION_ID = f"manual_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                print(f"\n✅ 新会话已创建: {SESSION_ID}\n")
                conversation_count = 0
                last_context = None
                continue
            
            if not user_input.strip():
                continue
            
            # 发送消息
            print("\n⏳ 咨询师正在思考...\n")
            result = await send_message(user_input)
            
            if result:
                conversation_count += 1
                
                # 显示咨询师回复
                ai_response = result.get('response', '')
                print(f"🧑‍⚕️  陈老师: {ai_response}\n")
                
                # 保存上下文
                last_context = result.get('context', {})
                
                # 简要显示记忆系统使用情况
                context = last_context
                mem_count = context.get('session_memories_count', 0)
                kb_count = context.get('knowledge_count', 0)
                has_profile = '已加载' in context.get('user_profile_status', '')
                
                print(f"📊 [第{conversation_count}轮] ", end="")
                print(f"画像: {'✅' if has_profile else '❌'} | ", end="")
                print(f"记忆: {mem_count}条 | ", end="")
                print(f"知识: {kb_count}条")
                print(f"   (输入 'context' 查看详情 | 输入 'full' 查看完整内容)\n")
                print("="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 咨询结束，祝你一切顺利！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}\n")
    
    # 结束统计
    if conversation_count > 0:
        print(f"\n{'='*60}")
        print(f"📈 本次咨询统计")
        print(f"{'='*60}")
        print(f"对话轮数: {conversation_count} 轮")
        print(f"会话ID: {SESSION_ID}")
        
        if last_context:
            mem_count = last_context.get('session_memories_count', 0)
            print(f"累积记忆: {mem_count} 条")
        
        print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
