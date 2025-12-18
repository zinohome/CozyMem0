"""FastAPI 应用主入口"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI

from .config import settings
from .clients import CogneeClientWrapper, MemobaseClientWrapper, Mem0ClientWrapper
from .services import ConversationEngine

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 全局变量
conversation_engine: Optional[ConversationEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global conversation_engine
    
    # 启动时初始化
    logger.info("Initializing services...")
    logger.info(f"Cognee URL: {settings.cognee_api_url}")
    logger.info(f"Memobase URL: {settings.memobase_project_url}")
    logger.info(f"Mem0 URL: {settings.mem0_api_url}")
    
    # 初始化客户端
    openai_kwargs = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        openai_kwargs["base_url"] = settings.openai_base_url
        logger.info(f"OpenAI Base URL: {settings.openai_base_url}")
    openai_client = AsyncOpenAI(**openai_kwargs)
    cognee_client = CogneeClientWrapper()
    memobase_client = MemobaseClientWrapper()
    mem0_client = Mem0ClientWrapper()
    
    # 检查客户端初始化状态
    if not mem0_client.client:
        logger.warning("Mem0 client is not initialized (mem0_api_url may be empty)")
    
    # 初始化对话引擎
    conversation_engine = ConversationEngine(
        openai_client=openai_client,
        cognee_client=cognee_client,
        memobase_client=memobase_client,
        mem0_client=mem0_client
    )
    
    logger.info("Services initialized successfully")
    
    yield
    
    # 关闭时清理
    logger.info("Shutting down services...")
    await cognee_client.close()
    await mem0_client.close()
    logger.info("Services shut down successfully")


# 创建 FastAPI 应用
app = FastAPI(
    title="Conversational Agent POC",
    description="智能对话系统 POC - 整合 Cognee、Memobase、Mem0",
    version="0.1.0",
    lifespan=lifespan
)


# 请求模型
class MessageRequest(BaseModel):
    """消息请求模型"""
    message: str
    user_id: str
    session_id: str
    dataset_names: Optional[List[str]] = None
    role: str = "default"  # 角色：default 或 psychology_counselor


class TestRequest(BaseModel):
    """测试请求模型"""
    user_id: str
    session_id: Optional[str] = None
    message: str
    dataset_names: Optional[List[str]] = None
    role: str = "default"  # 角色：default 或 psychology_counselor


# API 端点
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Conversational Agent POC",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/api/v1/conversations/{session_id}/messages")
async def send_message(
    session_id: str,
    request: MessageRequest
):
    """
    发送消息并获取响应
    
    Args:
        session_id: 会话ID
        request: 消息请求
    """
    if not conversation_engine:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = await conversation_engine.process_message(
            user_id=request.user_id,
            session_id=session_id,
            message=request.message,
            dataset_names=request.dataset_names,
            role=request.role
        )
        
        return JSONResponse(content={
            "success": True,
            "session_id": session_id,
            "response": result["response"],
            "timestamp": "2024-01-01T00:00:00Z"
        })
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/test/conversation")
async def test_conversation(request: TestRequest):
    """
    测试对话接口（返回完整上下文信息）
    
    Args:
        request: 测试请求
    """
    if not conversation_engine:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        session_id = request.session_id or f"test_session_{request.user_id}"
        
        result = await conversation_engine.process_message(
            user_id=request.user_id,
            session_id=session_id,
            message=request.message,
            dataset_names=request.dataset_names,
            role=request.role
        )
        
        return JSONResponse(content={
            "success": True,
            "user_id": request.user_id,
            "session_id": session_id,
            "message": request.message,
            "response": result["response"],
            "context": result["context"],
            "dataset_names": request.dataset_names,
            "role": request.role
        })
    except Exception as e:
        logger.error(f"Error in test conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """
    获取用户画像（测试接口）
    
    Args:
        user_id: 用户ID
    """
    if not conversation_engine:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        profile = await conversation_engine.profile_service.get_user_profile(
            user_id=user_id
        )
        return JSONResponse(content={
            "success": True,
            "user_id": user_id,
            "profile": profile
        })
    except Exception as e:
        logger.error(f"Error getting user profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/debug/status")
async def debug_status():
    """
    调试接口：查看服务状态和配置
    """
    if not conversation_engine:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return JSONResponse(content={
        "success": True,
        "services": {
            "cognee": {
                "url": settings.cognee_api_url,
                "initialized": conversation_engine.knowledge_service.cognee.client is not None
            },
            "memobase": {
                "url": settings.memobase_project_url,
                "initialized": conversation_engine.profile_service.memobase.client is not None
            },
            "mem0": {
                "url": settings.mem0_api_url,
                "initialized": conversation_engine.memory_service.mem0.client is not None
            },
            "openai": {
                "model": settings.openai_model,
                "base_url": settings.openai_base_url or "default"
            }
        }
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )

