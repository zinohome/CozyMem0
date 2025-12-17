/**
 * Mem0 API 适配的 useMemoriesApi Hook
 * 将 OpenMemory UI 的接口调用适配到 Mem0 API
 */

import { useState, useCallback } from 'react';
import axios from 'axios';
import { Memory, Category } from '@/components/types';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '@/store/store';
import { setAccessLogs, setMemoriesSuccess, setSelectedMemory, setRelatedMemories } from '@/store/memoriesSlice';

// Mem0 API 响应格式
interface Mem0Memory {
  id: string;
  memory: string;
  created_at?: number;
  metadata?: Record<string, any>;
}

interface Mem0SearchResponse {
  results: Array<{
    id: string;
    memory: string;
    score?: number;
    metadata?: Record<string, any>;
  }>;
}

interface Mem0GetAllResponse {
  results: Mem0Memory[];
  relations?: Array<any>; // 图数据库关系（可选）
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

  // Mem0 API URL (默认端口 8888)
  const URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8888";

  // 前端分页和过滤实现
  const applyFilters = (items: Memory[], filters?: {
    apps?: string[];
    categories?: string[];
    sortColumn?: string;
    sortDirection?: 'asc' | 'desc';
    showArchived?: boolean;
  }): Memory[] => {
    let filtered = [...items];

    // 应用过滤（前端实现）
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

    // 应用排序
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
      let allMemories: Memory[] = [];

      if (query) {
        // 使用搜索接口
        const searchResponse = await axios.post<Mem0SearchResponse>(
          `${URL}/api/v1/search`,
          {
            query: query,
            user_id: user_id
          }
        );
        
        allMemories = searchResponse.data.results.map((item) => ({
          id: item.id,
          memory: item.memory,
          created_at: Date.now(), // Mem0 可能不返回时间戳
          state: "active" as const,
          metadata: item.metadata || {},
          categories: [] as Category[],
          client: 'api',
          app_name: item.metadata?.source_app || 'mem0'
        }));
      } else {
        // 获取所有记忆
        const response = await axios.get<Mem0GetAllResponse>(
          `${URL}/api/v1/memories`,
          {
            params: { user_id: user_id }
          }
        );
        
        // 处理响应格式：{results: [...], relations: [...]}
        // relations 是图数据库关系，当前不需要处理
        const results = response.data.results || [];
        
        allMemories = results.map((item) => ({
          id: item.id || String(item),
          memory: item.memory || '',
          created_at: item.created_at || Date.now(),
          state: "active" as const,
          metadata: item.metadata || {},
          categories: [] as Category[],
          client: 'api',
          app_name: item.metadata?.source_app || item.metadata?.app_name || 'mem0'
        }));
      }

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
      const errorMessage = err.message || 'Failed to fetch memories';
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  }, [user_id, dispatch, URL]);

  const createMemory = async (text: string): Promise<void> => {
    try {
      await axios.post(`${URL}/api/v1/memories`, {
        messages: [
          {
            role: "user",
            content: text
          }
        ],
        user_id: user_id
      });
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to create memory';
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  };

  const deleteMemories = async (memory_ids: string[]) => {
    try {
      // Mem0 API 只支持单个删除，需要循环删除
      await Promise.all(
        memory_ids.map(id => 
          axios.delete(`${URL}/api/v1/memories/${id}`)
        )
      );
      dispatch(setMemoriesSuccess(memories.filter((memory: Memory) => !memory_ids.includes(memory.id))));
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to delete memories';
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  };

  const fetchMemoryById = async (memoryId: string): Promise<void> => {
    if (memoryId === "") {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get<Mem0Memory>(
        `${URL}/api/v1/memories/${memoryId}`
      );
      setIsLoading(false);
      dispatch(setSelectedMemory({
        id: response.data.id,
        text: response.data.memory,
        created_at: new Date(response.data.created_at || Date.now()).toISOString(),
        state: "active",
        categories: [],
        app_name: response.data.metadata?.source_app || 'mem0'
      }));
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch memory';
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
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

      const response = await axios.post<Mem0SearchResponse>(
        `${URL}/api/v1/search`,
        {
          query: currentMemory.memory.substring(0, 100), // 使用前100字符作为查询
          user_id: user_id
        }
      );

      const adaptedMemories: Memory[] = response.data.results
        .filter(item => item.id !== memoryId) // 排除当前记忆
        .slice(0, 5) // 只取前5个
        .map((item) => ({
          id: item.id,
          memory: item.memory,
          created_at: Date.now(),
          state: "active" as const,
          metadata: item.metadata || {},
          categories: [] as Category[],
          client: 'api',
          app_name: item.metadata?.source_app || 'mem0'
        }));

      setIsLoading(false);
      dispatch(setRelatedMemories(adaptedMemories));
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch related memories';
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  };

  const updateMemory = async (memoryId: string, content: string): Promise<void> => {
    if (memoryId === "") {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      await axios.put(`${URL}/api/v1/memories/${memoryId}`, {
        memory: content
      });
      setIsLoading(false);
      setHasUpdates(hasUpdates + 1);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to update memory';
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
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
            axios.delete(`${URL}/api/v1/memories/${id}`)
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
      const errorMessage = err.message || 'Failed to update memory state';
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
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

