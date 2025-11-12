# Memory Sync Scheduler 部署指南

## 概述

本文档详细说明了如何部署和配置定时记忆同步系统。

## 系统要求

### 基础依赖
- **Python**: 3.8+
- **操作系统**: Linux (推荐 Ubuntu 20.04+)
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘**: 最低 10GB 可用空间

### 外部服务
- **PostgreSQL**: 12+
- **RabbitMQ**: 3.8+
- **Redis**: 6.0+
- **MinIO**: RELEASE.2023-01-02T09-40-09Z+

## 安装步骤

### 1. 环境准备

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

### 2. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 或者安装特定版本的依赖
pip install celery==5.3.0
pip install minio==7.2.0
pip install sqlalchemy==2.0.0
pip install psycopg2-binary==2.9.5
pip install redis==5.0.0
```

### 3. 配置环境变量

```bash
# 复制配置模板
cp config/scheduler.env.example .env

# 编辑配置文件
vim .env
```

**必需配置项：**
```bash
# 数据库连接
DATABASE_URL=postgresql://username:password@localhost:5432/suagent

# RabbitMQ 连接
CELERY_BROKER_URL=amqp://username:password@localhost:5672//

# Redis 连接
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
```

### 4. 数据库初始化

确保数据库中存在必要的表：

```sql
-- 用户长期记忆设置表
CREATE TABLE IF NOT EXISTS user_memory_settings (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'admin',
    updated_by VARCHAR(100) DEFAULT 'admin',
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_memory_settings_username
ON user_memory_settings(username);
```

### 5. MinIO 初始化

```bash
# 创建 MinIO 客户端配置
mkdir -p ~/.mc
mc alias set local http://localhost:9000 minioadmin minioadmin

# 创建存储桶
mc mb local/user-memories

# 设置存储桶策略（可选）
mc policy set public local/user-memories
```

## 启动服务

### 1. 启动基础服务

```bash
# 启动 RabbitMQ
sudo systemctl start rabbitmq-server

# 启动 Redis
sudo systemctl start redis-server

# 启动 PostgreSQL
sudo systemctl start postgresql

# 启动 MinIO
minio server /data --console-address ":9001"
```

### 2. 启动 Celery Worker

```bash
# 启动 Celery Worker
celery -A src.scheduler.celery_app worker \
  --loglevel=info \
  --queues=memory_sync,storage,maintenance \
  --concurrency=4 \
  --max-tasks-per-child=50

# 后台启动
nohup celery -A src.scheduler.celery_app worker \
  --loglevel=info \
  --queues=memory_sync,storage,maintenance \
  --concurrency=4 \
  --max-tasks-per-child=50 \
  > /var/log/celery-worker.log 2>&1 &
```

### 3. 启动 Celery Beat

```bash
# 启动定时任务调度器
celery -A src.scheduler.celery_app beat \
  --loglevel=info \
  --schedule=/tmp/celerybeat-schedule

# 后台启动
nohup celery -A src.scheduler.celery_app beat \
  --loglevel=info \
  --schedule=/tmp/celerybeat-schedule \
  > /var/log/celery-beat.log 2>&1 &
```

### 4. 启动 Celery Flower (可选，监控界面)

```bash
# 安装 Flower
pip install flower

# 启动 Flower
celery -A src.scheduler.celery_app flower \
  --port=5555 \
  --basic_auth=admin:password

# 访问监控界面
# http://localhost:5555
```

## 服务管理

### Systemd 服务配置

创建 `/etc/systemd/system/celery-worker.service`：

```ini
[Unit]
Description=Celery Worker Service
After=network.target

[Service]
Type=forking
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/fenq-super-agent/suagent-server
Environment=PATH=/home/ubuntu/fenq-super-agent/suagent-server/venv/bin
ExecStart=/home/ubuntu/fenq-super-agent/suagent-server/venv/bin/celery -A src.scheduler.celery_app worker --loglevel=info --queues=memory_sync,storage,maintenance --detach
ExecStop=/home/ubuntu/fenq-super-agent/suagent-server/venv/bin/celery -A src.scheduler.celery_app control shutdown
ExecReload=/home/ubuntu/fenq-super-agent/suagent-server/venv/bin/celery -A src.scheduler.celery_app control reload
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

创建 `/etc/systemd/system/celery-beat.service`：

```ini
[Unit]
Description=Celery Beat Service
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/fenq-super-agent/suagent-server
Environment=PATH=/home/ubuntu/fenq-super-agent/suagent-server/venv/bin
ExecStart=/home/ubuntu/fenq-super-agent/suagent-server/venv/bin/celery -A src.scheduler.celery_app beat --loglevel=info --schedule=/tmp/celerybeat-schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用和启动服务：

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable celery-worker celery-beat

# 启动服务
sudo systemctl start celery-worker celery-beat

# 查看状态
sudo systemctl status celery-worker celery-beat
```

## 监控和日志

### 日志配置

日志文件位置：
- Celery Worker: `/var/log/celery-worker.log`
- Celery Beat: `/var/log/celery-beat.log`
- 应用日志: 通过标准日志框架配置

### 监控指标

使用 Celery Flower 监控：
```bash
# 安装和配置 Flower
pip install flower

# 启动监控
celery -A src.scheduler.celery_app flower --port=5555
```

关键监控指标：
- 任务执行成功率
- 任务执行时间
- 队列长度
- Worker 状态
- 内存使用情况

### 告警配置

配置邮件告警：

```bash
# 在 .env 文件中配置
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_SMTP_HOST=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_USERNAME=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-password
ALERT_EMAIL_TO=admin@example.com,ops@example.com
```

## 性能优化

### Celery 配置优化

```python
# 在 config.py 中调整性能参数
CELERY_WORKER_CONCURRENCY = 4  # 根据 CPU 核心数调整
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 50
CELERY_TASK_TIME_LIMIT = 3600
CELERY_TASK_SOFT_TIME_LIMIT = 3000
```

### 数据库优化

```sql
-- 创建必要的索引
CREATE INDEX CONCURRENTLY idx_session_logs_created_at
ON session_logs(created_at);

CREATE INDEX CONCURRENTLY idx_session_logs_session_id_created_at
ON session_logs(session_id, created_at);

-- 定期清理旧数据
DELETE FROM session_logs
WHERE created_at < NOW() - INTERVAL '90 days';
```

### MinIO 优化

```bash
# 设置存储桶生命周期策略
mc ilm rule add local/user-memories --expire-days 365
```

## 故障排查

### 常见问题

1. **连接 RabbitMQ 失败**
   ```bash
   # 检查 RabbitMQ 状态
   sudo systemctl status rabbitmq-server

   # 检查连接配置
   rabbitmqctl list_connections
   ```

2. **数据库连接问题**
   ```bash
   # 测试数据库连接
   psql -h localhost -U postgres -d suagent

   # 检查数据库配置
   echo $DATABASE_URL
   ```

3. **MinIO 连接问题**
   ```bash
   # 测试 MinIO 连接
   mc admin info local

   # 检查存储桶状态
   mc ls local/user-memories
   ```

### 日志分析

查看关键日志：
```bash
# 查看 Worker 日志
tail -f /var/log/celery-worker.log

# 查看 Beat 日志
tail -f /var/log/celery-beat.log

# 查看系统日志
journalctl -u celery-worker -f
journalctl -u celery-beat -f
```

## 安全配置

### 网络安全

```bash
# 配置防火墙
sudo ufw allow 5672    # RabbitMQ
sudo ufw allow 6379    # Redis
sudo ufw allow 9000    # MinIO
sudo ufw allow 5432    # PostgreSQL
```

### 访问控制

```bash
# RabbitMQ 用户管理
rabbitmqctl add_user scheduler password123
rabbitmqctl set_user_tags scheduler monitoring
rabbitmqctl set_permissions -p / scheduler ".*" ".*" ".*"

# Redis 密码配置
redis-cli CONFIG SET requirepass your-redis-password
```

### SSL/TLS 配置

```bash
# MinIO SSL 配置
MINIO_SECURE=true
MINIO_SSL_CERT_PATH=/path/to/cert.pem
MINIO_SSL_KEY_PATH=/path/to/key.pem
```

## 备份和恢复

### 数据备份

```bash
# 数据库备份
pg_dump -h localhost -U postgres suagent > backup_$(date +%Y%m%d).sql

# MinIO 备份
mc mirror local/user-memories backup/minio/$(date +%Y%m%d)/
```

### 配置备份

```bash
# 备份配置文件
tar -czf scheduler_config_$(date +%Y%m%d).tar.gz \
  .env \
  config/ \
  src/scheduler/
```

## 升级指南

### 版本升级

```bash
# 1. 备份当前版本
./scripts/backup.sh

# 2. 停止服务
sudo systemctl stop celery-worker celery-beat

# 3. 更新代码
git pull origin main

# 4. 更新依赖
pip install -r requirements.txt

# 5. 数据库迁移（如果需要）
alembic upgrade head

# 6. 重启服务
sudo systemctl start celery-worker celery-beat
```

### 回滚步骤

```bash
# 1. 停止服务
sudo systemctl stop celery-worker celery-beat

# 2. 切换到上一版本
git checkout previous_version_tag

# 3. 恢复依赖
pip install -r requirements.txt

# 4. 恢复配置
cp backup/scheduler_config.env .env

# 5. 重启服务
sudo systemctl start celery-worker celery-beat
```