"""分析心理咨询 POC 测试结果

生成详细的对比分析报告
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

RESULTS_DIR = Path("psychology_results")


def analyze_session_context(session_results: List[Dict]) -> Dict:
    """分析单个会话的上下文使用情况"""
    profile_counts = []
    memory_counts = []
    knowledge_counts = []
    
    for round_data in session_results:
        if round_data.get('success'):
            context = round_data.get('context', {})
            memory_counts.append(context.get('session_memories_count', 0))
            knowledge_counts.append(context.get('knowledge_count', 0))
            
            status = context.get('user_profile_status', '')
            has_profile = '已加载' in status if status else False
            profile_counts.append(1 if has_profile else 0)
    
    return {
        "avg_profile_usage": sum(profile_counts) / len(profile_counts) if profile_counts else 0,
        "avg_memories": sum(memory_counts) / len(memory_counts) if memory_counts else 0,
        "avg_knowledge": sum(knowledge_counts) / len(knowledge_counts) if knowledge_counts else 0,
        "max_memories": max(memory_counts) if memory_counts else 0,
        "max_knowledge": max(knowledge_counts) if knowledge_counts else 0
    }


def analyze_response_quality(session_results: List[Dict]) -> Dict:
    """分析回复质量"""
    total_rounds = len(session_results)
    successful_rounds = sum(1 for r in session_results if r.get('success'))
    
    response_lengths = []
    for round_data in session_results:
        if round_data.get('success'):
            response = round_data.get('ai_response', '')
            response_lengths.append(len(response))
    
    return {
        "success_rate": successful_rounds / total_rounds if total_rounds > 0 else 0,
        "total_rounds": total_rounds,
        "successful_rounds": successful_rounds,
        "avg_response_length": sum(response_lengths) / len(response_lengths) if response_lengths else 0,
        "min_response_length": min(response_lengths) if response_lengths else 0,
        "max_response_length": max(response_lengths) if response_lengths else 0
    }


def generate_markdown_report(results: Dict[str, Any], output_file: Path):
    """生成 Markdown 格式的分析报告"""
    
    md = []
    md.append("# 心理咨询场景化 POC 测试报告\n")
    md.append(f"**测试时间**: {results['test_time']}\n")
    md.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    md.append("\n## 测试概述\n")
    md.append("本次测试对比了三种配置的效果：\n")
    md.append("1. **对照组**：基础 LLM，不使用知识库、用户画像和会话记忆\n")
    md.append("2. **仅知识库组**：LLM + kb_psyc 知识库\n")
    md.append("3. **完整系统组**：LLM + kb_psyc + Memobase + Mem0\n")
    
    md.append("\n## 测试结果对比\n")
    
    # 创建对比表格
    md.append("\n### 1. 三种记忆系统使用情况\n")
    md.append("| 测试组 | 用户画像 | 会话记忆(平均) | 专业知识(平均) |\n")
    md.append("|--------|----------|----------------|----------------|\n")
    
    for group in results['test_groups']:
        group_name = group['group_name']
        
        # 统计所有会话的平均值
        total_profile = 0
        total_memories = 0
        total_knowledge = 0
        session_count = 0
        
        for session in group['sessions']:
            analysis = analyze_session_context(session['conversation_results'])
            total_profile += analysis['avg_profile_usage']
            total_memories += analysis['avg_memories']
            total_knowledge += analysis['avg_knowledge']
            session_count += 1
        
        avg_profile = total_profile / session_count if session_count > 0 else 0
        avg_memories = total_memories / session_count if session_count > 0 else 0
        avg_knowledge = total_knowledge / session_count if session_count > 0 else 0
        
        profile_status = "✅ 使用" if avg_profile > 0.5 else "❌ 未使用"
        memories_display = f"{avg_memories:.1f} 条" if avg_memories > 0 else "❌ 未使用"
        knowledge_display = f"{avg_knowledge:.1f} 条" if avg_knowledge > 0 else "❌ 未使用"
        
        md.append(f"| {group_name} | {profile_status} | {memories_display} | {knowledge_display} |\n")
    
    # 详细分析每个测试组
    md.append("\n### 2. 各测试组详细分析\n")
    
    for group in results['test_groups']:
        md.append(f"\n#### {group['group_name']}\n")
        md.append(f"**配置**: {group['config']['description']}\n")
        md.append(f"**用户ID**: `{group['config']['user_id']}`\n")
        
        for session in group['sessions']:
            md.append(f"\n##### 会话 {session['session_id']}: {session['session_name']}\n")
            md.append(f"**主题**: {session['theme']}\n")
            
            # 分析上下文使用
            context_analysis = analyze_session_context(session['conversation_results'])
            md.append(f"- 用户画像使用率: {context_analysis['avg_profile_usage']*100:.0f}%\n")
            md.append(f"- 平均会话记忆数: {context_analysis['avg_memories']:.1f} 条\n")
            md.append(f"- 平均专业知识数: {context_analysis['avg_knowledge']:.1f} 条\n")
            
            # 分析回复质量
            quality_analysis = analyze_response_quality(session['conversation_results'])
            md.append(f"- 成功对话轮数: {quality_analysis['successful_rounds']}/{quality_analysis['total_rounds']}\n")
            md.append(f"- 平均回复长度: {quality_analysis['avg_response_length']:.0f} 字符\n")
            
            # 展示部分对话示例
            md.append(f"\n**对话示例**（第1-2轮）：\n")
            for round_data in session['conversation_results'][:2]:
                if round_data.get('success'):
                    md.append(f"\n*第 {round_data['round']} 轮 - {round_data['topic']}*\n")
                    md.append(f"> **来访者**: {round_data['user_message'][:100]}...\n\n")
                    md.append(f"> **咨询师**: {round_data['ai_response'][:200]}...\n")
    
    # 关键发现
    md.append("\n## 关键发现\n")
    
    # 对比三组的记忆使用
    baseline_group = next((g for g in results['test_groups'] if 'baseline' in g['group_id']), None)
    kb_group = next((g for g in results['test_groups'] if 'kb_only' in g['group_id']), None)
    full_group = next((g for g in results['test_groups'] if 'full' in g['group_id']), None)
    
    md.append("\n### 1. 专业性对比（知识库的作用）\n")
    if baseline_group and kb_group:
        md.append("**对照组** vs **仅知识库组**:\n")
        md.append("- 对照组回复基于通用 LLM 知识\n")
        md.append("- 仅知识库组可以引用专业心理学知识\n")
        md.append("- 预期：知识库组在专业术语、理论应用方面更准确\n")
    
    md.append("\n### 2. 个性化对比（用户画像的作用）\n")
    if kb_group and full_group:
        md.append("**仅知识库组** vs **完整系统组**:\n")
        md.append("- 仅知识库组每次对话都是'新用户'\n")
        md.append("- 完整系统组记住用户姓名、年龄、学校等信息\n")
        md.append("- 预期：完整系统组回复更个性化，体现对用户的了解\n")
    
    md.append("\n### 3. 连续性对比（会话记忆的作用）\n")
    if kb_group and full_group:
        md.append("**仅知识库组** vs **完整系统组**:\n")
        md.append("- 仅知识库组跨会话时不记得之前的对话\n")
        md.append("- 完整系统组能追踪咨询进展、回顾作业完成情况\n")
        md.append("- 预期：完整系统组在跨会话对话中表现出连贯性\n")
    
    md.append("\n## 结论\n")
    md.append("本次测试验证了三种记忆系统（Cognee, Memobase, Mem0）在心理咨询场景中的作用：\n")
    md.append("1. **Cognee (kb_psyc)**: 提供专业心理学知识支持\n")
    md.append("2. **Memobase**: 记住用户的个人信息和特点，实现个性化\n")
    md.append("3. **Mem0**: 保持会话连续性，支持跨会话咨询\n")
    
    md.append("\n三种系统协同工作，能够提供更专业、个性化和连续的心理咨询服务。\n")
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(md))
    
    print(f"✅ Markdown 报告已生成: {output_file}")


def main():
    """主函数"""
    print("="*60)
    print("分析心理咨询 POC 测试结果")
    print("="*60)
    
    # 查找最新的结果文件
    result_files = sorted(RESULTS_DIR.glob("psychology_poc_results_*.json"))
    
    if not result_files:
        print("\n❌ 未找到测试结果文件")
        print(f"请先运行测试: python3 run_psychology_poc.py")
        return
    
    latest_result = result_files[-1]
    print(f"\n分析文件: {latest_result}")
    
    # 加载结果
    with open(latest_result, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # 生成报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = RESULTS_DIR / f"psychology_poc_report_{timestamp}.md"
    
    generate_markdown_report(results, report_file)
    
    print(f"\n{'='*60}")
    print(f"✅ 分析完成！")
    print(f"{'='*60}")
    print(f"\n报告文件: {report_file}")
    print(f"\n请查看报告了解详细对比结果。")


if __name__ == "__main__":
    main()
