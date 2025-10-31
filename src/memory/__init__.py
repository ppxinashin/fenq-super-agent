"""
记忆管理模块 - 使用 Redis 实现对话历史持久化
"""

from .redis_memory import RedisMessageHistory, get_redis_memory

__all__ = ["RedisMessageHistory", "get_redis_memory"]

