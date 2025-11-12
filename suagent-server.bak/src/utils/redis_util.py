"""
Redis 工具类
"""

import json
from typing import Optional, Any
import redis
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RedisUtil:
    """Redis 工具类"""
    
    _client: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """
        获取 Redis 客户端（单例模式）
        
        Returns:
            Redis 客户端实例
        """
        if cls._client is None:
            cls._client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True  # 自动解码为字符串
            )
            logger.info("Redis 客户端连接成功")
        return cls._client
    
    @classmethod
    def set(cls, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置键值
        
        Args:
            key: 键
            value: 值（会自动序列化为 JSON）
            expire: 过期时间（秒），None 表示不过期
            
        Returns:
            是否设置成功
        """
        try:
            client = cls.get_client()
            # 如果值不是字符串，转换为 JSON
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            
            if expire:
                return client.setex(key, expire, value)
            else:
                return client.set(key, value)
        except Exception as e:
            logger.error(f"Redis set 失败: {e}")
            return False
    
    @classmethod
    def get(cls, key: str, as_json: bool = False) -> Optional[Any]:
        """
        获取键值
        
        Args:
            key: 键
            as_json: 是否将值解析为 JSON
            
        Returns:
            值，不存在返回 None
        """
        try:
            client = cls.get_client()
            value = client.get(key)
            
            if value is None:
                return None
            
            if as_json:
                return json.loads(value)
            
            return value
        except Exception as e:
            logger.error(f"Redis get 失败: {e}")
            return None
    
    @classmethod
    def delete(cls, key: str) -> bool:
        """
        删除键
        
        Args:
            key: 键
            
        Returns:
            是否删除成功
        """
        try:
            client = cls.get_client()
            return client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis delete 失败: {e}")
            return False
    
    @classmethod
    def exists(cls, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 键
            
        Returns:
            是否存在
        """
        try:
            client = cls.get_client()
            return client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists 失败: {e}")
            return False
    
    @classmethod
    def expire(cls, key: str, seconds: int) -> bool:
        """
        设置键的过期时间
        
        Args:
            key: 键
            seconds: 过期时间（秒）
            
        Returns:
            是否设置成功
        """
        try:
            client = cls.get_client()
            return client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire 失败: {e}")
            return False
    
    @classmethod
    def ttl(cls, key: str) -> int:
        """
        获取键的剩余过期时间
        
        Args:
            key: 键
            
        Returns:
            剩余时间（秒），-1 表示永不过期，-2 表示键不存在
        """
        try:
            client = cls.get_client()
            return client.ttl(key)
        except Exception as e:
            logger.error(f"Redis ttl 失败: {e}")
            return -2
    
    @classmethod
    def close(cls):
        """关闭 Redis 连接"""
        if cls._client:
            cls._client.close()
            cls._client = None
            logger.info("Redis 客户端连接已关闭")


# 全局工具实例
redis_util = RedisUtil()

