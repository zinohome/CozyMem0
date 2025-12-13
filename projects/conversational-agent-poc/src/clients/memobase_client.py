"""Memobase 客户端封装"""
from typing import Dict, Any, List
from memobase import MemoBaseClient, ChatBlob
from ..config import settings


class MemobaseClientWrapper:
    """Memobase 客户端封装类"""
    
    def __init__(self):
        self.client = MemoBaseClient(
            project_url=settings.memobase_project_url,
            api_key=settings.memobase_api_key
        )
    
    def get_user_profile(
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
        try:
            user = self.client.get_or_create_user(user_id)
            profile = user.profile(
                max_token_size=max_token_size,
                prefer_topics=["basic_info", "interest", "work"]
            )
            return profile if profile else {}
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return {}
    
    def extract_and_update_profile(
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
        try:
            user = self.client.get_or_create_user(user_id)
            blob = ChatBlob(messages=messages)
            user.insert(blob)
            user.flush()
        except Exception as e:
            print(f"Error updating user profile: {e}")

