/**
 * Mem0 API 适配的 useFiltersApi Hook
 * Mem0 API 不支持分类管理，返回空分类列表
 */

import { useState, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/store/store';
import {
  Category,
  setCategoriesLoading,
  setCategoriesSuccess,
  setCategoriesError,
  setSortingState,
  setSelectedApps,
  setSelectedCategories
} from '@/store/filtersSlice';

export interface UseFiltersApiReturn {
  fetchCategories: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
  updateApps: (apps: string[]) => void;
  updateCategories: (categories: string[]) => void;
  updateSort: (column: string, direction: 'asc' | 'desc') => void;
}

export const useFiltersApi = (): UseFiltersApiReturn => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const dispatch = useDispatch<AppDispatch>();

  // Mem0 API 不支持分类管理，返回空列表
  const fetchCategories = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    dispatch(setCategoriesLoading());
    try {
      dispatch(setCategoriesSuccess({
        categories: [],
        total: 0
      }));
      setIsLoading(false);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to fetch categories';
      setError(errorMessage);
      dispatch(setCategoriesError(errorMessage));
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  }, [dispatch]);

  const updateApps = useCallback((apps: string[]) => {
    dispatch(setSelectedApps(apps));
  }, [dispatch]);

  const updateCategories = useCallback((categories: string[]) => {
    dispatch(setSelectedCategories(categories));
  }, [dispatch]);

  const updateSort = useCallback((column: string, direction: 'asc' | 'desc') => {
    dispatch(setSortingState({ column, direction }));
  }, [dispatch]);

  return {
    fetchCategories,
    isLoading,
    error,
    updateApps,
    updateCategories,
    updateSort
  };
};

