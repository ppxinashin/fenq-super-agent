"""
Redis 短期记忆
"""
import os
from dataclasses import dataclass
from langgraph.checkpoint.redis import AsyncRedisSaver, RedisSaver
from src.config import settings


class RedisShortMemory:    
    """
    Redis 短期记忆
    """
    ttl: int = 1440
    
    @classmethod
    def _checkpointer(cls):
        with RedisSaver.from_conn_string(settings.redis_url, ttl={"default_ttl": cls.ttl}) as checkpointer:
            checkpointer.setup()
            yield checkpointer
            
    @classmethod
    async def _acheckpointer(cls):
        os.environ['REDIS_URL'] = settings.redis_url
        async with AsyncRedisSaver.from_conn_string(settings.redis_url, ttl={"default_ttl": cls.ttl}) as checkpointer:
            await checkpointer.asetup()
        return checkpointer
            
    @classmethod
    def get_checkpointer(cls):
        return next(cls._checkpointer())
    
    @classmethod
    async def get_acheckpointer(cls):
        return await cls._acheckpointer()