# Multi-stage build for suagent-app (Next.js frontend)
FROM node:24-alpine AS builder
WORKDIR /app
ENV NODE_ENV=production
# API 地址通过构建阶段读取同目录下的 .env（NEXT_PUBLIC_API_BASE_URL）。
# 如需覆盖，构建前写入 suagent-app/.env。

# Install dependencies and build
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:24-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/package.json /app/package-lock.json ./
RUN npm ci --omit=dev

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 11451
CMD ["npm", "run", "start"]
