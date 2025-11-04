"""
Redis 短期记忆
"""

from dataclasses import dataclass
from langgraph.checkpoint.redis import RedisSaver
from src.config import settings


@dataclass
class RedisShortMemory:
    """
    Redis 短期记忆
    """
    @classmethod
    def _checkpointer(cls):
        with RedisSaver.from_conn_string(settings.redis_url) as checkpointer:
            checkpointer.setup()
            yield checkpointer
            
    @classmethod
    def get_checkpointer(cls):
        return next(cls._checkpointer())