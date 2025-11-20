"""入口脚本：启动调度器和 MQ 消费者"""

import asyncio

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config.settings import settings
from src.model import init_database
from src.mq import RabbitMQClient
from src.tasks import (
    MemorySyncConsumer,
    MemorySyncProducer,
    run_memory_sync_job,
    set_global_producer,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def start_scheduler(producer: MemorySyncProducer) -> AsyncIOScheduler:
    """初始化并启动定时任务调度器"""
    jobstore = SQLAlchemyJobStore(url=settings.scheduler_store_url)
    scheduler = AsyncIOScheduler(
        jobstores={"default": jobstore},
        timezone=settings.scheduler_timezone,
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": settings.scheduler_misfire_grace_seconds,
        },
    )

    # APScheduler SQLAlchemyJobStore 需要可pickle的函数，这里使用模块级入口
    scheduler.add_job(
        run_memory_sync_job,
        trigger="interval",
        minutes=settings.memory_sync_interval_minutes,
        id="memory_sync_dispatch",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"定时任务启动成功：每 {settings.memory_sync_interval_minutes} 分钟派发一次记忆同步任务"
    )
    return scheduler


async def main():
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")

    # 确保表存在
    init_database()

    mq_client = RabbitMQClient()
    await mq_client.connect()

    producer = MemorySyncProducer(mq_client)
    set_global_producer(producer)
    consumer = MemorySyncConsumer(mq_client)

    # 先跑一次全量同步再交给定时任务
    await producer.enqueue_enabled_users()
    await consumer.start()

    scheduler = await start_scheduler(producer)

    try:
        # 阻塞直至收到中断信号
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("收到退出信号，开始优雅关闭...")
    finally:
        scheduler.shutdown(wait=False)
        await mq_client.close()
        logger.info("服务已关闭")


if __name__ == "__main__":
    asyncio.run(main())
