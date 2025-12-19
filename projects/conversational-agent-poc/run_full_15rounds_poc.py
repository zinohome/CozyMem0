#!/usr/bin/env python3
"""
运行完整的 15 轮心理咨询 POC
展示完整记忆框架在深度咨询中的应用
"""
import asyncio
import httpx
import json
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


API_BASE_URL = "http://localhost:8080"  # POC 服务端口
SESSION_FILE = "psychology_sessions/session_full_15rounds.json"
RESULTS_DIR = Path("psychology_results")

# 全局输出收集器
output_lines = []


def log_print(text: str = ""):
    """打印并记录到输出收集器"""
    print(text)
    output_lines.append(text)


def print_header(text: str, char: str = "=", width: int = 80):
    """打印格式化标题"""
    log_print(f"\n{char * width}")
    log_print(f"{text:^{width}}")
    log_print(f"{char * width}\n")


def print_round_header(round_num: int, total: int):
    """打印轮次标题"""
    log_print(f"\n{'━' * 80}")
    log_print(f"💬 第 {round_num}/{total} 轮对话")
    log_print(f"{'━' * 80}")


def print_context_summary(context: Dict[str, Any]):
    """打印上下文摘要（简化版，仅显示条数）"""
    # 用户画像
    profile = context.get("user_profile", {})
    profile_count = len(profile) if isinstance(profile, dict) else 0
    
    # 会话记忆
    memories = context.get("session_memories", [])
    memories_count = len(memories)
    
    # 专业知识
    knowledge = context.get("knowledge", [])
    knowledge_count = len(knowledge)
    
    log_print(f"   📊 记忆系统: 画像 {profile_count} 项 | 记忆 {memories_count} 条 | 知识 {knowledge_count} 条")


def wrap_text(text: str, width: int = 78, initial_indent: str = "  ", subsequent_indent: str = "  ") -> str:
    """
    自动换行文本（支持中文）
    
    Args:
        text: 要换行的文本
        width: 每行最大宽度（默认78，加上缩进2字符共80字符，与分隔线对齐）
        initial_indent: 首行缩进
        subsequent_indent: 后续行缩进
    
    Returns:
        换行后的文本
    """
    # 处理多段落（以换行符分隔）
    paragraphs = text.split('\n')
    wrapped_paragraphs = []
    
    for para in paragraphs:
        if not para.strip():  # 空行保留
            wrapped_paragraphs.append("")
            continue
            
        # 手动处理中文换行
        lines = []
        current_line = initial_indent if not lines else subsequent_indent
        
        for char in para:
            # 计算字符宽度（中文字符算2个宽度，英文算1个）
            char_width = 2 if ord(char) > 127 else 1
            current_line_width = sum(2 if ord(c) > 127 else 1 for c in current_line)
            
            # 如果加上当前字符会超过宽度限制，开始新行
            if current_line_width + char_width > width:
                lines.append(current_line)
                current_line = subsequent_indent + char
            else:
                current_line += char
        
        # 添加最后一行
        if current_line.strip():
            lines.append(current_line)
        
        wrapped_paragraphs.append('\n'.join(lines))
    
    return '\n'.join(wrapped_paragraphs)


def print_conversation(user_msg: str, ai_response: str, context: Dict[str, Any]):
    """打印对话内容"""
    log_print(f"\n👧 江小婉:")
    # 对用户消息进行换行处理（78字符+2字符缩进=80字符总长度）
    wrapped_user_msg = wrap_text(user_msg, width=78)
    log_print(wrapped_user_msg)
    
    log_print(f"\n🧑‍⚕️ 陈老师:")
    # 对AI回复进行换行处理（78字符+2字符缩进=80字符总长度）
    wrapped_ai_response = wrap_text(ai_response, width=78)
    log_print(wrapped_ai_response)
    
    print_context_summary(context)


async def run_conversation_round(
    client: httpx.AsyncClient,
    round_data: Dict[str, Any],
    session_id: str,
    user_id: str,
    dataset_names: list,
    role: str,
    round_num: int,
    total_rounds: int
) -> Dict[str, Any]:
    """运行单轮对话"""
    print_round_header(round_num, total_rounds)
    
    user_message = round_data["user_message"]
    
    # 打印期望的行为
    expected_behavior = round_data.get("expected_behavior", [])
    if expected_behavior:
        log_print(f"\n🎯 本轮期望行为:")
        for behavior in expected_behavior:
            log_print(f"  • {behavior}")
    
    # 调用 API
    start_time = datetime.now()
    
    try:
        response = await client.post(
            f"{API_BASE_URL}/api/v1/test/conversation",
            json={
                "user_id": user_id,
                "session_id": session_id,
                "message": user_message,
                "dataset_names": dataset_names,
                "role": role
            },
            timeout=60.0
        )
        response.raise_for_status()
        result = response.json()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # 打印对话
        print_conversation(
            user_message,
            result["response"],
            result["context"]
        )
        
        return {
            "round": round_num,
            "user_message": user_message,
            "ai_response": result["response"],
            "context": result["context"],
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        import traceback
        error_msg = str(e) if str(e) else repr(e)
        error_detail = traceback.format_exc()
        
        log_print(f"❌ 第 {round_num} 轮失败: {error_msg}")
        log_print(f"   错误详情: {error_detail[:200]}...")
        
        return {
            "round": round_num,
            "error": error_msg,
            "error_detail": error_detail,
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """主函数"""
    # 清空输出收集器
    global output_lines
    output_lines = []
    
    print_header("🌟 15 轮完整心理咨询 POC 🌟", char="=")
    
    # 读取会话脚本
    log_print("📖 加载会话脚本...")
    with open(SESSION_FILE, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    session_info = session_data["session_info"]
    user_profile = session_data["user_profile"]
    conversations = session_data["conversation"]
    
    log_print(f"✅ 加载成功")
    log_print(f"  会话ID: {session_info['session_id']}")
    log_print(f"  用户: {user_profile['name']} ({user_profile['age']}岁, {user_profile['grade']})")
    log_print(f"  总轮数: {len(conversations)}")
    log_print(f"  知识库: {session_info['dataset_names']}")
    log_print(f"  关注领域: {', '.join(session_info['focus_areas'][:3])}...")
    
    # 确认继续
    log_print(f"\n⚠️  这将执行 {len(conversations)} 轮对话，预计耗时 2-3 分钟")
    input("按 Enter 键开始...")
    
    # 创建客户端
    async with httpx.AsyncClient() as client:
        results = []
        total_rounds = len(conversations)
        
        start_time = datetime.now()
        
        # 逐轮执行
        for i, round_data in enumerate(conversations, 1):
            result = await run_conversation_round(
                client=client,
                round_data=round_data,
                session_id=session_info["session_id"],
                user_id=session_info["user_id"],
                dataset_names=session_info["dataset_names"],
                role=session_info["role"],
                round_num=i,
                total_rounds=total_rounds
            )
            results.append(result)
            
            # 短暂延迟，避免过载
            if i < total_rounds:
                await asyncio.sleep(1)
        
        total_elapsed = (datetime.now() - start_time).total_seconds()
        
        # 打印总结
        print_header("📊 POC 执行总结", char="=")
        
        successful_rounds = [r for r in results if "error" not in r]
        failed_rounds = [r for r in results if "error" in r]
        
        log_print(f"✅ 成功轮数: {len(successful_rounds)}/{total_rounds}")
        log_print(f"❌ 失败轮数: {len(failed_rounds)}/{total_rounds}")
        log_print(f"⏱️  总耗时: {total_elapsed:.2f} 秒")
        
        if successful_rounds:
            avg_time = sum(r["elapsed_seconds"] for r in successful_rounds) / len(successful_rounds)
            log_print(f"📊 平均响应时间: {avg_time:.2f} 秒/轮")
        
        # 保存结果
        RESULTS_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = RESULTS_DIR / f"full_15rounds_poc_{timestamp}.json"
        
        full_result = {
            "session_info": session_info,
            "user_profile": user_profile,
            "execution_time": start_time.isoformat(),
            "total_elapsed_seconds": total_elapsed,
            "total_rounds": total_rounds,
            "successful_rounds": len(successful_rounds),
            "failed_rounds": len(failed_rounds),
            "rounds": results
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(full_result, f, ensure_ascii=False, indent=2)
        
        log_print(f"\n💾 JSON 结果已保存: {result_file}")
        
        # 保存文本文件
        text_file = RESULTS_DIR / f"full_15rounds_poc_{timestamp}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        log_print(f"📄 文本记录已保存: {text_file}")
        
        # 生成简要报告
        print_header("📋 记忆系统使用分析", char="=")
        
        if successful_rounds:
            # 统计记忆使用
            profile_usage = []
            memory_usage = []
            knowledge_usage = []
            
            for r in successful_rounds:
                context = r.get("context", {})
                profile = context.get("user_profile", {})
                memories = context.get("session_memories", [])
                knowledge = context.get("knowledge", [])
                
                profile_usage.append(len(profile) if isinstance(profile, dict) else 0)
                memory_usage.append(len(memories))
                knowledge_usage.append(len(knowledge))
            
            log_print(f"👤 用户画像使用:")
            log_print(f"   平均: {sum(profile_usage)/len(profile_usage):.1f} 个字段/轮")
            log_print(f"   范围: {min(profile_usage)} - {max(profile_usage)}")
            
            log_print(f"\n🧠 会话记忆使用:")
            log_print(f"   平均: {sum(memory_usage)/len(memory_usage):.1f} 条/轮")
            log_print(f"   范围: {min(memory_usage)} - {max(memory_usage)}")
            log_print(f"   趋势: {'递增' if memory_usage[-1] > memory_usage[0] else '稳定'} (首轮: {memory_usage[0]}, 末轮: {memory_usage[-1]})")
            
            log_print(f"\n📚 专业知识使用:")
            log_print(f"   平均: {sum(knowledge_usage)/len(knowledge_usage):.1f} 条/轮")
            log_print(f"   范围: {min(knowledge_usage)} - {max(knowledge_usage)}")
        
        print_header("✅ POC 完成！", char="=")
        log_print(f"📦 输出文件:")
        log_print(f"  JSON: {result_file}")
        log_print(f"  文本: {text_file}")
        log_print(f"\n💡 可以使用以下命令查看详细分析:")
        log_print(f"  python3 analyze_psychology_results.py")


if __name__ == "__main__":
    asyncio.run(main())
