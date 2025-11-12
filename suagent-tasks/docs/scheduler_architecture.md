# Memory Sync Scheduler 定时记忆同步系统架构设计

## 系统架构概览

```mermaid
graph TB
    A[Celery Beat 定时调度器] --> B[Daily Memory Sync Task]
    B --> C[筛选长期记忆用户]
    C --> D[按用户分组处理]
    D --> E[获取会话数据]
    E --> F[格式化Markdown]
    F --> G[上传MinIO存储]
    G --> H[任务状态记录]

    I[RabbitMQ消息队列] --> B
    B --> I

    J[错误处理模块] --> K[重试机制]
    K --> L[告警通知]
```

## 技术栈

- **任务队列**: Celery 5.5 + RabbitMQ 4.2+
- **对象存储**: MinIO
- **数据库**: PostgreSQL
- **定时调度**: Celery Beat

## 目录结构

```
src/scheduler/
├── __init__.py
├── celery_app.py              # Celery 应用配置
├── tasks.py                   # 主要任务定义
├── memory_sync_service.py     # 记忆同步核心业务
├── minio_client.py           # MinIO 客户端封装
├── config.py                 # 配置管理
└── utils/
    ├── __init__.py
    ├── formatter.py          # Markdown 格式化工具
    └── retry_handler.py      # 重试处理器
```

## 数据流程

1. **定时触发**: 每日凌晨 2:00 自动执行
2. **用户筛选**: 查询 `user_memory_settings.enabled = true` 的用户
3. **数据获取**: 查询前一日对话数据（按 session_id 分组）
4. **内容处理**: 格式化为标准 Markdown 格式
5. **文件存储**: 上传至 MinIO (`memory/{user_id}/{session_title}_{yyyyMMdd}.md`)
6. **状态记录**: 记录同步状态和统计信息

## 核心组件设计

### 1. Celery 配置
- 连接 RabbitMQ 作为消息代理
- 配置任务重试和错误处理
- 设置任务序列化格式

### 2. 记忆同步服务
- 用户筛选逻辑
- 会话数据聚合
- 文件命名规则
- 数据一致性检查

### 3. MinIO 存储客户端
- 连接池管理
- 文件上传逻辑
- 权限控制
- 错误处理

### 4. 可靠性保障
- 自动重试机制
- 异常捕获和处理
- 任务状态监控
- 告警通知

## 配置参数

```python
# Celery 配置
CELERY_BROKER_URL = "amqp://guest:guest@localhost:15672/"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# 任务调度配置
MEMORY_SYNC_SCHEDULE = "0 2 * * *"  # 每日凌晨2点

# MinIO 配置
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "your-access-key"
MINIO_SECRET_KEY = "your-secret-key"
MINIO_SECURE = False
MINIO_MEMORY_BUCKET = "user-memories"
```

## 任务流程示例

```python
@app.task(bind=True, max_retries=3)
def sync_user_daily_memory(self):
    """同步用户日常记忆任务"""
    try:
        # 1. 获取开启长期记忆的用户列表
        users = get_users_with_long_memory_enabled()

        # 2. 按用户处理数据
        for user_id in users:
            sync_user_memories.delay(user_id, date_range)

    except Exception as exc:
        self.retry(countdown=60, exc=exc)
```

## 错误处理策略

1. **连接失败**: 自动重试 3 次，每次间隔递增
2. **数据异常**: 记录错误日志，跳过异常数据
3. **存储失败**: 本地缓存，稍后重试
4. **配置错误**: 启动时验证，提前失败

## 监控和日志

- 任务执行状态记录
- 性能指标收集
- 错误统计和分析
- 存储使用量监控