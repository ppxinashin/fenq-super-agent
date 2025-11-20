from __future__ import annotations
"""定时扫描开启长期记忆的用户并发送 MQ 任务"""

import asyncio
from typing import List

from src.config.settings import settings
from src.model.crud_user_memory_setting import crud_user_memory_setting
from src.model.database import get_db_session
from src.mq import RabbitMQClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

_global_producer: "MemorySyncProducer" | None = None


class MemorySyncProducer:
    """负责定时查询开启长期记忆的用户并发送同步任务"""

    def __init__(self, mq_client: RabbitMQClient):
        self.mq_client = mq_client

    async def enqueue_enabled_users(self) -> None:
        """将所有开启长期记忆的用户推送到消息队列"""
        try:
            # 查询数据库使用阻塞驱动，将其放在线程池避免阻塞事件循环
            usernames = await asyncio.to_thread(self._fetch_enabled_usernames)
            if not usernames:
                logger.info("没有开启长期记忆的用户，跳过消息投递")
                return

            logger.info(f"准备为 {len(usernames)} 个用户发送同步任务")
            delay = settings.mq_publish_delay_ms / 1000

            for username in usernames:
                await self.mq_client.publish_memory_task(username)
                if delay > 0:
                    await asyncio.sleep(delay)

            logger.info("本轮同步任务投递完成")
        except Exception as exc:
            logger.error(f"发送同步任务失败: {exc}")
            raise

    def _fetch_enabled_usernames(self) -> List[str]:
        """查询开启长期记忆的用户"""
        with get_db_session() as db:
            return crud_user_memory_setting.list_enabled_usernames(db)


def set_global_producer(producer: MemorySyncProducer) -> None:
    """注册全局 producer，用于 APScheduler 序列化调用"""
    global _global_producer
    _global_producer = producer


async def run_memory_sync_job() -> None:
    """供 APScheduler 调用的可序列化入口，不携带不可 pickle 的实例"""
    if not _global_producer:
        raise RuntimeError("MemorySyncProducer 未初始化")
    await _global_producer.enqueue_enabled_users()
