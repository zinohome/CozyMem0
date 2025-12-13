/**
 * Mem0 API 适配的 useStats Hook
 * 通过调用 Mem0 API 计算统计数据
 */

import { useState } from 'react';
import axios from 'axios';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '@/store/store';
import { setApps, setTotalApps } from '@/store/profileSlice';
import { setTotalMemories } from '@/store/profileSlice';

interface UseMemoriesApiReturn {
  fetchStats: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export const useStats = (): UseMemoriesApiReturn => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const dispatch = useDispatch<AppDispatch>();
  const user_id = useSelector((state: RootState) => state.profile.userId);

  const URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8888";

  const fetchStats = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // 获取所有记忆来计算总数
      const response = await axios.get(`${URL}/memories`, {
        params: { user_id: user_id }
      });
      
      const memories = response.data.results || [];
      const totalMemories = memories.length;
      
      dispatch(setTotalMemories(totalMemories));
      dispatch(setTotalApps(1)); // Mem0 只有一个默认应用
      dispatch(setApps([{ id: 'mem0-default', name: 'Mem0' }]));
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch stats';
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  };

  return { fetchStats, isLoading, error };
};

