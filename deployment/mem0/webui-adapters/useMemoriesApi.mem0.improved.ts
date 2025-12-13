/**
 * Mem0 API 适配的 useMemoriesApi Hook (改进版)
 * 增加了灵活的响应格式适配和更好的错误处理
 */

import { useState, useCallback } from 'react';
import axios from 'axios';
import { Memory, Category } from '@/components/types';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '@/store/store';
import { setAccessLogs, setMemoriesSuccess, setSelectedMemory, setRelatedMemories } from '@/store/memoriesSlice';

// 灵活的响应格式适配
interface Mem0MemoryItem {
  id?: string;
  memory_id?: string;
  memory?: string;
  content?: string;
  text?: string;
  created_at?: number | string;
  metadata?: Record<string, any>;
  [key: string]: any; // 允许其他字段
}

// 适配函数：将 Mem0 API 响应转换为 Memory 数组
function adaptMem0Response(response: any): Memory[] {
  if (!response) return [];
  
  let items: Mem0MemoryItem[] = [];
  
  // 情况1: 响应是数组
  if (Array.isArray(response)) {
    items = response;
  }
  // 情况2: 响应有 results 字段
  else if (response.results && Array.isArray(response.results)) {
    items = response.results;
  }
  // 情况3: 响应是单个对象
  else if (response.id || response.memory_id) {
    items = [response];
  }
  // 情况4: 其他格式（尝试提取数据）
  else {
    console.warn('[Mem0 Adapter] Unknown response format:', response);
    return [];
  }
  
  return items.map(adaptMemoryItem);
}

// 适配单个记忆项
function adaptMemoryItem(item: Mem0MemoryItem): Memory {
  // 提取 ID
  const id = item.id || item.memory_id || item.memory_id || String(item);
  
  // 提取内容（尝试多个可能的字段名）
  const content = item.memory || item.content || item.text || '';
  
  // 解析时间戳
  const created_at = parseTimestamp(item.created_at);
  
  // 提取元数据
  const metadata = item.metadata || {};
  
  return {
    id: String(id),
    memory: String(content),
    created_at: created_at,
    state: "active" as const,
    metadata: metadata,
    categories: [] as Category[],
    client: 'api',
    app_name: metadata?.source_app || metadata?.app_name || 'mem0'
  };
}

// 解析时间戳（支持多种格式）
function parseTimestamp(timestamp: any): number {
  if (!timestamp) return Date.now();
  
  // 如果是数字，直接返回
  if (typeof timestamp === 'number') {
    // 如果是秒级时间戳，转换为毫秒
    return timestamp < 1e12 ? timestamp * 1000 : timestamp;
  }
  
  // 如果是字符串，尝试解析
  if (typeof timestamp === 'string') {
    const date = new Date(timestamp);
    if (!isNaN(date.getTime())) {
      return date.getTime();
    }
    // 尝试解析数字字符串
    const num = parseInt(timestamp, 10);
    if (!isNaN(num)) {
      return num < 1e12 ? num * 1000 : num;
    }
  }
  
  // 默认返回当前时间
  return Date.now();
}

interface SimpleMemory {
  id: string;
  text: string;
  created_at: string;
  state: string;
  categories: string[];
  app_name: string;
}

interface UseMemoriesApiReturn {
  fetchMemories: (
    query?: string,
    page?: number,
    size?: number,
    filters?: {
      apps?: string[];
      categories?: string[];
      sortColumn?: string;
      sortDirection?: 'asc' | 'desc';
      showArchived?: boolean;
    }
  ) => Promise<{ memories: Memory[]; total: number; pages: number }>;
  fetchMemoryById: (memoryId: string) => Promise<void>;
  fetchAccessLogs: (memoryId: string, page?: number, pageSize?: number) => Promise<void>;
  fetchRelatedMemories: (memoryId: string) => Promise<void>;
  createMemory: (text: string) => Promise<void>;
  deleteMemories: (memoryIds: string[]) => Promise<void>;
  updateMemory: (memoryId: string, content: string) => Promise<void>;
  updateMemoryState: (memoryIds: string[], state: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  hasUpdates: number;
  memories: Memory[];
  selectedMemory: SimpleMemory | null;
}

export const useMemoriesApi = (): UseMemoriesApiReturn => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasUpdates, setHasUpdates] = useState<number>(0);
  const dispatch = useDispatch<AppDispatch>();
  const user_id = useSelector((state: RootState) => state.profile.userId);
  const memories = useSelector((state: RootState) => state.memories.memories);
  const selectedMemory = useSelector((state: RootState) => state.memories.selectedMemory);

  const URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8888";

  // 增强的错误处理
  function handleError(err: any, operation: string): never {
    let errorMessage = `Failed to ${operation}`;
    
    if (err.response) {
      // API 返回了错误响应
      const status = err.response.status;
      const data = err.response.data;
      errorMessage = `API Error (${status}): ${data?.detail || data?.message || JSON.stringify(data)}`;
      console.error(`[Mem0 Adapter] ${operation} error:`, {
        status,
        data,
        url: err.config?.url
      });
    } else if (err.request) {
      // 请求发送了但没有收到响应
      errorMessage = `Network Error: Unable to reach API server at ${URL}`;
      console.error(`[Mem0 Adapter] ${operation} network error:`, err.request);
    } else {
      // 其他错误
      errorMessage = `Error: ${err.message || String(err)}`;
      console.error(`[Mem0 Adapter] ${operation} error:`, err);
    }
    
    setError(errorMessage);
    setIsLoading(false);
    throw new Error(errorMessage);
  }

  // 前端分页和过滤实现
  const applyFilters = (items: Memory[], filters?: {
    apps?: string[];
    categories?: string[];
    sortColumn?: string;
    sortDirection?: 'asc' | 'desc';
    showArchived?: boolean;
  }): Memory[] => {
    let filtered = [...items];

    if (filters?.apps && filters.apps.length > 0) {
      filtered = filtered.filter(m => filters.apps!.includes(m.app_name || ''));
    }

    if (filters?.categories && filters.categories.length > 0) {
      filtered = filtered.filter(m => 
        m.categories.some(cat => 
          filters.categories!.includes(typeof cat === 'string' ? cat : cat.name || '')
        )
      );
    }

    if (filters?.sortColumn) {
      const direction = filters.sortDirection === 'desc' ? -1 : 1;
      filtered.sort((a, b) => {
        let aVal: any, bVal: any;
        switch (filters.sortColumn) {
          case 'memory':
            aVal = a.memory;
            bVal = b.memory;
            break;
          case 'created_at':
            aVal = a.created_at;
            bVal = b.created_at;
            break;
          case 'app_name':
            aVal = a.app_name || '';
            bVal = b.app_name || '';
            break;
          default:
            return 0;
        }
        if (aVal < bVal) return -1 * direction;
        if (aVal > bVal) return 1 * direction;
        return 0;
      });
    }

    return filtered;
  };

  const fetchMemories = useCallback(async (
    query?: string,
    page: number = 1,
    size: number = 10,
    filters?: {
      apps?: string[];
      categories?: string[];
      sortColumn?: string;
      sortDirection?: 'asc' | 'desc';
      showArchived?: boolean;
    }
  ): Promise<{ memories: Memory[], total: number, pages: number }> => {
    setIsLoading(true);
    setError(null);
    try {
      let response: any;
      
      if (query) {
        // 使用搜索接口
        console.log('[Mem0 Adapter] Searching memories:', { query, user_id });
        response = await axios.post(
          `${URL}/search`,
          {
            query: query,
            user_id: user_id
          }
        );
      } else {
        // 获取所有记忆
        console.log('[Mem0 Adapter] Fetching all memories:', { user_id });
        response = await axios.get(
          `${URL}/memories`,
          {
            params: { user_id: user_id }
          }
        );
      }
      
      console.log('[Mem0 Adapter] API Response:', {
        status: response.status,
        dataType: typeof response.data,
        isArray: Array.isArray(response.data),
        hasResults: !!response.data?.results
      });
      
      // 使用灵活的适配函数
      const allMemories = adaptMem0Response(response.data);
      
      console.log('[Mem0 Adapter] Adapted memories:', allMemories.length);

      // 应用前端过滤
      const filtered = applyFilters(allMemories, filters);
      
      // 前端分页
      const total = filtered.length;
      const pages = Math.ceil(total / size);
      const start = (page - 1) * size;
      const end = start + size;
      const paginated = filtered.slice(start, end);

      setIsLoading(false);
      dispatch(setMemoriesSuccess(paginated));
      return {
        memories: paginated,
        total: total,
        pages: pages
      };
    } catch (err: any) {
      handleError(err, 'fetch memories');
    }
  }, [user_id, dispatch, URL]);

  const createMemory = async (text: string): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      console.log('[Mem0 Adapter] Creating memory:', { text, user_id });
      const response = await axios.post(
        `${URL}/memories`,
        {
          messages: [
            {
              role: "user",
              content: text
            }
          ],
          user_id: user_id
        }
      );
      console.log('[Mem0 Adapter] Create memory response:', response.data);
      setIsLoading(false);
    } catch (err: any) {
      handleError(err, 'create memory');
    }
  };

  const deleteMemories = async (memory_ids: string[]) => {
    setIsLoading(true);
    setError(null);
    try {
      console.log('[Mem0 Adapter] Deleting memories:', memory_ids);
      // Mem0 API 只支持单个删除，需要循环删除
      await Promise.all(
        memory_ids.map(id => 
          axios.delete(`${URL}/memories/${id}`)
        )
      );
      dispatch(setMemoriesSuccess(memories.filter((memory: Memory) => !memory_ids.includes(memory.id))));
      setIsLoading(false);
    } catch (err: any) {
      handleError(err, 'delete memories');
    }
  };

  const fetchMemoryById = async (memoryId: string): Promise<void> => {
    if (memoryId === "") {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      console.log('[Mem0 Adapter] Fetching memory by ID:', memoryId);
      const response = await axios.get(`${URL}/memories/${memoryId}`);
      
      const adapted = adaptMem0Response(response.data);
      if (adapted.length === 0) {
        throw new Error('Memory not found');
      }
      
      const memory = adapted[0];
      setIsLoading(false);
      dispatch(setSelectedMemory({
        id: memory.id,
        text: memory.memory,
        created_at: new Date(memory.created_at).toISOString(),
        state: "active",
        categories: [],
        app_name: memory.app_name || 'mem0'
      }));
    } catch (err: any) {
      handleError(err, 'fetch memory');
    }
  };

  // Mem0 API 不支持访问日志，返回空数组
  const fetchAccessLogs = async (memoryId: string, page: number = 1, pageSize: number = 10): Promise<void> => {
    setIsLoading(false);
    dispatch(setAccessLogs([]));
  };

  // Mem0 API 不支持相关记忆，使用搜索代替
  const fetchRelatedMemories = async (memoryId: string): Promise<void> => {
    if (memoryId === "") {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      // 获取当前记忆内容作为查询
      const currentMemory = memories.find(m => m.id === memoryId);
      if (!currentMemory) {
        setIsLoading(false);
        return;
      }

      const response = await axios.post(
        `${URL}/search`,
        {
          query: currentMemory.memory.substring(0, 100),
          user_id: user_id
        }
      );

      const adapted = adaptMem0Response(response.data);
      const relatedMemories = adapted
        .filter(item => item.id !== memoryId)
        .slice(0, 5);

      setIsLoading(false);
      dispatch(setRelatedMemories(relatedMemories));
    } catch (err: any) {
      handleError(err, 'fetch related memories');
    }
  };

  const updateMemory = async (memoryId: string, content: string): Promise<void> => {
    if (memoryId === "") {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      console.log('[Mem0 Adapter] Updating memory:', { memoryId, content });
      // 注意：Mem0 API 的 update 方法接受的 data 格式需要确认
      await axios.put(`${URL}/memories/${memoryId}`, {
        memory: content
      });
      setIsLoading(false);
      setHasUpdates(hasUpdates + 1);
    } catch (err: any) {
      handleError(err, 'update memory');
    }
  };

  // Mem0 API 不支持状态管理，这里只是标记（实际不改变状态）
  const updateMemoryState = async (memoryIds: string[], state: string): Promise<void> => {
    if (memoryIds.length === 0) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      // 如果是删除状态，实际删除记忆
      if (state === "deleted" || state === "archived") {
        await Promise.all(
          memoryIds.map(id => 
            axios.delete(`${URL}/memories/${id}`)
          )
        );
        dispatch(setMemoriesSuccess(memories.filter((memory: Memory) => !memoryIds.includes(memory.id))));
      } else {
        // 其他状态（暂停等）在 Mem0 中不支持，只更新本地状态
        dispatch(setMemoriesSuccess(memories.map((memory: Memory) => {
          if (memoryIds.includes(memory.id)) {
            return { ...memory, state: state as "active" | "paused" | "archived" | "deleted" };
          }
          return memory;
        })));
      }

      setIsLoading(false);
      setHasUpdates(hasUpdates + 1);
    } catch (err: any) {
      handleError(err, 'update memory state');
    }
  };

  return {
    fetchMemories,
    fetchMemoryById,
    fetchAccessLogs,
    fetchRelatedMemories,
    createMemory,
    deleteMemories,
    updateMemory,
    updateMemoryState,
    isLoading,
    error,
    hasUpdates,
    memories,
    selectedMemory
  };
};

