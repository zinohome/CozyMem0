# Dockerfile for Mem0 WebUI - Development Mode
# 开发模式：使用 npm run dev，支持运行时环境变量
# 注意：开发模式性能较慢，仅用于开发/测试环境

FROM node:18-alpine AS base

# Install dependencies for pnpm and patch
RUN apk add --no-cache libc6-compat curl patch && \
    corepack enable && \
    corepack prepare pnpm@latest --activate

WORKDIR /app

FROM base AS deps

# Copy package files
COPY projects/mem0/openmemory/ui/package.json projects/mem0/openmemory/ui/pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile

FROM base AS dev
WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/pnpm-lock.yaml ./pnpm-lock.yaml

# Copy OpenMemory UI source
COPY projects/mem0/openmemory/ui ./

# Copy Mem0 API adapters to replace original hooks
COPY deployment/mem0/webui-adapters/useMemoriesApi.mem0.ts ./hooks/useMemoriesApi.ts
COPY deployment/mem0/webui-adapters/useAppsApi.mem0.ts ./hooks/useAppsApi.ts
COPY deployment/mem0/webui-adapters/useFiltersApi.mem0.ts ./hooks/useFiltersApi.ts
COPY deployment/mem0/webui-adapters/useStats.mem0.ts ./hooks/useStats.ts
COPY deployment/mem0/webui-adapters/useConfig.mem0.ts ./hooks/useConfig.ts

# Copy Mem0 UI adapters (user selector feature)
COPY deployment/mem0/webui-adapters/UserSelector.tsx ./components/UserSelector.tsx
COPY deployment/mem0/webui-adapters/profileSlice.mem0.ts ./store/profileSlice.ts
COPY deployment/mem0/webui-adapters/Navbar.mem0.tsx ./components/Navbar.tsx
COPY deployment/mem0/webui-adapters/settings-page.mem0.tsx ./app/settings/page.tsx

# Apply UI patches to remove unwanted features
COPY deployment/mem0/webui-patches/remove-apps-navbar.patch /tmp/remove-apps-navbar.patch
COPY deployment/mem0/webui-patches/remove-install-component.patch /tmp/remove-install-component.patch
RUN cd /app && \
    patch -p0 < /tmp/remove-apps-navbar.patch || (echo "Warning: Apps navbar patch failed" && true) && \
    patch -p0 < /tmp/remove-install-component.patch || (echo "Warning: Install component patch failed" && true)

# Use dev config
RUN cp next.config.dev.mjs next.config.mjs

# Expose port
EXPOSE 3000

# Set environment variables (can be overridden at runtime)
ENV NODE_ENV=development
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Default environment variables (can be overridden in docker-compose)
ENV NEXT_PUBLIC_API_URL=http://mem0-api:8000
ENV NEXT_PUBLIC_USER_ID=user

# Start in development mode
# 开发模式下，Next.js 会在运行时读取环境变量，无需重新构建
CMD ["pnpm", "run", "dev"]

