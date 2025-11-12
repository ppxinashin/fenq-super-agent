"""
JWT Token 工具类
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JWTUtil:
    """JWT Token 工具类"""
    
    @staticmethod
    def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        创建 JWT Token
        
        Args:
            data: 要编码的数据（通常包含用户ID、用户名等）
            expires_delta: 过期时间增量，默认使用配置中的值
            
        Returns:
            JWT Token 字符串
        """
        to_encode = data.copy()
        
        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        # 生成 Token
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        解码 JWT Token
        
        Args:
            token: JWT Token 字符串
            
        Returns:
            解码后的数据字典，失败返回 None
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token 已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token 无效: {e}")
            return None
    
    @staticmethod
    def verify_token(token: str) -> bool:
        """
        验证 Token 是否有效
        
        Args:
            token: JWT Token 字符串
            
        Returns:
            Token 是否有效
        """
        return JWTUtil.decode_token(token) is not None
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        """
        从 Token 中获取用户 ID
        
        Args:
            token: JWT Token 字符串
            
        Returns:
            用户 ID，失败返回 None
        """
        payload = JWTUtil.decode_token(token)
        if payload:
            return payload.get("user_id")
        return None
    
    @staticmethod
    def get_username_from_token(token: str) -> Optional[str]:
        """
        从 Token 中获取用户名
        
        Args:
            token: JWT Token 字符串
            
        Returns:
            用户名，失败返回 None
        """
        payload = JWTUtil.decode_token(token)
        if payload:
            return payload.get("username")
        return None


# 全局工具实例
jwt_util = JWTUtil()

