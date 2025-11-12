"""
Celery Application - Celery 应用配置和初始化
"""

import os
import logging
from celery import Celery
from src.scheduler.config import *

# 配置日志
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# 创建 Celery 应用
celery_app = Celery(
    'memory_sync_scheduler',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['src.scheduler.tasks']
)

# 配置 Celery
celery_app.conf.update(
    # 序列化配置
    task_serializer=CELERY_TASK_SERIALIZER,
    result_serializer=CELERY_RESULT_SERIALIZER,
    accept_content=CELERY_ACCEPT_CONTENT,
    timezone=CELERY_TIMEZONE,
    enable_utc=CELERY_ENABLE_UTC,

    # 任务执行配置
    task_track_started=CELERY_TASK_TRACK_STARTED,
    task_time_limit=CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=CELERY_TASK_SOFT_TIME_LIMIT,
    worker_prefetch_multiplier=CELERY_WORKER_PREFETCH_MULTIPLIER,
    worker_max_tasks_per_child=CELERY_WORKER_MAX_TASKS_PER_CHILD,

    # 重试和可靠性配置
    task_reject_on_worker_lost=CELERY_TASK_REJECT_ON_WORKER_LOST,
    task_acks_late=CELERY_TASK_ACKS_LATE,

    # 调度配置
    beat_schedule=CELERY_BEAT_SCHEDULE,
)

# 任务路由配置
celery_app.conf.task_routes = {
    'src.scheduler.tasks.sync_daily_user_memory': {'queue': 'memory_sync'},
    'src.scheduler.tasks.sync_user_memories': {'queue': 'memory_sync'},
    'src.scheduler.tasks.upload_session_memory': {'queue': 'storage'},
    'src.scheduler.tasks.cleanup_old_logs': {'queue': 'maintenance'},
}

# 任务优先级配置
celery_app.conf.task_default_priority = 5
celery_app.conf.worker_direct = True

# 启动时验证配置
@celery_app.task(bind=True)
def startup_validation(self):
    """启动时验证配置"""
    try:
        from src.scheduler.memory_sync_service import MemorySyncService
        from src.scheduler.minio_client import MinIOClient

        # 验证数据库连接
        service = MemorySyncService()
        users_count = service.get_long_memory_users_count()
        logger.info(f"Found {users_count} users with long memory enabled")

        # 验证 MinIO 连接
        minio_client = MinIOClient()
        bucket_exists = minio_client.check_bucket_exists()
        logger.info(f"MinIO bucket '{MINIO_MEMORY_BUCKET}' exists: {bucket_exists}")

        if not bucket_exists:
            logger.warning(f"MinIO bucket '{MINIO_MEMORY_BUCKET}' does not exist, creating it...")
            minio_client.create_bucket()

        logger.info("Scheduler startup validation completed successfully")
        return True

    except Exception as exc:
        logger.error(f"Scheduler startup validation failed: {exc}")
        raise

if __name__ == '__main__':
    celery_app.start()