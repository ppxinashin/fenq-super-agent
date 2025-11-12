"""
Scheduler Configuration - 定时任务配置管理
使用新的 Pydantic Settings 配置系统
"""

from datetime import timedelta
from celery.schedules import crontab
from ..config.settings import settings

# ===== Celery 配置 (从新配置系统获取) =====
CELERY_BROKER_URL = settings.celery_broker_url
CELERY_RESULT_BACKEND = settings.celery_result_backend

# 任务序列化配置
CELERY_TASK_SERIALIZER = settings.celery_task_serializer
CELERY_RESULT_SERIALIZER = settings.celery_result_serializer
CELERY_ACCEPT_CONTENT = settings.celery_accept_content
CELERY_TIMEZONE = settings.celery_timezone
CELERY_ENABLE_UTC = settings.celery_enable_utc

# 任务执行配置
CELERY_TASK_TRACK_STARTED = settings.celery_task_track_started
CELERY_TASK_TIME_LIMIT = settings.celery_task_time_limit
CELERY_TASK_SOFT_TIME_LIMIT = settings.celery_task_soft_time_limit
CELERY_WORKER_PREFETCH_MULTIPLIER = settings.celery_worker_prefetch_multiplier
CELERY_WORKER_MAX_TASKS_PER_CHILD = settings.celery_worker_max_tasks_per_child
CELERY_WORKER_CONCURRENCY = settings.celery_worker_concurrency

# 重试配置
CELERY_TASK_REJECT_ON_WORKER_LOST = settings.celery_task_reject_on_worker_lost
CELERY_TASK_ACKS_LATE = settings.celery_task_acks_late

# ===== MinIO 配置 =====
MINIO_ENDPOINT = settings.minio_endpoint
MINIO_ACCESS_KEY = settings.minio_access_key
MINIO_SECRET_KEY = settings.minio_secret_key
MINIO_SECURE = settings.minio_secure
MINIO_MEMORY_BUCKET = settings.minio_memory_bucket
MINIO_SSL_CERT_PATH = settings.minio_ssl_cert_path
MINIO_SSL_KEY_PATH = settings.minio_ssl_key_path

# ===== 定时任务配置 =====
MEMORY_SYNC_SCHEDULE = crontab(
    hour=settings.memory_sync_schedule_hour,
    minute=settings.memory_sync_schedule_minute
)
MEMORY_SYNC_DATE_RANGE_DAYS = settings.memory_sync_date_range_days

# ===== 数据库配置 =====
DATABASE_URL = settings.database_url

# ===== 日志配置 =====
LOG_LEVEL = settings.log_level
LOG_FORMAT = settings.log_format
LOG_FILE_PATH = settings.log_file_path
LOG_ROTATION = settings.log_rotation
LOG_RETENTION = settings.log_retention

# ===== 告警配置 =====
ALERT_EMAIL_ENABLED = settings.alert_email_enabled
ALERT_EMAIL_SMTP_HOST = settings.alert_email_smtp_host
ALERT_EMAIL_SMTP_PORT = settings.alert_email_smtp_port
ALERT_EMAIL_USERNAME = settings.alert_email_username
ALERT_EMAIL_PASSWORD = settings.alert_email_password
ALERT_EMAIL_TO = settings.alert_email_to

# ===== 性能配置 =====
MAX_CONCURRENT_USERS = settings.max_concurrent_users
BATCH_SIZE = settings.batch_size
MEMORY_SYNC_RETRY_DELAY = settings.memory_sync_retry_delay
MEMORY_SYNC_MAX_RETRIES = settings.memory_sync_max_retries

# ===== 记忆管理配置 =====
MEMORY_SYNC_ENABLED = settings.memory_sync_enabled
MEMORY_CLEANUP_ENABLED = settings.memory_cleanup_enabled
MEMORY_CLEANUP_DAYS = settings.memory_cleanup_days

# ===== Flower 监控配置 =====
FLOWER_ENABLED = settings.flower_enabled
FLOWER_PORT = settings.flower_port
FLOWER_BASIC_AUTH = settings.flower_basic_auth

# Celery Beat 调度配置
CELERY_BEAT_SCHEDULE = {
    'sync-daily-user-memory': {
        'task': 'src.scheduler.tasks.sync_daily_user_memory',
        'schedule': MEMORY_SYNC_SCHEDULE,
        'options': {
            'queue': 'memory_sync',
            'priority': 5,
        }
    },
    'cleanup-old-logs': {
        'task': 'src.scheduler.tasks.cleanup_old_logs',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # 每周一凌晨3点
        'options': {
            'queue': 'maintenance',
            'priority': 2,
        }
    }
}