"""Cognee 客户端封装"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from cognee_sdk import CogneeClient, SearchType
from ..config import settings

logger = logging.getLogger(__name__)


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
            # 🎯 性能优化策略：尝试多种搜索模式
            # 优先使用快速模式，失败则降级到慢速但稳定的模式
            results = None
            
            # 策略1: 先尝试 CHUNKS（快但可能返回空）
            try:
                logger.info(f"🚀 尝试 CHUNKS 模式...")
                results = await self.client.search(
                    query=query,
                    datasets=dataset_names,
                    search_type=SearchType.CHUNKS,
                    top_k=top_k
                )
                if results and len(results) > 0:
                    logger.info(f"✅ CHUNKS 模式成功，返回 {len(results)} 条")
                else:
                    logger.warning(f"⚠️ CHUNKS 模式返回空，降级到 GRAPH_COMPLETION")
                    results = None
            except Exception as e:
                logger.warning(f"⚠️ CHUNKS 模式失败: {e}，降级到 GRAPH_COMPLETION")
                results = None
            
            # 策略2: 如果 CHUNKS 失败，使用 GRAPH_COMPLETION
            if not results:
                logger.info(f"🐌 使用 GRAPH_COMPLETION 模式（较慢但稳定）")
                results = await self.client.search(
                    query=query,
                    datasets=dataset_names,
                    search_type=SearchType.GRAPH_COMPLETION,
                    top_k=top_k
                )
            
            # 🔍 调试：记录原始返回结果
            logger.info(f"🔍 Cognee 原始返回: type={type(results)}, len={len(results) if hasattr(results, '__len__') else 'N/A'}")
            if results:
                logger.info(f"🔍 第一个结果类型: {type(results[0] if hasattr(results, '__getitem__') else 'N/A')}")
                logger.info(f"🔍 第一个结果内容: {str(results[0] if hasattr(results, '__getitem__') else results)[:200]}")
            else:
                logger.warning(f"⚠️ Cognee 返回空结果！query={query}, datasets={dataset_names}")
            
            # 解析 Cognee SDK 返回的结果
            knowledge_results = []
            for i, result in enumerate(results):
                content = None
                default_score = 1.0 - (i * 0.1)  # 按顺序递减分数
                score = default_score
                
                if isinstance(result, str):
                    # 字符串格式（GRAPH_COMPLETION 模式）
                    content = result
                elif hasattr(result, 'text'):
                    # SearchResult 对象格式（CHUNKS 模式）
                    content = result.text
                    # 获取 score，如果是 None 或无效值则使用默认值
                    result_score = getattr(result, 'score', None)
                    score = result_score if result_score is not None else default_score
                    logger.info(f"  📄 CHUNKS 结果 {i+1}: text 长度={len(result.text)}, score={score}")
                elif hasattr(result, 'content'):
                    # 其他对象格式（备用）
                    content = result.content
                    result_score = getattr(result, 'score', None)
                    score = result_score if result_score is not None else default_score
                elif isinstance(result, dict):
                    # 字典格式（备用）
                    content = result.get("text") or result.get("content") or str(result)
                    result_score = result.get("score")
                    score = result_score if result_score is not None else default_score
                
                if content:
                    knowledge_results.append({
                        "content": content,
                        "score": score,
                        "source": dataset_names[0] if dataset_names else "unknown"
                    })
                else:
                    logger.warning(f"  ⚠️ 无法解析结果 {i+1}: type={type(result)}, attributes={dir(result)[:10]}")
            
            logger.info(f"✅ 解析后知识数: {len(knowledge_results)}")
            return knowledge_results
        except Exception as e:
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

