# Dockerfile for Mem0 WebUI (adapted from OpenMemory UI)
# 基于 OpenMemory UI，适配 Mem0 API

# syntax=docker.io/docker/dockerfile:1

# Base stage for common setup
FROM node:18-alpine AS base

# Install dependencies for pnpm and patch tool
RUN apk add --no-cache libc6-compat curl patch && \
    corepack enable && \
    corepack prepare pnpm@latest --activate

WORKDIR /app

FROM base AS deps

# Copy package files
COPY projects/mem0/openmemory/ui/package.json projects/mem0/openmemory/ui/pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile

FROM base AS builder
WORKDIR /app

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

# Use dev config for standalone build
RUN cp next.config.dev.mjs next.config.mjs

# Set environment variables for Mem0 API
ENV NEXT_PUBLIC_API_URL=http://192.168.66.11:8888

# Build the application
RUN pnpm build

FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Copy entrypoint script from builder stage (it was copied in builder stage)
COPY --from=builder --chown=nextjs:nodejs /app/entrypoint.sh /home/nextjs/entrypoint.sh
RUN chmod +x /home/nextjs/entrypoint.sh

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

ENTRYPOINT ["/home/nextjs/entrypoint.sh"]
CMD ["node", "server.js"]

