"""Cognee 客户端封装"""
import asyncio
from typing import List, Dict, Any, Optional
from cognee_sdk import CogneeClient, SearchType
from ..config import settings


class CogneeClientWrapper:
    """Cognee 客户端封装类"""
    
    def __init__(self):
        self.client = CogneeClient(
            api_url=settings.cognee_api_url,
            api_token=settings.cognee_api_token
        )
    
    async def search_knowledge(
        self,
        query: str,
        dataset_names: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        从多个知识库检索知识
        
        Args:
            query: 查询文本
            dataset_names: 数据集名称列表
            top_k: 返回结果数量
        
        Returns:
            知识检索结果列表
        """
        if not dataset_names:
            return []
        
        try:
            results = await self.client.search(
                query=query,
                datasets=dataset_names,
                search_type=SearchType.GRAPH_COMPLETION,
                top_k=top_k
            )
            
            return [
                {
                    "content": result.content,
                    "score": result.score,
                    "source": dataset_names[0] if dataset_names else "unknown"
                }
                for result in results
            ]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            # 数据集不存在是常见情况，使用 warning 而不是 error
            error_msg = str(e)
            if "DatasetNotFoundError" in error_msg or "No datasets found" in error_msg:
                logger.warning(f"Dataset not found in Cognee: {dataset_names}. Error: {error_msg}")
            else:
                logger.error(f"Error searching knowledge: {e}", exc_info=True)
            return []
    
    async def close(self):
        """关闭客户端"""
        await self.client.close()

