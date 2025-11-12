"""
API中间件模块 - 用于FastAPI应用认证和权限控制
"""

from .jwt_middleware import (
    get_current_user_from_token,
    get_current_user_optional_from_token,
    get_current_user_from_token_strict,
    require_admin,
    require_user,
    require_any_role,
    require_admin_or_user,
    JWTAuthMiddleware,
    get_token_from_header,
    get_token_from_scope
)

__all__ = [
    "get_current_user_from_token",
    "get_current_user_optional_from_token",
    "get_current_user_from_token_strict",
    "require_admin",
    "require_user",
    "require_any_role",
    "require_admin_or_user",
    "JWTAuthMiddleware",
    "get_token_from_header",
    "get_token_from_scope"
]