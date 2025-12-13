"""会话记忆服务"""
from typing import List, Dict, Any, Optional
from ..clients import Mem0ClientWrapper


class MemoryService:
    """会话记忆服务"""
    
    def __init__(self, mem0_client: Mem0ClientWrapper):
        self.mem0 = mem0_client
    
    async def get_conversation_context(
        self,
        user_id: str,
        session_id: str,
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取会话上下文
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            query: 查询文本
        
        Returns:
            记忆列表
        """
        return await self.mem0.get_conversation_context(
            user_id=user_id,
            session_id=session_id,
            query=query
        )
    
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
        await self.mem0.save_conversation(
            user_id=user_id,
            session_id=session_id,
            messages=messages,
            metadata=metadata
        )

