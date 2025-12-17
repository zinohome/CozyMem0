"""Mem0 客户端封装"""
import asyncio
from typing import List, Dict, Any, Optional
import httpx
from ..config import settings


class Mem0ClientWrapper:
    """Mem0 客户端封装类（直接调用本地 mem0 服务器 API）"""
    
    def __init__(self):
        # mem0 服务器使用 /api/v1 前缀（通过补丁添加）
        # 注意：mem0_api_key 是可选的，即使没有 key 也可以使用本地服务器
        import logging
        logger = logging.getLogger(__name__)
        
        if not settings.mem0_api_url:
            logger.warning("Mem0 API URL not configured, mem0 client will be disabled")
            self.base_url = None
            self.client = None
        else:
            self.base_url = settings.mem0_api_url.rstrip('/')
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
            logger.info(f"Mem0 client initialized with URL: {self.base_url}")
    
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
            # mem0 服务器 API: POST /api/v1/search
            # 注意：如果 agent_id 为空字符串，mem0 可能不会返回结果，所以使用 None
            current_memories_resp, cross_memories_resp = await asyncio.gather(
                self.client.post(
                    "/api/v1/search",
                    json={
                        "query": query,
                        "user_id": user_id,
                        "agent_id": session_id if session_id else None
                    }
                ),
                self.client.post(
                    "/api/v1/search",
                    json={
                        "query": query,
                        "user_id": user_id
                    }
                ),
                return_exceptions=True
            )
            
            memories = []
            import logging
            logger = logging.getLogger(__name__)
            
            # 处理当前会话记忆
            if isinstance(current_memories_resp, Exception):
                logger.warning(f"Current session search failed: {current_memories_resp}")
            elif not isinstance(current_memories_resp, Exception):
                current_memories_resp.raise_for_status()
                current_data = current_memories_resp.json()
                logger.debug(f"Mem0 current session response: {current_data}")
                # mem0 返回的格式：直接是列表，每个元素包含 memory 字段
                if isinstance(current_data, list):
                    for item in current_data[:10]:
                        memories.append({
                            "content": item.get("memory", item.get("content", str(item))),
                            "type": item.get("memory_type", item.get("type", "semantic")),
                            "session": "current",
                            "timestamp": item.get("created_at", item.get("timestamp"))
                        })
                elif isinstance(current_data, dict):
                    # 如果是字典，可能是包装格式
                    if "results" in current_data:
                        for item in current_data["results"][:10]:
                            memories.append({
                                "content": item.get("memory", item.get("content", str(item))),
                                "type": item.get("memory_type", item.get("type", "semantic")),
                                "session": "current",
                                "timestamp": item.get("created_at", item.get("timestamp"))
                            })
                    else:
                        # 单个结果
                        memories.append({
                            "content": current_data.get("memory", current_data.get("content", str(current_data))),
                            "type": current_data.get("memory_type", current_data.get("type", "semantic")),
                        "session": "current",
                            "timestamp": current_data.get("created_at", current_data.get("timestamp"))
                        })
            
            logger.debug(f"After processing current session: {len(memories)} memories")
            
            # 处理跨会话记忆
            if not isinstance(cross_memories_resp, Exception):
                cross_memories_resp.raise_for_status()
                cross_data = cross_memories_resp.json()
                logger.debug(f"Mem0 cross session response: {cross_data}")
                if isinstance(cross_data, list):
                    for item in cross_data[:5]:
                        memories.append({
                            "content": item.get("memory", item.get("content", str(item))),
                            "type": item.get("memory_type", item.get("type", "semantic")),
                            "session": "cross",
                            "timestamp": item.get("created_at", item.get("timestamp"))
                        })
                elif isinstance(cross_data, dict):
                    if "results" in cross_data:
                        for item in cross_data["results"][:5]:
                            memories.append({
                                "content": item.get("memory", item.get("content", str(item))),
                                "type": item.get("memory_type", item.get("type", "semantic")),
                                "session": "cross",
                                "timestamp": item.get("created_at", item.get("timestamp"))
                            })
                    else:
                        # 单个结果
                        memories.append({
                            "content": cross_data.get("memory", cross_data.get("content", str(cross_data))),
                            "type": cross_data.get("memory_type", cross_data.get("type", "semantic")),
                        "session": "cross",
                            "timestamp": cross_data.get("created_at", cross_data.get("timestamp"))
                        })
            
            logger.debug(f"After processing cross session: {len(memories)} memories")
            
            # 按时间排序
            memories.sort(key=lambda x: x.get("timestamp", "") or "", reverse=True)
            final_memories = memories[:15]
            logger.info(f"Mem0 returning {len(final_memories)} memories for user {user_id}")
            return final_memories
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting conversation context: {e}", exc_info=True)
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
            # mem0 服务器 API: POST /api/v1/memories
            # 消息格式需要转换为 mem0 期望的格式
            mem0_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    # 如果已经是 {"role": "user", "content": "..."} 格式，直接使用
                    if "role" in msg and "content" in msg:
                        mem0_messages.append(msg)
                    # 如果是其他格式，尝试转换
                    elif "message" in msg:
                        mem0_messages.append({
                            "role": msg.get("role", "user"),
                            "content": msg["message"]
                        })
                    elif "text" in msg:
                        mem0_messages.append({
                            "role": msg.get("role", "user"),
                            "content": msg["text"]
                        })
            
            payload = {
                "messages": mem0_messages,
                "user_id": user_id,
                "agent_id": session_id
            }
            if metadata:
                payload["metadata"] = metadata
            
            response = await self.client.post("/api/v1/memories", json=payload)
            response.raise_for_status()
            
            # 记录保存结果（用于调试）
            import logging
            logger = logging.getLogger(__name__)
            try:
                result = response.json()
                logger.info(f"Mem0 memory saved successfully for user {user_id}, session {session_id}")
                # 检查返回结果中是否有错误
                if isinstance(result, dict) and "error" in result:
                    logger.warning(f"Mem0 returned error in response: {result.get('error')}")
            except Exception as e:
                logger.warning(f"Could not parse Mem0 response: {e}")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving conversation: {e}", exc_info=True)
    
    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()

