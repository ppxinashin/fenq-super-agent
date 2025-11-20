"""RabbitMQ 客户端，仅负责声明拓扑并发布记忆同步任务。"""

import asyncio
import json
from typing import Optional

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message
from aio_pika.abc import (
    AbstractRobustChannel,
    AbstractRobustConnection,
    AbstractRobustExchange,
    AbstractRobustQueue,
)

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RabbitMQClient:
    """封装 RabbitMQ 连接、拓扑声明与可靠发布."""

    def __init__(self):
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel: Optional[AbstractRobustChannel] = None
        self._exchange: Optional[AbstractRobustExchange] = None
        self._dlx_exchange: Optional[AbstractRobustExchange] = None
        self._queue: Optional[AbstractRobustQueue] = None
        self._dlx_queue: Optional[AbstractRobustQueue] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        """建立连接并声明 exchange/queue。重复调用可复用现有连接。"""
        async with self._lock:
            if self._connection and not self._connection.is_closed:
                return

            logger.info("连接 RabbitMQ 中...")
            self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            self._channel = await self._connection.channel(publisher_confirms=True)
            await self._channel.set_qos(prefetch_count=settings.mq_prefetch_count)

            await self._declare_topology()
            logger.info("RabbitMQ 连接与队列声明完成")

    async def _declare_topology(self) -> None:
        """声明交换机、主队列、死信队列并建立绑定。"""
        assert self._channel, "channel 未初始化"

        self._exchange = await self._channel.declare_exchange(
            settings.mq_exchange,
            ExchangeType.DIRECT,
            durable=True,
        )

        self._dlx_exchange = await self._channel.declare_exchange(
            settings.mq_dead_letter_exchange,
            ExchangeType.DIRECT,
            durable=True,
        )

        self._queue = await self._channel.declare_queue(
            settings.mq_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.mq_dead_letter_exchange,
                "x-dead-letter-routing-key": settings.mq_dead_letter_routing_key,
                "x-message-ttl": settings.mq_message_ttl_ms,
            },
        )
        await self._queue.bind(self._exchange, routing_key=settings.mq_routing_key)

        self._dlx_queue = await self._channel.declare_queue(
            settings.mq_dead_letter_queue,
            durable=True,
        )
        await self._dlx_queue.bind(
            self._dlx_exchange, routing_key=settings.mq_dead_letter_routing_key
        )

    async def publish_memory_task(self, username: str) -> None:
        """发布单个用户的记忆同步任务，等待 publisher confirm。"""
        await self.connect()
        assert self._exchange, "exchange 未初始化"

        payload = json.dumps({"username": username}).encode("utf-8")
        message = Message(
            payload,
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        try:
            await self._exchange.publish(
                message,
                routing_key=settings.mq_routing_key,
                mandatory=True,
            )
            logger.info(f"[MQ] 发布记忆同步任务成功 username={username}")
        except aio_pika.exceptions.DeliveryError as exc:
            logger.error(f"[MQ] 任务未送达 username={username}: {exc}")
            raise
        except Exception as exc:
            logger.error(f"[MQ] 发布记忆同步任务失败 username={username}: {exc}")
            raise

    async def close(self) -> None:
        """关闭连接资源。"""
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
