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
            print(f"Error searching knowledge: {e}")
            return []
    
    async def close(self):
        """关闭客户端"""
        await self.client.close()

