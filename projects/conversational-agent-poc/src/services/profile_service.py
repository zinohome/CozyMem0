"""用户画像服务"""
from typing import Dict, Any, List
from ..clients import MemobaseClientWrapper


class ProfileService:
    """用户画像服务"""
    
    def __init__(self, memobase_client: MemobaseClientWrapper):
        self.memobase = memobase_client
    
    async def get_user_profile(
        self,
        user_id: str,
        max_token_size: int = 500
    ) -> Dict[str, Any]:
        """
        获取用户画像
        
        Args:
            user_id: 用户ID
            max_token_size: 最大token数量
        
        Returns:
            用户画像字典
        """
        # Memobase 客户端是同步的，需要在异步环境中运行
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.memobase.get_user_profile,
            user_id,
            max_token_size
        )
    
    async def extract_and_update_profile(
        self,
        user_id: str,
        messages: List[Dict[str, str]]
    ) -> None:
        """
        从对话中提取并更新用户画像
        
        Args:
            user_id: 用户ID
            messages: 对话消息列表
        """
        # Memobase 客户端是同步的，需要在异步环境中运行
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.memobase.extract_and_update_profile,
            user_id,
            messages
        )

