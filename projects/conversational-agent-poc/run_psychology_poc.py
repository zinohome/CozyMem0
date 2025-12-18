"""运行心理咨询 POC 自动化测试

执行三组对比测试：
1. 对照组 - 基础 LLM
2. 仅知识库组 - LLM + kb_psyc
3. 完整系统组 - LLM + kb_psyc + Memobase + Mem0
"""
import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 配置
POC_URL = "http://localhost:8080"
SESSION_DIR = Path("psychology_sessions")
RESULTS_DIR = Path("psychology_results")

# 测试组配置
TEST_GROUPS = {
    "baseline": {
        "name": "对照组（基础LLM）",
        "user_id": "xiaowan_baseline",
        "dataset_names": [],
        "role": "psychology_counselor",  # 使用心理咨询师角色
        "description": "不使用知识库、用户画像和会话记忆"
    },
    "kb_only": {
        "name": "仅知识库组（LLM + 知识库）",
        "user_id": "xiaowan_kb_only",
        "dataset_names": ["kb_psyc"],
        "role": "psychology_counselor",
        "description": "使用知识库，但不使用用户画像和会话记忆"
    },
    "full": {
        "name": "完整系统组（三种记忆全开）",
        "user_id": "xiaowan_full",
        "dataset_names": ["kb_psyc"],
        "role": "psychology_counselor",
        "description": "使用知识库、用户画像和会话记忆"
    }
}

# 会话文件
SESSION_FILES = [
    "session_1_initial_consultation.json",
    "session_2_deep_exploration.json",
    "session_3_consolidation.json"
]


def load_session_script(session_file: str) -> Dict[str, Any]:
    """加载会话脚本"""
    file_path = SESSION_DIR / session_file
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


async def run_conversation(
    group_id: str,
    session_id: int,
    conversation: List[Dict[str, Any]],
    config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """运行一个会话的对话"""
    results = []
    session_key = f"{config['user_id']}_session_{session_id}"
    
    print(f"\n  {'='*50}")
    print(f"  会话 {session_id} - 共 {len(conversation)} 轮对话")
    print(f"  {'='*50}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for round_data in conversation:
            round_num = round_data.get('round', 0)
            user_message = round_data.get('user_message', '')
            topic = round_data.get('topic', '')
            
            print(f"\n  第 {round_num} 轮 - {topic}")
            print(f"    用户: {user_message[:50]}...")
            
            try:
                # 调用 API
                response = await client.post(
                    f"{POC_URL}/api/v1/test/conversation",
                    json={
                        "user_id": config['user_id'],
                        "session_id": session_key,
                        "message": user_message,
                        "dataset_names": config['dataset_names'],
                        "role": config['role']
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get('response', '')
                    context = result.get('context', {})
                    
                    print(f"    咨询师: {ai_response[:80]}...")
                    
                    # 保存结果
                    results.append({
                        "round": round_num,
                        "topic": topic,
                        "user_message": user_message,
                        "user_emotion": round_data.get('user_emotion', ''),
                        "ai_response": ai_response,
                        "context": {
                            "user_profile_status": context.get('user_profile_status', ''),
                            "session_memories_count": context.get('session_memories_count', 0),
                            "knowledge_count": context.get('knowledge_count', 0)
                        },
                        "success": True
                    })
                    
                    # 等待一下，让系统处理
                    await asyncio.sleep(2)
                else:
                    print(f"    ❌ API 错误: {response.status_code}")
                    results.append({
                        "round": round_num,
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    })
            except Exception as e:
                print(f"    ❌ 错误: {e}")
                results.append({
                    "round": round_num,
                    "success": False,
                    "error": str(e)
                })
    
    return results


async def run_test_group(group_id: str, config: Dict[str, Any]):
    """运行一个测试组的所有会话"""
    print(f"\n{'='*60}")
    print(f"测试组: {config['name']}")
    print(f"{'='*60}")
    print(f"用户ID: {config['user_id']}")
    print(f"知识库: {config['dataset_names'] or '无'}")
    print(f"说明: {config['description']}")
    
    group_results = {
        "group_id": group_id,
        "group_name": config['name'],
        "config": config,
        "sessions": []
    }
    
    # 运行三个会话
    for i, session_file in enumerate(SESSION_FILES, 1):
        print(f"\n加载会话脚本: {session_file}")
        session_script = load_session_script(session_file)
        
        # 运行对话
        conversation_results = await run_conversation(
            group_id,
            i,
            session_script['conversation'],
            config
        )
        
        group_results['sessions'].append({
            "session_id": i,
            "session_name": session_script['session_info']['session_name'],
            "theme": session_script['session_info']['theme'],
            "conversation_results": conversation_results
        })
        
        # 会话间等待
        if i < len(SESSION_FILES):
            print(f"\n  ⏸️  会话间休息 5 秒...")
            await asyncio.sleep(5)
    
    return group_results


async def main():
    """主函数"""
    print("="*60)
    print("心理咨询 POC 自动化测试")
    print("="*60)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建结果目录
    RESULTS_DIR.mkdir(exist_ok=True)
    
    # 检查服务
    print(f"\n检查 POC 服务...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{POC_URL}/health")
            if response.status_code == 200:
                print(f"  ✅ POC 服务运行正常")
            else:
                print(f"  ❌ POC 服务异常: {response.status_code}")
                return
    except Exception as e:
        print(f"  ❌ POC 服务未运行: {e}")
        print(f"\n请先启动服务：./start_poc.sh")
        return
    
    # 检查会话脚本
    print(f"\n检查会话脚本...")
    for session_file in SESSION_FILES:
        file_path = SESSION_DIR / session_file
        if file_path.exists():
            print(f"  ✅ {session_file}")
        else:
            print(f"  ❌ {session_file} 不存在")
            return
    
    # 运行测试
    all_results = {
        "test_time": datetime.now().isoformat(),
        "test_groups": []
    }
    
    for group_id, config in TEST_GROUPS.items():
        try:
            group_results = await run_test_group(group_id, config)
            all_results['test_groups'].append(group_results)
        except Exception as e:
            print(f"\n❌ 测试组 {group_id} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = RESULTS_DIR / f"psychology_poc_results_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ 测试完成！")
    print(f"{'='*60}")
    print(f"\n结果已保存到: {result_file}")
    print(f"\n下一步:")
    print(f"  1. 查看测试结果: {result_file}")
    print(f"  2. 生成对比报告: python3 analyze_psychology_results.py")


if __name__ == "__main__":
    asyncio.run(main())
