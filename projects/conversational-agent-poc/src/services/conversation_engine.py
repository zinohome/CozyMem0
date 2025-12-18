"""对话处理引擎"""
import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from ..config import settings
from ..clients import CogneeClientWrapper, MemobaseClientWrapper, Mem0ClientWrapper
from ..services import KnowledgeService, ProfileService, MemoryService
from ..prompts.templates import build_conversation_prompt, get_system_prompt

logger = logging.getLogger(__name__)


class ConversationEngine:
    """对话处理引擎"""
    
    def __init__(
        self,
        openai_client: AsyncOpenAI,
        cognee_client: CogneeClientWrapper,
        memobase_client: MemobaseClientWrapper,
        mem0_client: Mem0ClientWrapper
    ):
        self.openai = openai_client
        self.knowledge_service = KnowledgeService(cognee_client)
        self.profile_service = ProfileService(memobase_client)
        self.memory_service = MemoryService(mem0_client)
    
    async def process_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        dataset_names: Optional[List[str]] = None,
        role: str = "default"
    ) -> Dict[str, Any]:
        """
        处理用户消息，生成响应
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            message: 用户消息
            dataset_names: 知识库数据集名称列表
        
        Returns:
            包含响应和上下文的字典
        """
        # 步骤 1-3：并发获取上下文（🚀 已优化性能）
        import time
        start_time = time.time()
        retrieval_start = time.time()
        
        user_profile, session_memories, knowledge_results = await asyncio.gather(
            self.profile_service.get_user_profile(user_id=user_id, max_token_size=300),  # 🚀 减少token
            self.memory_service.get_conversation_context(
                user_id=user_id,
                session_id=session_id,
                query=message
            ),
            self.knowledge_service.search_knowledge(
                query=message,
                dataset_names=dataset_names or [],
                top_k=2  # 🚀 从5减少到2，显著加快检索速度
            ),
            return_exceptions=True
        )
        
        retrieval_time = time.time() - retrieval_start
        logger.info(f"⚡ 并行检索耗时: {retrieval_time:.2f}秒")
        
        # 处理异常并记录详细信息
        if isinstance(user_profile, Exception):
            logger.warning(f"Failed to get user profile (will use empty profile): {user_profile}")
            user_profile = {}
        else:
            logger.info(f"Retrieved user profile: {len(user_profile)} fields")
        
        if isinstance(session_memories, Exception):
            logger.warning(f"Failed to get session memories (will use empty memories): {session_memories}")
            session_memories = []
        else:
            logger.info(f"Retrieved {len(session_memories)} session memories")
        
        if isinstance(knowledge_results, Exception):
            # 如果是数据集不存在的错误，给出友好提示
            error_msg = str(knowledge_results)
            if "DatasetNotFoundError" in error_msg or "No datasets found" in error_msg:
                logger.warning(f"Dataset not found (will continue without knowledge): {error_msg}")
            else:
                logger.warning(f"Failed to get knowledge (will continue without knowledge): {error_msg}")
            knowledge_results = []
        else:
            logger.info(f"Retrieved {len(knowledge_results)} knowledge results")
        
        # 步骤 4：构建 Prompt
        prompt = build_conversation_prompt(
            user_profile=user_profile,
            session_memories=session_memories,
            knowledge=knowledge_results,
            user_message=message
        )
        
        # 步骤 5：调用 OpenAI API
        llm_start = time.time()
        try:
            response = await self.openai.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": get_system_prompt(role)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800  # 🚀 限制回复长度，加快生成
            )
            ai_response = response.choices[0].message.content
            llm_time = time.time() - llm_start
            logger.info(f"⚡ LLM生成耗时: {llm_time:.2f}秒")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            ai_response = "抱歉，我遇到了一些问题，请稍后再试。"
            llm_time = time.time() - llm_start
        
        # 步骤 6-7：异步保存（不阻塞响应）
        asyncio.create_task(
            self._save_conversation_async(
                user_id=user_id,
                session_id=session_id,
                user_message=message,
                ai_response=ai_response,
                dataset_names=dataset_names
            )
        )
        
        # 总耗时
        total_time = time.time() - start_time
        logger.info(f"🎯 对话总耗时: {total_time:.2f}秒 (检索: {retrieval_time:.2f}s + LLM: {llm_time:.2f}s)")
        
        # 返回响应和上下文信息（用于测试和调试）
        # 确保即使数据为空也返回有意义的信息
        context = {
            "user_profile": user_profile if user_profile else {},
            "user_profile_status": "已加载" if user_profile else "暂无（首次对话或新用户）",
            "session_memories_count": len(session_memories),
            "session_memories_status": f"已加载 {len(session_memories)} 条记忆" if session_memories else "暂无（首次对话或新会话）",
            "knowledge_count": len(knowledge_results),
            "knowledge_status": f"已检索到 {len(knowledge_results)} 条知识" if knowledge_results else "暂无（未指定知识库或知识库为空）",
            "session_memories": session_memories[:5] if session_memories else [],  # 只返回前5条
            "knowledge": knowledge_results[:3] if knowledge_results else [],  # 只返回前3条
        }
        
        # 添加调试信息（仅在有错误时）
        if any(isinstance(x, Exception) for x in [user_profile, session_memories, knowledge_results]):
            context["debug"] = {
                "profile_error": str(user_profile) if isinstance(user_profile, Exception) else None,
                "memories_error": str(session_memories) if isinstance(session_memories, Exception) else None,
                "knowledge_error": str(knowledge_results) if isinstance(knowledge_results, Exception) else None
            }
        
        return {
            "response": ai_response,
            "context": context
        }
    
    async def _save_conversation_async(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        ai_response: str,
        dataset_names: Optional[List[str]] = None
    ) -> None:
        """异步保存会话记忆和更新用户画像"""
        try:
            await asyncio.gather(
                self.memory_service.save_conversation(
                    user_id=user_id,
                    session_id=session_id,
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": ai_response}
                    ],
                    metadata={
                        "dataset_names": dataset_names,
                        "timestamp": datetime.now().isoformat()
                    }
                ),
                self.profile_service.extract_and_update_profile(
                    user_id=user_id,
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": ai_response}
                    ]
                ),
                return_exceptions=True
            )
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}", exc_info=True)

