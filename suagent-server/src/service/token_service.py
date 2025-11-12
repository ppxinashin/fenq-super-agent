"""
Token管理服务
"""

import json
import redis
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from src.config.settings import settings
from src.response.auth_response import UserInfo
import logging

logger = logging.getLogger(__name__)


class TokenService:
    """Token管理服务"""

    def __init__(self):
        """初始化Token服务"""
        self.redis_client = None
        self.settings = settings
        self._init_redis()

    def _init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.redis_client = None

    def create_access_token(self, user_info: Dict[str, Any]) -> str:
        """
        创建JWT访问令牌

        Args:
            user_info: 用户信息字典

        Returns:
            JWT令牌字符串
        """
        # 设置过期时间
        expire_delta = timedelta(minutes=settings.jwt_expire_minutes)
        expire_time = datetime.utcnow() + expire_delta

        # 创建JWT payload
        payload = {
            "sub": str(user_info["id"]),  # subject: 用户ID
            "username": user_info["username"],
            "role": user_info["role"],
            "exp": expire_time,
            "iat": datetime.utcnow(),  # issued at
            "type": "access"
        }

        # 生成JWT令牌
        token = jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )

        # 将token和用户信息存储到Redis
        if self.redis_client:
            try:
                redis_key = f"token:{token}"
                user_data = {
                    "user_id": user_info["id"],
                    "username": user_info["username"],
                    "role": user_info["role"],
                    "created_at": datetime.utcnow().isoformat(),
                    "expires_at": expire_time.isoformat()
                }

                # 设置过期时间比JWT稍长一些
                redis_expire = settings.jwt_expire_minutes * 60 + 300  # +5分钟缓冲

                self.redis_client.setex(
                    redis_key,
                    redis_expire,
                    json.dumps(user_data)
                )
                logger.info(f"Token已存储到Redis: {redis_key}")
            except Exception as e:
                logger.error(f"存储token到Redis失败: {e}")

        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT令牌

        Args:
            token: JWT令牌字符串

        Returns:
            验证成功返回payload，失败返回None
        """
        try:
            # 解码JWT令牌
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )

            # 检查token类型
            if payload.get("type") != "access":
                logger.warning("Token类型不正确")
                return None

            # 检查是否过期（jose会自动检查exp）
            return payload

        except JWTError as e:
            logger.warning(f"JWT验证失败: {e}")
            return None
        except Exception as e:
            logger.error(f"Token验证异常: {e}")
            return None

    def get_user_info_from_redis(self, token: str) -> Optional[Dict[str, Any]]:
        """
        从Redis获取用户信息

        Args:
            token: JWT令牌字符串

        Returns:
            用户信息字典，未找到返回None
        """
        if not self.redis_client:
            logger.warning("Redis未连接")
            return None

        try:
            redis_key = f"token:{token}"
            user_data_str = self.redis_client.get(redis_key)

            if user_data_str:
                user_data = json.loads(user_data_str)
                logger.info(f"从Redis获取用户信息成功: {user_data['username']}")
                return user_data
            else:
                logger.warning(f"Redis中未找到token: {redis_key}")
                return None

        except Exception as e:
            logger.error(f"从Redis获取用户信息失败: {e}")
            return None

    def revoke_token(self, token: str) -> bool:
        """
        撤销token（从Redis中删除）

        Args:
            token: 要撤销的token

        Returns:
            是否成功撤销
        """
        if not self.redis_client:
            logger.warning("Redis未连接，无法撤销token")
            return False

        try:
            redis_key = f"token:{token}"
            result = self.redis_client.delete(redis_key)

            if result > 0:
                logger.info(f"Token已从Redis中撤销: {redis_key}")
                return True
            else:
                logger.warning(f"Redis中未找到要撤销的token: {redis_key}")
                return False

        except Exception as e:
            logger.error(f"撤销token失败: {e}")
            return False

    def refresh_token(self, token: str) -> Optional[str]:
        """
        刷新token

        Args:
            token: 原token

        Returns:
            新token，失败返回None
        """
        # 验证原token
        payload = self.verify_token(token)
        if not payload:
            return None

        # 检查Redis中是否存在
        user_data = self.get_user_info_from_redis(token)
        if not user_data:
            return None

        # 撤销原token
        self.revoke_token(token)

        # 创建新token
        new_token = self.create_access_token({
            "id": payload["sub"],
            "username": payload["username"],
            "role": payload["role"]
        })

        logger.info(f"Token刷新成功: {payload['username']}")
        return new_token

    def is_token_valid(self, token: str) -> bool:
        """
        检查token是否有效

        Args:
            token: JWT令牌字符串

        Returns:
            是否有效
        """
        # JWT验证
        payload = self.verify_token(token)
        if not payload:
            return False

        # Redis验证
        user_data = self.get_user_info_from_redis(token)
        if not user_data:
            return False

        return True

    def get_token_expire_time(self) -> int:
        """
        获取token过期时间（秒）

        Returns:
            过期时间（秒）
        """
        return settings.jwt_expire_minutes * 60

    def cleanup_expired_tokens(self) -> int:
        """
        清理过期的token（手动清理，通常Redis会自动清理）

        Returns:
            清理的token数量
        """
        if not self.redis_client:
            return 0

        try:
            # 查找所有token键
            token_keys = self.redis_client.keys("token:*")
            cleaned_count = 0

            for key in token_keys:
                user_data_str = self.redis_client.get(key)
                if user_data_str:
                    try:
                        user_data = json.loads(user_data_str)
                        expires_at = datetime.fromisoformat(user_data["expires_at"])

                        # 如果已过期，删除
                        if datetime.utcnow() > expires_at:
                            self.redis_client.delete(key)
                            cleaned_count += 1

                    except (json.JSONDecodeError, ValueError):
                        # 数据格式错误，直接删除
                        self.redis_client.delete(key)
                        cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"清理了 {cleaned_count} 个过期token")

            return cleaned_count

        except Exception as e:
            logger.error(f"清理过期token失败: {e}")
            return 0


# 全局Token服务实例
token_service = TokenService()