"""
用户角色校验中间件
"""

from functools import wraps
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import List, Optional
from src.utils.jwt_util import JWTUtil
from src.consts.user_consts import UserConsts
from src.response.base_response import ApiResponse


class RoleMiddleware:
    """角色校验中间件类"""

    @staticmethod
    def require_roles(required_roles: List[str]):
        """
        装饰器：要求用户具有指定角色之一

        Args:
            required_roles: 允许的角色列表
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 从请求中获取token
                request = None

                # 查找Request对象参数
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

                if not request:
                    # 如果没在args中找到，尝试在kwargs中找
                    for key, value in kwargs.items():
                        if isinstance(value, Request):
                            request = value
                            break

                if not request:
                    return JSONResponse(
                        status_code=500,
                        content=ApiResponse.error("无法获取请求对象", 500).model_dump()
                    )

                # 从请求头获取token
                authorization: str = request.headers.get("Authorization")
                if not authorization or not authorization.startswith("Bearer "):
                    return JSONResponse(
                        status_code=401,
                        content=ApiResponse.error("缺少有效的认证token", 401).model_dump()
                    )

                token = authorization.split(" ")[1]

                # 解析token
                try:
                    payload = JWTUtil.decode_token(token)
                    user_role = payload.get("role")

                    if not user_role:
                        return JSONResponse(
                            status_code=403,
                            content=ApiResponse.error("token中缺少用户角色信息", 403).model_dump()
                        )

                    # 检查用户角色是否在允许的角色列表中
                    if user_role not in required_roles:
                        return JSONResponse(
                            status_code=403,
                            content=ApiResponse.error(
                                f"权限不足，需要角色: {', '.join(required_roles)}，当前角色: {user_role}",
                                403
                            ).model_dump()
                        )

                    # 将用户信息添加到请求状态中，供后续使用
                    if hasattr(request, 'state'):
                        request.state.user_id = payload.get("user_id")
                        request.state.username = payload.get("username")
                        request.state.role = user_role

                except Exception as e:
                    return JSONResponse(
                        status_code=401,
                        content=ApiResponse.error("无效的认证token", 401).model_dump()
                    )

                return await func(*args, **kwargs)
            return wrapper
        return decorator


class AdminMiddleware:
    """管理员权限中间件"""

    @staticmethod
    def require_admin():
        """要求管理员权限"""
        return RoleMiddleware.require_roles([UserConsts.USER_ROLE_ADMIN])


# 便捷装饰器
def require_roles(required_roles: List[str]):
    """要求指定角色的便捷装饰器"""
    return RoleMiddleware.require_roles(required_roles)


def require_admin():
    """要求管理员权限的便捷装饰器"""
    return AdminMiddleware.require_admin()