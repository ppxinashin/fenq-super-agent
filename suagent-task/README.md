# Fenq Super Agent - Memory Sync Task

一个纯定时任务进程，每 2 小时扫描开启长期记忆的用户，把每个用户名作为独立任务投递到 RabbitMQ，并异步消费后将该用户的聊天日志重新上传到 MinIO（先删后建，保证幂等）。

## 架构与可靠性
- **调度**：APScheduler + SQLAlchemy JobStore（默认复用 PostgreSQL）持久化任务计划，错过执行自动补偿（`scheduler_misfire_grace_seconds`）。
- **消息队列**：RabbitMQ 直连交换机 + 持久化队列 + 持久化消息，开启 publisher confirms；队列开启 TTL + DLX，未消费的消息会被路由到死信队列。
- **生产者限速**：逐条发送并基于 `MQ_PUBLISH_DELAY_MS` 放缓速度，避免突发堆积。
- **消费者并发**：异步消费，`MQ_CONSUMER_MAX_CONCURRENCY` 控制并发，`MQ_PREFETCH_COUNT` 控制预取；同一用户加锁，避免并发写导致状态漂移。
- **幂等**：同步前先清理用户现有 memory 目录，再整体重建；消息失败 nack 后重回队列，成功才 ack。

## 运行步骤
1. 准备依赖：Python 3.11+、PostgreSQL、RabbitMQ、MinIO。
2. 安装依赖：`pip install -r requirements.txt`。
3. 配置环境：`cp .env.example .env` 并填写数据库、RabbitMQ、MinIO 信息，按需调整调度周期/时区。
4. 初始化表：`python -m src.model.init_db`（或执行 `scripts/` 下的 SQL）。
5. 启动任务：`python -m src.task_runner` 或 `./start.sh` 后台运行。

## 关键配置（.env）
- PostgreSQL：`POSTGRES_HOST/PORT/USER/PASSWORD/DB`，或自定义 `SCHEDULER_JOB_STORE_URL`。
- 调度：`SCHEDULER_TIMEZONE`、`MEMORY_SYNC_INTERVAL_MINUTES`（默认 120 分钟）。
- RabbitMQ：`RABBITMQ_HOST/PORT/USERNAME/PASSWORD/VIRTUAL_HOST`，交换机/队列/路由键及 DLX/TTL 由 `MQ_*` 前缀控制。
- 消费控制：`MQ_PREFETCH_COUNT`、`MQ_CONSUMER_MAX_CONCURRENCY`、`MQ_PUBLISH_DELAY_MS`。
- MinIO：`MINIO_ENDPOINT`、`MINIO_ACCESS_KEY`、`MINIO_SECRET_KEY`、`MINIO_BUCKET`。

## 核心流程
1. `MemorySyncProducer.enqueue_enabled_users`：查询 `user_memory_settings.enabled = true` 的用户名，逐条发送持久化消息并等待 confirm。
2. `RabbitMQClient`：声明持久化直连交换机/队列、TTL + DLX，mandatory 发布失败直接报错，消费者成功后 ack，异常 nack 重回队列。
3. `MemorySyncConsumer`：异步消费，按用户加锁后调用 `memory_setting_service.sync_user_memory`。
4. `memory_setting_service`：删除用户现有 MinIO memory 文件，拉取会话日志拼成 Markdown，再按时间戳路径上传，保证多次执行结果一致。

## 目录
- `src/task_runner.py`：调度器与 MQ 入口。
- `src/tasks/`：生产/消费任务实现。
- `src/mq/`：RabbitMQ 客户端封装。
- `src/service/memory_setting_service.py`：长期记忆同步逻辑。
- `src/model/`：SQLAlchemy 模型与 CRUD。
- `scripts/`：数据库初始化 SQL。

## 常用命令
- 环境自检：`python check_environment.py`
- 启动：`python -m src.task_runner`（前台）或 `./start.sh`（后台）
- 停止后台任务：`kill $(cat logs/memory-sync-task.pid)`（或手动杀掉 PID）
