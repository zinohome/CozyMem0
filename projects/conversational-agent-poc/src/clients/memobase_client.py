"""Memobase 客户端封装"""
import uuid
from typing import Dict, Any, List
from memobase import MemoBaseClient, ChatBlob
from ..config import settings


def user_id_to_uuid(user_id: str) -> str:
    """
    将任意用户 ID 转换为 UUID v5 格式
    
    Memobase API 要求 user_id 必须是 UUID v4 或 v5 格式。
    这个函数使用 UUID v5 (基于 SHA-1) 将任意字符串转换为确定性的 UUID。
    
    Args:
        user_id: 原始用户 ID（任意字符串）
    
    Returns:
        UUID v5 格式的字符串
    """
    # 使用 UUID v5 (基于 SHA-1)，使用 DNS 命名空间
    # 这样同一个 user_id 总是生成相同的 UUID
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))


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
            user_id: 用户ID（任意字符串，会自动转换为 UUID 格式）
            max_token_size: 最大token数量
        
        Returns:
            用户画像字典
        """
        # 将 user_id 转换为 UUID 格式（Memobase API 要求）
        uuid_user_id = user_id_to_uuid(user_id)
        
        try:
            # 尝试获取用户
            user = self.client.get_user(uuid_user_id, no_get=False)
            
            # 尝试使用 need_json=True 获取JSON格式的画像
            try:
                profile = user.profile(
                    need_json=True,
                    max_token_size=max_token_size,
                    prefer_topics=["basic_info", "interest", "work"]
                )
                # need_json=True 应该返回字典，但需要处理UUID等不可序列化类型
                if profile:
                    return self._serialize_profile(profile)
                return {}
            except (TypeError, AttributeError):
                # 如果 need_json 不支持，尝试普通方式并转换
                profile = user.profile(
                    max_token_size=max_token_size,
                    prefer_topics=["basic_info", "interest", "work"]
                )
                if profile:
                    return self._serialize_profile(profile)
                return {}
        except Exception as e:
            # 用户不存在或其他错误，返回空画像
            import logging
            logger = logging.getLogger(__name__)
            error_msg = str(e)
            if "422" in error_msg or "Unprocessable Entity" in error_msg or "404" in error_msg:
                logger.debug(f"User {user_id} (UUID: {uuid_user_id}) not found in Memobase (normal for new users)")
            else:
                logger.warning(f"Error getting user profile for {user_id} (UUID: {uuid_user_id}): {e}")
            return {}
    
    def _serialize_profile(self, profile: Any) -> Dict[str, Any]:
        """
        序列化profile对象为字典，处理UUID等不可序列化类型
        
        Args:
            profile: profile对象或字典
        
        Returns:
            可序列化的字典
        """
        import uuid
        from datetime import datetime
        
        if isinstance(profile, dict):
            result = {}
            for key, value in profile.items():
                result[key] = self._serialize_value(value)
            return result
        elif hasattr(profile, 'dict'):
            return self._serialize_profile(profile.dict())
        elif hasattr(profile, 'model_dump'):
            return self._serialize_profile(profile.model_dump())
        else:
            # 如果无法转换，尝试转换为字符串
            return {"raw": str(profile)}
    
    def _serialize_value(self, value: Any) -> Any:
        """
        序列化单个值，处理UUID、datetime等类型
        
        Args:
            value: 要序列化的值
        
        Returns:
            可序列化的值
        """
        import uuid
        from datetime import datetime
        
        if isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif hasattr(value, 'dict'):
            return self._serialize_value(value.dict())
        elif hasattr(value, 'model_dump'):
            return self._serialize_value(value.model_dump())
        else:
            return value
    
    def extract_and_update_profile(
        self,
        user_id: str,
        messages: List[Dict[str, str]]
    ) -> None:
        """
        从对话中提取并更新用户画像
        
        Args:
            user_id: 用户ID（任意字符串，会自动转换为 UUID 格式）
            messages: 对话消息列表
        """
        # 将 user_id 转换为 UUID 格式（Memobase API 要求）
        uuid_user_id = user_id_to_uuid(user_id)
        
        try:
            # 先尝试获取用户，如果不存在则创建
            user = None
            try:
                user = self.client.get_user(uuid_user_id, no_get=False)
            except Exception as get_error:
                # 如果用户不存在（422 或其他错误），尝试创建用户
                import logging
                logger = logging.getLogger(__name__)
                error_msg = str(get_error)
                if "422" in error_msg or "Unprocessable Entity" in error_msg or "404" in error_msg:
                    logger.info(f"User {user_id} (UUID: {uuid_user_id}) not found, creating new user in Memobase")
                    try:
                        # 使用 add_user 创建用户（使用 UUID 格式）
                        self.client.add_user(id=uuid_user_id, data={})
                        user = self.client.get_user(uuid_user_id, no_get=True)
                    except Exception as create_error:
                        logger.warning(f"Failed to create user {user_id} (UUID: {uuid_user_id}) in Memobase: {create_error}")
                        # 如果创建失败，使用 no_get=True 继续尝试
                        user = self.client.get_user(uuid_user_id, no_get=True)
                else:
                    # 其他错误，使用 no_get=True 继续尝试
                    logger.warning(f"Error getting user {user_id} (UUID: {uuid_user_id}): {get_error}")
                    user = self.client.get_user(uuid_user_id, no_get=True)
            
            if user:
                blob = ChatBlob(messages=messages)
                user.insert(blob)
                user.flush()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            # Memobase 可能暂时不可用或配置问题，记录警告但不影响主流程
            error_msg = str(e)
            if "422" in error_msg or "Unprocessable Entity" in error_msg:
                logger.warning(f"Memobase operation failed for user {user_id} (UUID: {uuid_user_id}): {error_msg}")
            else:
                logger.warning(f"Error updating user profile in Memobase for user {user_id} (UUID: {uuid_user_id}): {e}")
            # 不抛出异常，允许系统继续运行

