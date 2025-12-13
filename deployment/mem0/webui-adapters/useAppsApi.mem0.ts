/**
 * Mem0 API 适配的 useAppsApi Hook
 * Mem0 API 不支持应用管理，返回空数据
 */

import { useState, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/store/store';
import {
  App,
  AppDetails,
  AppMemory,
  AccessedMemory,
  setAppsSuccess,
  setAppsError,
  setAppsLoading,
  setSelectedAppLoading,
  setSelectedAppDetails,
  setCreatedMemoriesLoading,
  setCreatedMemoriesSuccess,
  setCreatedMemoriesError,
  setAccessedMemoriesLoading,
  setAccessedMemoriesSuccess,
  setAccessedMemoriesError,
  setSelectedAppError,
} from '@/store/appsSlice';

interface FetchAppsParams {
  name?: string;
  is_active?: boolean;
  sort_by?: 'name' | 'memories' | 'memories_accessed';
  sort_direction?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

interface UseAppsApiReturn {
  fetchApps: (params?: FetchAppsParams) => Promise<{ apps: App[], total: number }>;
  fetchAppDetails: (appId: string) => Promise<void>;
  fetchAppMemories: (appId: string, page?: number, pageSize?: number) => Promise<void>;
  fetchAppAccessedMemories: (appId: string, page?: number, pageSize?: number) => Promise<void>;
  updateAppDetails: (appId: string, details: { is_active: boolean }) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export const useAppsApi = (): UseAppsApiReturn => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const dispatch = useDispatch<AppDispatch>();

  // Mem0 API 不支持应用管理，返回默认应用
  const fetchApps = useCallback(async (params: FetchAppsParams = {}): Promise<{ apps: App[], total: number }> => {
    setIsLoading(true);
    dispatch(setAppsLoading());
    try {
      // 返回一个默认的 mem0 应用
      const defaultApp: App = {
        id: 'mem0-default',
        name: 'Mem0',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        memories_count: 0,
        memories_accessed_count: 0
      };
      
      setIsLoading(false);
      dispatch(setAppsSuccess([defaultApp]));
      return {
        apps: [defaultApp],
        total: 1
      };
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch apps';
      setError(errorMessage);
      dispatch(setAppsError(errorMessage));
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  }, [dispatch]);

  const fetchAppDetails = useCallback(async (appId: string): Promise<void> => {
    setIsLoading(true);
    dispatch(setSelectedAppLoading());
    try {
      const defaultAppDetails: AppDetails = {
        id: appId,
        name: 'Mem0',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        memories_count: 0,
        memories_accessed_count: 0
      };
      dispatch(setSelectedAppDetails(defaultAppDetails));
      setIsLoading(false);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch app details';
      dispatch(setSelectedAppError(errorMessage));
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  }, [dispatch]);

  const fetchAppMemories = useCallback(async (appId: string, page: number = 1, pageSize: number = 10): Promise<void> => {
    setIsLoading(true);
    dispatch(setCreatedMemoriesLoading());
    try {
      dispatch(setCreatedMemoriesSuccess({
        items: [],
        total: 0,
        page: 1,
      }));
      setIsLoading(false);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch app memories';
      dispatch(setCreatedMemoriesError(errorMessage));
      setError(errorMessage);
      setIsLoading(false);
    }
  }, [dispatch]);

  const fetchAppAccessedMemories = useCallback(async (appId: string, page: number = 1, pageSize: number = 10): Promise<void> => {
    setIsLoading(true);
    dispatch(setAccessedMemoriesLoading());
    try {
      dispatch(setAccessedMemoriesSuccess({
        items: [],
        total: 0,
        page: 1,
      }));
      setIsLoading(false);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch accessed memories';
      dispatch(setAccessedMemoriesError(errorMessage));
      setError(errorMessage);
      setIsLoading(false);
    }
  }, [dispatch]);

  const updateAppDetails = async (appId: string, details: { is_active: boolean }) => {
    setIsLoading(true);
    try {
      // Mem0 API 不支持应用管理，只返回成功
      setIsLoading(false);
    } catch (error) {
      console.error("Failed to update app details:", error);
      setIsLoading(false);
      throw error;
    }
  };

  return {
    fetchApps,
    fetchAppDetails,
    fetchAppMemories,
    fetchAppAccessedMemories,
    updateAppDetails,
    isLoading,
    error
  };
};

