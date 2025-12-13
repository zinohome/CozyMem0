# 对话智能体 POC 设计文档

## 1. 项目概述

### 1.1 项目目标

构建一个智能对话系统，整合三个记忆/知识管理系统：
- **Cognee**：专业知识库（只读）
- **Memobase**：用户画像管理
- **Mem0**：会话记忆管理

### 1.2 核心功能

1. **智能对话**：基于 OpenAI API 的对话能力
2. **知识检索**：从 Cognee 知识库中检索专业知识
3. **用户画像**：从对话中提取并更新用户画像
4. **会话记忆**：跨会话的记忆管理

### 1.3 技术栈

- **LLM**：OpenAI API（GPT-4 或 GPT-3.5）
- **知识库**：Cognee（只读）
- **用户画像**：Memobase
- **会话记忆**：Mem0
- **后端框架**：FastAPI（Python）
- **部署**：Docker Compose

## 2. 架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     对话智能体应用层                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          对话处理引擎 (ConversationEngine)           │   │
│  │  - 消息路由                                          │   │
│  │  - 上下文管理                                        │   │
│  │  - 响应生成                                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼────────┐  ┌──────▼────────┐
│   Cognee SDK   │  │  Memobase SDK  │  │   Mem0 SDK    │
│  (知识检索)     │  │  (用户画像)    │  │  (会话记忆)   │
└───────┬────────┘  └──────┬────────┘  └──────┬────────┘
        │                   │                   │
┌───────▼────────┐  ┌──────▼────────┐  ┌──────▼────────┐
│  Cognee API    │  │ Memobase API  │  │   Mem0 API   │
│  (只读)        │  │  (读写)       │  │   (读写)     │
└────────────────┘  └───────────────┘  └──────────────┘
        │                   │                   │
┌───────▼────────┐  ┌──────▼────────┐  ┌──────▼────────┐
│  Cognee 服务    │  │ Memobase 服务  │  │   Mem0 服务   │
│  (知识图谱)     │  │  (用户画像)    │  │  (会话记忆)   │
└────────────────┘  └───────────────┘  └──────────────┘
```

### 2.2 核心组件

#### 2.2.1 对话处理引擎 (ConversationEngine)

**职责**：
- 接收用户消息
- 协调各个记忆系统
- 生成响应

**主要方法**：
```python
class ConversationEngine:
    async def process_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        knowledge_base_ids: List[str] = None
    ) -> str:
        """
        处理用户消息，生成响应
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            message: 用户消息
            knowledge_base_ids: 使用的知识库ID列表
        
        Returns:
            生成的响应
        """
        pass
```

#### 2.2.2 知识检索服务 (KnowledgeRetrievalService)

**职责**：
- 从 Cognee 知识库检索相关信息
- 支持多个知识库

**主要方法**：
```python
class KnowledgeRetrievalService:
    async def search_knowledge(
        self,
        query: str,
        knowledge_base_ids: List[str],
        top_k: int = 5
    ) -> List[KnowledgeResult]:
        """
        从多个知识库检索知识
        
        Args:
            query: 查询文本
            knowledge_base_ids: 知识库ID列表
            top_k: 返回结果数量
        
        Returns:
            知识检索结果列表
        """
        pass
```

#### 2.2.3 用户画像服务 (UserProfileService)

**职责**：
- 获取用户画像
- 从对话中提取用户画像信息
- 更新用户画像

**主要方法**：
```python
class UserProfileService:
    async def get_user_profile(
        self,
        user_id: str,
        max_token_size: int = 500
    ) -> Dict[str, Any]:
        """获取用户画像"""
        pass
    
    async def extract_and_update_profile(
        self,
        user_id: str,
        messages: List[Dict[str, str]]
    ) -> None:
        """从对话中提取并更新用户画像"""
        pass
```

#### 2.2.4 会话记忆服务 (ConversationMemoryService)

**职责**：
- 获取会话记忆
- 保存会话记忆
- 跨会话记忆检索

**主要方法**：
```python
class ConversationMemoryService:
    async def get_conversation_context(
        self,
        user_id: str,
        session_id: str,
        query: str = None
    ) -> List[Dict[str, Any]]:
        """获取会话上下文"""
        pass
    
    async def save_conversation(
        self,
        user_id: str,
        session_id: str,
        messages: List[Dict[str, str]],
        metadata: Dict[str, Any] = None
    ) -> None:
        """保存会话记忆"""
        pass
    
    async def search_cross_session_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """跨会话记忆检索"""
        pass
```

## 3. 数据流设计

### 3.1 对话处理流程（优化版）

```
用户消息
    │
    ├─→ 【并发执行】步骤 1-3（并行获取上下文）
    │   ├─→ 1. 获取用户画像 (Memobase)
    │   ├─→ 2. 获取会话记忆 (Mem0)
    │   └─→ 3. 检索专业知识 (Cognee)
    │
    ├─→ 4. 构建 Prompt（等待步骤 1-3 完成）
    │
    ├─→ 5. 调用 OpenAI API（同步，必须等待）
    │       └─→ 生成响应
    │
    ├─→ 【立即返回响应给用户】
    │
    └─→ 【异步执行】步骤 6-7（后台处理，不阻塞）
        ├─→ 6. 保存会话记忆 (Mem0)
        └─→ 7. 更新用户画像 (Memobase)
```

**性能优化说明**：
- **步骤 1-3 并发**：使用 `asyncio.gather()` 并行执行，减少等待时间
- **步骤 6-7 异步**：使用 `asyncio.create_task()` 后台执行，不阻塞响应
- **响应时间**：从 ~500-1000ms 降低到 ~200-500ms（取决于 OpenAI API 响应时间）

### 3.2 详细流程说明（优化版）

#### 步骤 1-3：并发获取上下文（并行执行）

```python
# 使用 asyncio.gather() 并发执行，减少等待时间
user_profile, session_memories, knowledge_results = await asyncio.gather(
    # 步骤 1：获取用户画像
    user_profile_service.get_user_profile(
        user_id=user_id,
        max_token_size=500,
        prefer_topics=["basic_info", "interest", "work"]
    ),
    
    # 步骤 2：获取会话记忆（内部也并发获取当前会话和跨会话记忆）
    memory_service.get_conversation_context(
        user_id=user_id,
        session_id=session_id,
        query=user_message
    ),
    
    # 步骤 3：检索专业知识
    knowledge_service.search_knowledge(
        query=user_message,
        knowledge_base_ids=["kb_tech", "kb_product"],
        top_k=5
    )
)
```

**性能提升**：
- 串行执行：`time_1 + time_2 + time_3`（例如：50ms + 100ms + 150ms = 300ms）
- 并发执行：`max(time_1, time_2, time_3)`（例如：max(50ms, 100ms, 150ms) = 150ms）
- **节省时间**：约 50-60%

**输出**：
- `user_profile`：用户画像 JSON
- `session_memories`：相关记忆列表（包含当前会话和跨会话）
- `knowledge_results`：相关知识片段列表

#### 步骤 4：构建 Prompt

```python
prompt = build_prompt(
    user_profile=user_profile,
    session_memories=session_memories,
    knowledge=knowledge_results,
    user_message=user_message
)
```

**Prompt 模板**：
```
# 用户画像
{user_profile}

# 相关记忆
{session_memories}

# 专业知识
{knowledge}

# 对话
用户: {user_message}
助手: 
```

#### 步骤 5：调用 OpenAI API（同步，必须等待）

```python
response = await openai_client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)
ai_response = response.choices[0].message.content
```

**注意**：这是唯一必须同步等待的步骤，因为需要响应内容才能返回给用户。

#### 步骤 6-7：异步保存（后台处理，不阻塞响应）

```python
# 立即返回响应给用户
return ai_response

# 后台异步保存（不阻塞响应）
asyncio.create_task(
    _save_conversation_async(
        user_id=user_id,
        session_id=session_id,
        user_message=user_message,
        ai_response=ai_response,
        knowledge_base_ids=knowledge_base_ids
    )
)

async def _save_conversation_async(
    user_id: str,
    session_id: str,
    user_message: str,
    ai_response: str,
    knowledge_base_ids: List[str]
):
    """异步保存会话记忆和更新用户画像"""
    # 并发执行保存操作
    await asyncio.gather(
        # 步骤 6：保存会话记忆
        memory_service.save_conversation(
            user_id=user_id,
            session_id=session_id,
            messages=[
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ai_response}
            ],
            metadata={
                "knowledge_base_ids": knowledge_base_ids,
                "timestamp": datetime.now()
            }
        ),
        
        # 步骤 7：更新用户画像
        user_profile_service.extract_and_update_profile(
            user_id=user_id,
            messages=[
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ai_response}
            ]
        )
    )
```

**性能提升**：
- **响应时间**：从 ~500-1000ms 降低到 ~200-500ms
- **用户体验**：立即收到响应，后台处理不影响交互

**注意事项**：
- 异步保存失败不会影响用户响应
- 建议添加错误日志和重试机制
- 可以考虑使用消息队列（如 Redis Queue）确保数据不丢失

## 4. 数据模型设计

### 4.1 用户模型

```python
class User:
    user_id: str
    name: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### 4.2 会话模型

```python
class Session:
    session_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
```

### 4.3 消息模型

```python
class Message:
    message_id: str
    session_id: str
    user_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
```

### 4.4 知识库映射模型

```python
class AgentKnowledgeBaseMapping:
    agent_id: str
    knowledge_base_id: str
    priority: int  # 优先级，用于排序
    created_at: datetime
```

## 5. API 设计

### 5.1 REST API 端点

#### 5.1.1 对话相关

```python
# 发送消息
POST /api/v1/conversations/{session_id}/messages
Request:
{
    "message": "用户消息",
    "knowledge_base_ids": ["kb_tech", "kb_product"]  # 可选
}
Response:
{
    "response": "AI响应",
    "session_id": "session_123",
    "timestamp": "2024-01-01T00:00:00Z"
}

# 获取会话历史
GET /api/v1/conversations/{session_id}/messages
Response:
{
    "messages": [
        {
            "role": "user",
            "content": "消息内容",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        ...
    ]
}

# 创建新会话
POST /api/v1/conversations
Request:
{
    "user_id": "user_123",
    "metadata": {}
}
Response:
{
    "session_id": "session_123",
    "created_at": "2024-01-01T00:00:00Z"
}
```

#### 5.1.2 用户相关

```python
# 获取用户画像
GET /api/v1/users/{user_id}/profile
Response:
{
    "profile": {
        "basic_info": {...},
        "interest": {...},
        "work": {...}
    }
}

# 创建用户
POST /api/v1/users
Request:
{
    "user_id": "user_123",
    "name": "用户名"
}
```

#### 5.1.3 知识库相关

```python
# 获取智能体的知识库列表
GET /api/v1/agents/{agent_id}/knowledge-bases
Response:
{
    "knowledge_bases": [
        {
            "id": "kb_tech",
            "name": "技术知识库",
            "priority": 1
        },
        ...
    ]
}
```

### 5.2 WebSocket API（可选）

```python
# WebSocket 连接
WS /ws/conversations/{session_id}

# 发送消息
{
    "type": "message",
    "data": {
        "message": "用户消息",
        "knowledge_base_ids": ["kb_tech"]
    }
}

# 接收响应
{
    "type": "response",
    "data": {
        "response": "AI响应",
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```

## 6. 实现方案

### 6.1 项目结构

```
conversational-agent-poc/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── session.py
│   │   └── message.py
│   ├── services/               # 业务服务
│   │   ├── __init__.py
│   │   ├── conversation_engine.py
│   │   ├── knowledge_service.py
│   │   ├── profile_service.py
│   │   └── memory_service.py
│   ├── clients/                # SDK 客户端封装
│   │   ├── __init__.py
│   │   ├── cognee_client.py
│   │   ├── memobase_client.py
│   │   └── mem0_client.py
│   ├── prompts/                # Prompt 模板
│   │   ├── __init__.py
│   │   └── templates.py
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── tests/                      # 测试
│   ├── __init__.py
│   ├── test_conversation_engine.py
│   └── test_services.py
├── deployment/                 # 部署配置
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── .env.example
├── docs/                       # 文档
│   ├── README.md
│   └── api.md
├── requirements.txt
├── pyproject.toml
└── README.md
```

### 6.2 核心代码实现

#### 6.2.1 对话处理引擎

```python
# src/services/conversation_engine.py
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from ..clients.cognee_client import CogneeClient
from ..clients.memobase_client import MemobaseClient
from ..clients.mem0_client import Mem0Client
from ..prompts.templates import build_conversation_prompt

class ConversationEngine:
    def __init__(
        self,
        openai_client: AsyncOpenAI,
        cognee_client: CogneeClient,
        memobase_client: MemobaseClient,
        mem0_client: Mem0Client
    ):
        self.openai = openai_client
        self.cognee = cognee_client
        self.memobase = memobase_client
        self.mem0 = mem0_client
    
    async def process_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        knowledge_base_ids: Optional[List[str]] = None
    ) -> str:
        """处理用户消息，生成响应（优化版：并发获取，异步保存）"""
        
        # 步骤 1-3：并发获取上下文（并行执行，减少等待时间）
        user_profile, session_memories, knowledge_results = await asyncio.gather(
            # 步骤 1：获取用户画像
            self.memobase.get_user_profile(
                user_id=user_id,
                max_token_size=500
            ),
            
            # 步骤 2：获取会话记忆（内部并发获取当前会话和跨会话记忆）
            self.mem0.get_conversation_context(
                user_id=user_id,
                session_id=session_id,
                query=message
            ),
            
            # 步骤 3：检索专业知识
            self.cognee.search_knowledge(
                query=message,
                knowledge_base_ids=knowledge_base_ids or []
            ) if knowledge_base_ids else asyncio.coroutine(lambda: [])(),
            return_exceptions=True  # 即使某个失败也不影响其他
        )
        
        # 处理异常（如果某个服务失败，使用默认值）
        if isinstance(user_profile, Exception):
            logger.warning(f"Failed to get user profile: {user_profile}")
            user_profile = {}
        if isinstance(session_memories, Exception):
            logger.warning(f"Failed to get session memories: {session_memories}")
            session_memories = []
        if isinstance(knowledge_results, Exception):
            logger.warning(f"Failed to get knowledge: {knowledge_results}")
            knowledge_results = []
        
        # 步骤 4：构建 Prompt
        prompt = build_conversation_prompt(
            user_profile=user_profile,
            session_memories=session_memories,
            knowledge=knowledge_results,
            user_message=message
        )
        
        # 步骤 5：调用 OpenAI API（同步，必须等待）
        response = await self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        ai_response = response.choices[0].message.content
        
        # 步骤 6-7：异步保存（后台处理，不阻塞响应）
        asyncio.create_task(
            self._save_conversation_async(
                user_id=user_id,
                session_id=session_id,
                user_message=message,
                ai_response=ai_response,
                knowledge_base_ids=knowledge_base_ids
            )
        )
        
        # 立即返回响应
        return ai_response
    
    async def _save_conversation_async(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        ai_response: str,
        knowledge_base_ids: Optional[List[str]] = None
    ) -> None:
        """异步保存会话记忆和更新用户画像"""
        try:
            # 并发执行保存操作
            await asyncio.gather(
                # 步骤 6：保存会话记忆
                self.mem0.save_conversation(
                    user_id=user_id,
                    session_id=session_id,
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": ai_response}
                    ],
                    metadata={
                        "knowledge_base_ids": knowledge_base_ids,
                        "timestamp": datetime.now().isoformat()
                    }
                ),
                
                # 步骤 7：更新用户画像
                self.memobase.extract_and_update_profile(
                    user_id=user_id,
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": ai_response}
                    ]
                ),
                return_exceptions=True  # 即使某个失败也不影响其他
            )
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}", exc_info=True)
    
    def _get_system_prompt(self) -> str:
        return """你是一个智能助手，能够：
1. 基于用户画像提供个性化回答
2. 利用专业知识库回答专业问题
3. 记住并参考历史对话内容
4. 提供友好、专业的服务"""
```

#### 6.2.2 知识检索服务

```python
# src/services/knowledge_service.py
from typing import List, Dict, Any
from cognee_sdk import CogneeClient, SearchType

class KnowledgeRetrievalService:
    def __init__(self, cognee_client: CogneeClient):
        self.client = cognee_client
    
    async def search_knowledge(
        self,
        query: str,
        knowledge_base_ids: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """从多个知识库检索知识"""
        all_results = []
        
        # 并发搜索多个知识库
        tasks = [
            self._search_single_kb(query, kb_id, top_k)
            for kb_id in knowledge_base_ids
        ]
        results_list = await asyncio.gather(*tasks)
        
        # 合并结果并按相关性排序
        for results in results_list:
            all_results.extend(results)
        
        # 去重并按分数排序
        unique_results = self._deduplicate_and_sort(all_results)
        return unique_results[:top_k]
    
    async def _search_single_kb(
        self,
        query: str,
        dataset_name: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """搜索单个知识库"""
        results = await self.client.search(
            query=query,
            datasets=[dataset_name],
            search_type=SearchType.GRAPH_COMPLETION,
            top_k=top_k
        )
        return [
            {
                "content": result.content,
                "score": result.score,
                "source": dataset_name
            }
            for result in results
        ]
    
    def _deduplicate_and_sort(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """去重并按分数排序"""
        seen = set()
        unique = []
        for result in results:
            content_hash = hash(result["content"])
            if content_hash not in seen:
                seen.add(content_hash)
                unique.append(result)
        return sorted(unique, key=lambda x: x["score"], reverse=True)
```

#### 6.2.3 用户画像服务

```python
# src/services/profile_service.py
from typing import Dict, Any, List
from memobase import MemoBaseClient, ChatBlob

class UserProfileService:
    def __init__(self, memobase_client: MemoBaseClient):
        self.client = memobase_client
    
    async def get_user_profile(
        self,
        user_id: str,
        max_token_size: int = 500
    ) -> Dict[str, Any]:
        """获取用户画像"""
        user = self.client.get_or_create_user(user_id)
        profile = user.profile(
            max_token_size=max_token_size,
            prefer_topics=["basic_info", "interest", "work"]
        )
        return profile
    
    async def extract_and_update_profile(
        self,
        user_id: str,
        messages: List[Dict[str, str]]
    ) -> None:
        """从对话中提取并更新用户画像"""
        user = self.client.get_or_create_user(user_id)
        
        # 创建对话 Blob
        blob = ChatBlob(messages=messages)
        
        # 插入数据（异步，不等待处理）
        user.insert(blob)
        
        # 刷新缓冲区（触发画像更新）
        user.flush()
```

#### 6.2.4 会话记忆服务

```python
# src/services/memory_service.py
from typing import List, Dict, Any, Optional
from mem0 import AsyncMemoryClient

class ConversationMemoryService:
    def __init__(self, mem0_client: AsyncMemoryClient):
        self.client = mem0_client
    
    async def get_conversation_context(
        self,
        user_id: str,
        session_id: str,
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取会话上下文（优化版：并发获取当前会话和跨会话记忆）"""
        if not query:
            return []
        
        # 并发获取当前会话记忆和跨会话记忆
        current_memories, cross_memories = await asyncio.gather(
            # 当前会话记忆
            self.client.search(
                query=query,
                user_id=user_id,
                agent_id=session_id,
                limit=10
            ),
            
            # 跨会话记忆
            self.client.search(
                query=query,
                user_id=user_id,
                limit=5
            ),
            return_exceptions=True
        )
        
        # 处理结果
        memories = []
        
        if not isinstance(current_memories, Exception):
            memories.extend([
                {
                    "content": result.memory,
                    "type": result.memory_type,
                    "session": "current",
                    "timestamp": result.created_at
                }
                for result in current_memories
            ])
        
        if not isinstance(cross_memories, Exception):
            memories.extend([
                {
                    "content": result.memory,
                    "type": result.memory_type,
                    "session": "cross",
                    "timestamp": result.created_at
                }
                for result in cross_memories
            ])
        
        # 按时间排序
        memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return memories[:15]  # 返回最多15条
    
    async def save_conversation(
        self,
        user_id: str,
        session_id: str,
        messages: List[Dict[str, str]],
        metadata: Dict[str, Any] = None
    ) -> None:
        """保存会话记忆"""
        await self.client.add(
            messages=messages,
            user_id=user_id,
            agent_id=session_id,
            metadata=metadata
        )
    
    async def search_cross_session_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """跨会话记忆检索"""
        results = await self.client.search(
            query=query,
            user_id=user_id,
            limit=limit
        )
        return [
            {
                "content": result.memory,
                "type": result.memory_type,
                "session_id": result.metadata.get("session_id"),
                "timestamp": result.created_at
            }
            for result in results
        ]
```

## 7. 配置管理

### 7.1 环境变量配置

```env
# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# Cognee
COGNEE_API_URL=http://localhost:8000
COGNEE_API_TOKEN=your-token

# Memobase
MEMOBASE_PROJECT_URL=http://localhost:8019
MEMOBASE_API_KEY=secret

# Mem0
MEM0_API_URL=http://localhost:8888
MEM0_API_KEY=your-api-key

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8080
LOG_LEVEL=INFO
```

### 7.2 配置文件

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # Cognee
    cognee_api_url: str = "http://localhost:8000"
    cognee_api_token: str | None = None
    
    # Memobase
    memobase_project_url: str = "http://localhost:8019"
    memobase_api_key: str = "secret"
    
    # Mem0
    mem0_api_url: str = "http://localhost:8888"
    mem0_api_key: str | None = None
    
    # 应用配置
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 8. 部署方案

### 8.1 Docker Compose 配置

```yaml
# deployment/docker-compose.yml
version: '3.8'

services:
  conversational-agent:
    build:
      context: ..
      dockerfile: deployment/Dockerfile
    container_name: conversational-agent
    restart: unless-stopped
    ports:
      - "8080:8080"
    env_file:
      - .env
    depends_on:
      - cognee-api
      - memobase-api
      - mem0-api
    networks:
      - agent-network

  cognee-api:
    # 使用现有的 Cognee 服务
    # 或者引用 CozyCognee 的部署配置
    external: true
    networks:
      - agent-network

  memobase-api:
    # 使用现有的 Memobase 服务
    # 或者引用 CozyMemobase 的部署配置
    external: true
    networks:
      - agent-network

  mem0-api:
    # 使用现有的 Mem0 服务
    # 或者引用 CozyMem0 的部署配置
    external: true
    networks:
      - agent-network

networks:
  agent-network:
    driver: bridge
```

### 8.2 Dockerfile

```dockerfile
# deployment/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY src/ ./src/
COPY pyproject.toml .

# 运行应用
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## 9. 测试方案

### 9.1 单元测试

```python
# tests/test_conversation_engine.py
import pytest
from unittest.mock import AsyncMock, patch
from src.services.conversation_engine import ConversationEngine

@pytest.mark.asyncio
async def test_process_message():
    """测试消息处理流程"""
    # Mock 各个客户端
    mock_openai = AsyncMock()
    mock_cognee = AsyncMock()
    mock_memobase = AsyncMock()
    mock_mem0 = AsyncMock()
    
    # 创建引擎
    engine = ConversationEngine(
        mock_openai, mock_cognee, mock_memobase, mock_mem0
    )
    
    # 测试处理消息
    response = await engine.process_message(
        user_id="user_123",
        session_id="session_123",
        message="测试消息"
    )
    
    assert response is not None
    # 验证各个服务被调用
    mock_memobase.get_user_profile.assert_called_once()
    mock_mem0.get_conversation_context.assert_called_once()
```

### 9.2 集成测试

```python
# tests/test_integration.py
import pytest
from src.main import app
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

def test_send_message(client):
    """测试发送消息接口"""
    response = client.post(
        "/api/v1/conversations/session_123/messages",
        json={
            "message": "你好",
            "knowledge_base_ids": ["kb_tech"]
        }
    )
    assert response.status_code == 200
    assert "response" in response.json()
```

## 10. 性能优化说明

### 10.1 响应时间优化

**优化前（串行执行）**：
```
总时间 = 用户画像(50ms) + 会话记忆(100ms) + 知识检索(150ms) 
      + Prompt构建(10ms) + OpenAI API(200-500ms) 
      + 保存记忆(50ms) + 更新画像(100ms)
      = 660-960ms
```

**优化后（并发+异步）**：
```
响应时间 = max(用户画像, 会话记忆, 知识检索)(150ms) 
         + Prompt构建(10ms) + OpenAI API(200-500ms)
         = 360-660ms

后台处理 = 保存记忆(50ms) + 更新画像(100ms) = 150ms（不阻塞）
```

**性能提升**：响应时间减少 **45-50%**

### 10.2 并发优化策略

1. **步骤 1-3 并发执行**：使用 `asyncio.gather()` 并行获取上下文
2. **步骤 6-7 异步执行**：使用 `asyncio.create_task()` 后台保存
3. **错误处理**：使用 `return_exceptions=True` 确保部分失败不影响整体

### 10.3 进一步优化建议

1. **缓存用户画像**：用户画像变化不频繁，可以缓存 5-10 分钟
2. **批量保存**：可以累积多条消息后批量保存，减少 I/O
3. **流式响应**：使用 OpenAI 的流式 API，边生成边返回

## 11. 开发计划

### 阶段 1：基础框架（1-2周）

- [ ] 项目结构搭建
- [ ] 配置管理
- [ ] SDK 客户端封装
- [ ] 基础 API 框架

### 阶段 2：核心功能（2-3周）

- [ ] 对话处理引擎实现（并发优化）
- [ ] 知识检索服务
- [ ] 用户画像服务
- [ ] 会话记忆服务（并发获取）
- [ ] Prompt 模板设计

### 阶段 3：集成测试（1周）

- [ ] 单元测试
- [ ] 集成测试
- [ ] 端到端测试
- [ ] 性能测试

### 阶段 4：优化和文档（1周）

- [ ] 性能优化（缓存、批量处理）
- [ ] 错误处理和降级策略
- [ ] API 文档
- [ ] 使用文档

## 11. 风险评估

### 11.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| SDK 性能问题 | 中 | 使用连接池、缓存优化 |
| 服务依赖问题 | 高 | 实现服务降级、健康检查 |
| Prompt 效果不佳 | 中 | 持续优化 Prompt 模板 |

### 11.2 业务风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 用户画像提取不准确 | 中 | 增加验证和人工审核 |
| 知识库检索不相关 | 中 | 优化检索策略和排序 |

## 12. 后续优化方向

1. **性能优化**
   - 实现响应缓存
   - 异步处理用户画像更新
   - 批量处理优化

2. **功能增强**
   - 支持多轮对话上下文
   - 实现流式响应
   - 增加对话质量评估

3. **监控和日志**
   - 添加性能监控
   - 实现请求日志
   - 错误追踪

---

*文档创建日期：2024年*
*最后更新：2024年*


