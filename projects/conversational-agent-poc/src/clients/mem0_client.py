"""Mem0 客户端封装"""
import asyncio
from typing import List, Dict, Any, Optional
from mem0 import AsyncMemoryClient
from ..config import settings


class Mem0ClientWrapper:
    """Mem0 客户端封装类"""
    
    def __init__(self):
        self.client = AsyncMemoryClient(
            api_key=settings.mem0_api_key,
            host=settings.mem0_api_url
        ) if settings.mem0_api_key else None
    
    async def get_conversation_context(
        self,
        user_id: str,
        session_id: str,
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取会话上下文（并发获取当前会话和跨会话记忆）
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            query: 查询文本
        
        Returns:
            记忆列表
        """
        if not self.client or not query:
            return []
        
        try:
            # 并发获取当前会话记忆和跨会话记忆
            current_memories, cross_memories = await asyncio.gather(
                self.client.search(
                    query=query,
                    user_id=user_id,
                    agent_id=session_id,
                    limit=10
                ),
                self.client.search(
                    query=query,
                    user_id=user_id,
                    limit=5
                ),
                return_exceptions=True
            )
            
            memories = []
            
            if not isinstance(current_memories, Exception):
                memories.extend([
                    {
                        "content": result.memory,
                        "type": result.memory_type,
                        "session": "current",
                        "timestamp": str(result.created_at) if hasattr(result, 'created_at') else None
                    }
                    for result in current_memories
                ])
            
            if not isinstance(cross_memories, Exception):
                memories.extend([
                    {
                        "content": result.memory,
                        "type": result.memory_type,
                        "session": "cross",
                        "timestamp": str(result.created_at) if hasattr(result, 'created_at') else None
                    }
                    for result in cross_memories
                ])
            
            # 按时间排序
            memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return memories[:15]
        except Exception as e:
            print(f"Error getting conversation context: {e}")
            return []
    
    async def save_conversation(
        self,
        user_id: str,
        session_id: str,
        messages: List[Dict[str, str]],
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        保存会话记忆
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            messages: 消息列表
            metadata: 元数据
        """
        if not self.client:
            return
        
        try:
            await self.client.add(
                messages=messages,
                user_id=user_id,
                agent_id=session_id,
                metadata=metadata
            )
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.close()

