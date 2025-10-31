"""
Redis 记忆存储 - 基于 Redis 的对话历史管理
"""

from typing import List, Optional
import json
import redis
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import BaseChatMessageHistory

from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)


class RedisMessageHistory(BaseChatMessageHistory):
    """基于 Redis 的消息历史记录"""

    def __init__(
        self,
        session_id: str,
        redis_client: Optional[redis.Redis] = None,
        key_prefix: str = "chat_history",
        ttl: Optional[int] = 86400 * 7,  # 默认保留 7 天
    ):
        """
        初始化 Redis 消息历史
        
        Args:
            session_id: 会话 ID
            redis_client: Redis 客户端（可选）
            key_prefix: Redis key 前缀
            ttl: 过期时间（秒），None 表示永不过期
        """
        self.session_id = session_id
        self.key_prefix = key_prefix
        self.ttl = ttl
        
        if redis_client is None:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
        else:
            self.redis_client = redis_client
        
        self._key = f"{self.key_prefix}:{self.session_id}"
        logger.info(f"初始化 Redis 消息历史，会话 ID: {session_id}")

    def add_message(self, message: BaseMessage) -> None:
        """添加消息到历史记录"""
        try:
            # 序列化消息
            message_dict = {
                "type": message.type,
                "content": message.content,
            }
            message_json = json.dumps(message_dict, ensure_ascii=False)
            
            # 添加到 Redis 列表
            self.redis_client.rpush(self._key, message_json)
            
            # 设置过期时间
            if self.ttl:
                self.redis_client.expire(self._key, self.ttl)
            
            logger.debug(f"添加消息到会话 {self.session_id}: {message.type}")
        
        except Exception as e:
            logger.error(f"添加消息失败: {str(e)}")
            raise

    @property
    def messages(self) -> List[BaseMessage]:
        """获取所有消息"""
        try:
            # 从 Redis 获取所有消息
            message_jsons = self.redis_client.lrange(self._key, 0, -1)
            
            messages = []
            for message_json in message_jsons:
                message_dict = json.loads(message_json)
                message = self._deserialize_message(message_dict)
                messages.append(message)
            
            logger.debug(f"从会话 {self.session_id} 获取 {len(messages)} 条消息")
            return messages
        
        except Exception as e:
            logger.error(f"获取消息失败: {str(e)}")
            return []

    def clear(self) -> None:
        """清除历史记录"""
        try:
            self.redis_client.delete(self._key)
            logger.info(f"清除会话 {self.session_id} 的历史记录")
        except Exception as e:
            logger.error(f"清除历史记录失败: {str(e)}")
            raise

    def _deserialize_message(self, message_dict: dict) -> BaseMessage:
        """反序列化消息"""
        message_type = message_dict.get("type")
        content = message_dict.get("content")
        
        if message_type == "human":
            return HumanMessage(content=content)
        elif message_type == "ai":
            return AIMessage(content=content)
        elif message_type == "system":
            return SystemMessage(content=content)
        else:
            # 默认返回 HumanMessage
            return HumanMessage(content=content)


def get_redis_memory(session_id: str) -> RedisMessageHistory:
    """
    获取 Redis 记忆实例
    
    Args:
        session_id: 会话 ID
    
    Returns:
        RedisMessageHistory 实例
    """
    return RedisMessageHistory(session_id=session_id)

