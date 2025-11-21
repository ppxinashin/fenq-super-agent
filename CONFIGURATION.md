# Fenq Super Agent 配置指南

## 环境变量与 .env
- 所有服务都读取同目录下的 `.env`，首次部署请从对应的 `.env.example` 复制：
  - `cp suagent-app/.env.example suagent-app/.env`
  - `cp suagent-server/.env.example suagent-server/.env`
  - `cp suagent-rag/.env.example suagent-rag/.env`
  - `cp suagent-task/.env.example suagent-task/.env`
  - `cp suagent-youtube-mcp/.env.example suagent-youtube-mcp/.env`
- **suagent-app**：`NEXT_PUBLIC_API_BASE_URL` 必须指向后端服务（容器网络内使用 `http://suagent-server:8000`）。
- **suagent-server**：
  - API: `API_HOST`/`API_PORT`（容器内保持 `0.0.0.0:8000`）。
  - OpenAI/通义：`OPENAI_API_KEY`、`OPENAI_API_BASE`、`OPENAI_MODEL`、`DASHSCOPE_API_KEY`。
  - 数据存储：`POSTGRES_HOST/PORT/USER/PASSWORD/DB` 与 `POSTGRES_RAG_*`；缓存 `REDIS_*`。
  - 消息队列：`RABBITMQ_*` 和 DLX 相关队列参数。
  - 其他：`LANGSMITH_*`、`EMBEDDING_MODEL`、`VECTOR_STORE_COLLECTION`、`MINIO_*`、`ENABLE_WEB_SEARCH`。
- **suagent-rag**：`DASHSCOPE_API_KEY`、PostgreSQL (`POSTGRES_*` + `POSTGRES_RAG_*`)、`EMBEDDING_MODEL`、`VECTOR_STORE_COLLECTION`、`MINIO_*`、`MINERU_API_TOKEN`/`OPEN_OCR`。
- **suagent-task**：PostgreSQL (`POSTGRES_*` 或 `SCHEDULER_JOB_STORE_URL`)、调度参数（如 `MEMORY_SYNC_INTERVAL_MINUTES`）、RabbitMQ (`RABBITMQ_*` 和 MQ 前缀变量)、`MINIO_*`。
- **suagent-youtube-mcp**：`FASTMCP_HOST`/`FASTMCP_PORT`（默认 `0.0.0.0:10086`），`YOUTUBE_API_KEY`，`YOUTUBE_SEARCH_LIMIT`（默认 5）。

## 服务间通信
- `docker-compose.yml` 定义了自定义桥接网络 `suagent-network`，容器可通过服务名互访，无需额外 DNS。
- 典型访问：
  - 前端调用后端：请根据你的域名修改。
  - 其他内部依赖（PostgreSQL/Redis/RabbitMQ/MinIO）使用各自容器名或外部地址，根据你的部署实际填写。

## 首次部署步骤
1. 复制环境变量模板并填写实际值（见上文示例）。
2. 在项目根目录执行 `docker compose up -d --build` 构建并启动全部服务。
3. 验证：`curl -f http://localhost:8000/health`（后端健康检查），前端可通过 `http://localhost:11451` 访问。

## 日常运维命令（在项目根目录）
- 查看运行状态：`docker compose ps`
- 跟踪日志：`docker compose logs -f suagent-server`（替换为任意服务名）
- 进入容器：`docker compose exec suagent-server /bin/sh`
- 重启单个服务：`docker compose restart suagent-youtube-mcp`
- 重新构建并启动：`docker compose up -d --build`
- 停止并清理：`docker compose down -v`
