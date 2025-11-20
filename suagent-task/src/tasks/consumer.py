"""MQ 消费者：并发消费用户记忆同步任务，确保幂等与 ACK。"""

import asyncio
from typing import Dict

from src.config.settings import settings
from src.mq import RabbitMQClient
from src.service.memory_setting_service import memory_setting_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MemorySyncConsumer:
    """消费消息并执行用户记忆同步"""

    def __init__(self, mq_client: RabbitMQClient):
        self.mq_client = mq_client
        self._semaphore = asyncio.Semaphore(settings.mq_consumer_max_concurrency)
        self._user_locks: Dict[str, asyncio.Lock] = {}

    async def start(self) -> None:
        """启动消费者监听"""
        await self.mq_client.consume_memory_tasks(self._handle_message)
        logger.info("记忆同步消费者已启动，等待消息...")

    def _get_user_lock(self, username: str) -> asyncio.Lock:
        """每个用户一个锁，防止同一用户并发同步导致状态漂移"""
        if username not in self._user_locks:
            self._user_locks[username] = asyncio.Lock()
        return self._user_locks[username]

    async def _handle_message(self, payload: dict) -> None:
        username = payload["username"]

        if not await asyncio.to_thread(memory_setting_service.get_memory_status, username):
            logger.warning(f"[MQ] 用户 {username} 未开启长期记忆，跳过任务")
            return

        async with self._semaphore:
            user_lock = self._get_user_lock(username)
            async with user_lock:
                logger.info(f"[MQ] 开始执行用户 {username} 的记忆同步")
                await memory_setting_service.sync_user_memory(username)
                logger.info(f"[MQ] 完成用户 {username} 的记忆同步")
