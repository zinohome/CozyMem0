"""Prompt 模板"""
from typing import Dict, Any, List


def build_conversation_prompt(
    user_profile: Dict[str, Any],
    session_memories: List[Dict[str, Any]],
    knowledge: List[Dict[str, Any]],
    user_message: str
) -> str:
    """
    构建对话 Prompt
    
    Args:
        user_profile: 用户画像
        session_memories: 会话记忆
        knowledge: 专业知识
        user_message: 用户消息
    
    Returns:
        构建好的 Prompt
    """
    prompt_parts = []
    
    # 用户画像
    if user_profile:
        prompt_parts.append("# 用户画像")
        prompt_parts.append(str(user_profile))
        prompt_parts.append("")
    
    # 相关记忆
    if session_memories:
        prompt_parts.append("# 相关记忆")
        for memory in session_memories[:10]:  # 最多10条
            content = memory.get("content", "")
            session_type = memory.get("session", "unknown")
            prompt_parts.append(f"- [{session_type}] {content}")
        prompt_parts.append("")
    
    # 专业知识
    if knowledge:
        prompt_parts.append("# 专业知识")
        for item in knowledge[:5]:  # 最多5条
            content = item.get("content", "")
            source = item.get("source", "unknown")
            prompt_parts.append(f"- [{source}] {content}")
        prompt_parts.append("")
    
    # 用户消息
    prompt_parts.append("# 对话")
    prompt_parts.append(f"用户: {user_message}")
    prompt_parts.append("助手: ")
    
    return "\n".join(prompt_parts)


def get_system_prompt() -> str:
    """获取系统 Prompt"""
    return """你是一个智能助手，能够：
1. 基于用户画像提供个性化回答
2. 利用专业知识库回答专业问题
3. 记住并参考历史对话内容
4. 提供友好、专业的服务

请根据用户画像、相关记忆和专业知识，提供准确、有用的回答。"""

