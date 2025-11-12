"""
JWT认证中间件
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.model.database import get_db
from src.response.auth_response import UserInfo
from src.service.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer 认证方案
security = HTTPBearer(auto_error=False)


async def get_current_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> UserInfo:
    """
    从JWT token中获取当前用户信息

    Args:
        credentials: HTTP认证凭据
        db: 数据库会话

    Returns:
        用户信息

    Raises:
        HTTPException: 认证失败时抛出异常
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证token，请在Header中提供Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # 验证token并获取用户信息
        user_info = auth_service.get_current_user_info(db, token)

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token无效或已过期，请重新登录",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取当前用户信息异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败，请稍后重试",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[UserInfo]:
    """
    可选的JWT token认证（不会抛出异常）

    Args:
        credentials: HTTP认证凭据
        db: 数据库会话

    Returns:
        用户信息，token无效时返回None
    """
    if not credentials:
        return None

    token = credentials.credentials

    try:
        user_info = auth_service.get_current_user_info(db, token)
        return user_info

    except Exception as e:
        logger.warning(f"可选认证获取用户信息失败: {e}")
        return None


async def get_current_user_from_token_strict(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> UserInfo:
    """
    严格的JWT token认证（同时验证JWT和Redis）

    Args:
        credentials: HTTP认证凭据
        db: 数据库会话

    Returns:
        用户信息

    Raises:
        HTTPException: 认证失败时抛出异常
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证token，请在Header中提供Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # 严格验证token（JWT + Redis + 数据库）
        is_valid = auth_service.validate_token(db, token)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token无效或已过期，请重新登录",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 获取用户信息
        user_info = auth_service.get_current_user_info(db, token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法获取用户信息，请重新登录",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"严格认证获取用户信息异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败，请稍后重试",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(required_role: str):
    """
    角色权限装饰器工厂

    Args:
        required_role: 需要的角色（"admin" 或 "user"）

    Returns:
        依赖函数
    """
    async def role_checker(
        current_user: UserInfo = Depends(get_current_user_from_token)
    ) -> UserInfo:
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要 {required_role} 权限",
            )
        return current_user

    return role_checker


# 预定义的角色依赖
require_admin = require_role("admin")
require_user = require_role("user")


def require_any_role(*allowed_roles: str):
    """
    多角色权限检查

    Args:
        allowed_roles: 允许的角色列表

    Returns:
        依赖函数
    """
    async def role_checker(
        current_user: UserInfo = Depends(get_current_user_from_token)
    ) -> UserInfo:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下权限之一: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


# 预定义的多角色依赖
require_admin_or_user = require_any_role("admin", "user")


async def get_token_from_header(
    authorization: Optional[str] = None
) -> Optional[str]:
    """
    从Authorization header中提取token

    Args:
        authorization: Authorization header值

    Returns:
        token字符串，无效时返回None
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    return authorization.split(" ")[1]


class JWTAuthMiddleware:
    """JWT认证中间件类（用于FastAPI中间件）"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """
        ASGI中间件调用

        Args:
            scope: ASGI scope
            receive: ASGI receive
            send: ASGI send
        """
        # 只处理HTTP请求
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 获取Authorization header
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            # 将token添加到scope中，供后续使用
            scope["jwt_token"] = token

        await self.app(scope, receive, send)


def get_token_from_scope(scope) -> Optional[str]:
    """
    从ASGI scope中获取JWT token

    Args:
        scope: ASGI scope

    Returns:
        token字符串，不存在时返回None
    """
    return scope.get("jwt_token")