/**
 * Mem0 API 适配的 useConfig Hook
 * Mem0 API 支持配置，但格式不同
 */

import { useState } from 'react';
import axios from 'axios';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/store/store';
import {
  setConfigLoading,
  setConfigSuccess,
  setConfigError,
  updateLLM,
  updateEmbedder,
  updateMem0Config,
  updateOpenMemory,
  LLMProvider,
  EmbedderProvider,
  Mem0Config,
  OpenMemoryConfig
} from '@/store/configSlice';

interface UseConfigApiReturn {
  fetchConfig: () => Promise<void>;
  saveConfig: (config: { openmemory?: OpenMemoryConfig; mem0: Mem0Config }) => Promise<void>;
  saveLLMConfig: (llmConfig: LLMProvider) => Promise<void>;
  saveEmbedderConfig: (embedderConfig: EmbedderProvider) => Promise<void>;
  resetConfig: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export const useConfig = (): UseConfigApiReturn => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const dispatch = useDispatch<AppDispatch>();
  const URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8888";
  
  // Mem0 API 不支持配置获取，返回默认配置
  const fetchConfig = async () => {
    setIsLoading(true);
    dispatch(setConfigLoading());
    
    try {
      const defaultConfig = {
        mem0: {
          llm: {
            provider: "openai",
            config: {
              model: "gpt-4o-mini",
              temperature: 0.2,
              api_key: "env:OPENAI_API_KEY"
            }
          },
          embedder: {
            provider: "openai",
            config: {
              model: "text-embedding-3-small",
              api_key: "env:OPENAI_API_KEY"
            }
          },
          vector_store: {
            provider: "pgvector",
            config: {}
          }
        }
      };
      dispatch(setConfigSuccess(defaultConfig));
      setIsLoading(false);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch configuration';
      dispatch(setConfigError(errorMessage));
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  };

  const saveConfig = async (config: { openmemory?: OpenMemoryConfig; mem0: Mem0Config }) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 转换配置格式为 Mem0 API 格式
      const mem0Config = {
        version: "v1.1",
        llm: config.mem0.llm,
        embedder: config.mem0.embedder,
        vector_store: config.mem0.vector_store
      };
      
      await axios.post(`${URL}/api/v1/configure`, mem0Config);
      dispatch(setConfigSuccess(config));
      setIsLoading(false);
      return config;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to save configuration';
      dispatch(setConfigError(errorMessage));
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  };

  const resetConfig = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Mem0 API 不支持重置配置，返回默认配置
      const defaultConfig = {
        mem0: {
          llm: {
            provider: "openai",
            config: {
              model: "gpt-4o-mini",
              temperature: 0.2
            }
          },
          embedder: {
            provider: "openai",
            config: {
              model: "text-embedding-3-small"
            }
          }
        }
      };
      dispatch(setConfigSuccess(defaultConfig));
      setIsLoading(false);
      return defaultConfig;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to reset configuration';
      dispatch(setConfigError(errorMessage));
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  };

  const saveLLMConfig = async (llmConfig: LLMProvider) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 需要先获取当前配置，然后更新 LLM 配置
      const currentConfig = {
        version: "v1.1",
        llm: llmConfig,
        embedder: {
          provider: "openai",
          config: {
            model: "text-embedding-3-small"
          }
        },
        vector_store: {
          provider: "pgvector",
          config: {}
        }
      };
      
      await axios.post(`${URL}/api/v1/configure`, currentConfig);
      dispatch(updateLLM(llmConfig));
      setIsLoading(false);
      return llmConfig;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to save LLM configuration';
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  };

  const saveEmbedderConfig = async (embedderConfig: EmbedderProvider) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 需要先获取当前配置，然后更新 Embedder 配置
      const currentConfig = {
        version: "v1.1",
        llm: {
          provider: "openai",
          config: {
            model: "gpt-4o-mini"
          }
        },
        embedder: embedderConfig,
        vector_store: {
          provider: "pgvector",
          config: {}
        }
      };
      
      await axios.post(`${URL}/api/v1/configure`, currentConfig);
      dispatch(updateEmbedder(embedderConfig));
      setIsLoading(false);
      return embedderConfig;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to save Embedder configuration';
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  };

  return {
    fetchConfig,
    saveConfig,
    saveLLMConfig,
    saveEmbedderConfig,
    resetConfig,
    isLoading,
    error
  };
};

