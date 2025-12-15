import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ProfileState {
  userId: string;
  totalMemories: number;
  totalApps: number;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
  apps: any[];
}

// 从 localStorage 读取用户ID（如果存在），否则使用环境变量或默认值
const getInitialUserId = (): string => {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('mem0_user_id');
    if (stored) {
      return stored;
    }
  }
  return process.env.NEXT_PUBLIC_USER_ID || 'user';
};

const initialState: ProfileState = {
  userId: getInitialUserId(),
  totalMemories: 0,
  totalApps: 0,
  status: 'idle',
  error: null,
  apps: [],
};

const profileSlice = createSlice({
  name: 'profile',
  initialState,
  reducers: {
    setUserId: (state, action: PayloadAction<string>) => {
      state.userId = action.payload;
      // 保存到 localStorage（仅在客户端）
      if (typeof window !== 'undefined') {
        localStorage.setItem('mem0_user_id', action.payload);
      }
    },
    setProfileLoading: (state) => {
      state.status = 'loading';
      state.error = null;
    },
    setProfileError: (state, action: PayloadAction<string>) => {
      state.status = 'failed';
      state.error = action.payload;
    },
    resetProfileState: (state) => {
      state.status = 'idle';
      state.error = null;
      state.userId = getInitialUserId();
    },
    setTotalMemories: (state, action: PayloadAction<number>) => {
      state.totalMemories = action.payload;
    },
    setTotalApps: (state, action: PayloadAction<number>) => {
      state.totalApps = action.payload;
    },
    setApps: (state, action: PayloadAction<any[]>) => {
      state.apps = action.payload;
    }
  },
});

export const {
  setUserId,
  setProfileLoading,
  setProfileError,
  resetProfileState,
  setTotalMemories,
  setTotalApps,
  setApps
} = profileSlice.actions;

export default profileSlice.reducer;

