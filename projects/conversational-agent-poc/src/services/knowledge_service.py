"""知识检索服务"""
from typing import List, Dict, Any
from ..clients import CogneeClientWrapper


class KnowledgeService:
    """知识检索服务"""
    
    def __init__(self, cognee_client: CogneeClientWrapper):
        self.cognee = cognee_client
    
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
        return await self.cognee.search_knowledge(
            query=query,
            dataset_names=dataset_names,
            top_k=top_k
        )

