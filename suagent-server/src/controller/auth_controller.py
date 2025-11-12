"""
用户认证控制器
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from src.model.database import get_db
from src.request.auth_request import LoginRequest, RegisterRequest, ChangePasswordRequest, LogoutRequest
from src.response.base_response import ApiResponse, success_response, business_error_response
from src.response.auth_response import (
    LoginResponse, RegisterResponse, LogoutResponse,
    ChangePasswordResponse, UserInfo, TokenValidationResponse
)
from src.service.auth_service import auth_service
from src.api_middlewares.jwt_middleware import get_current_user_from_token
import logging

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse[RegisterResponse])
async def register(
    register_request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册

    - **username**: 用户名，3-20个字符，只允许大小写字母、数字和下划线
    - **password**: 密码，至少8位ASCII可见字符
    - **confirm_password**: 确认密码，必须与密码一致
    """
    try:
        result = auth_service.register_user(db, register_request)
        return success_response(result=result, message="注册成功")

    except ValueError as e:
        return business_error_response(str(e))
    except Exception as e:
        logger.error(f"注册接口异常: {e}")
        return ApiResponse.error("注册失败，请稍后重试", 500)


@router.post("/login", response_model=ApiResponse[LoginResponse])
async def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码

    返回JWT访问令牌和用户信息
    """
    try:
        result = auth_service.login_user(db, login_request)
        return success_response(result=result, message="登录成功")

    except ValueError as e:
        return business_error_response(str(e))
    except Exception as e:
        logger.error(f"登录接口异常: {e}")
        return ApiResponse.error("登录失败，请稍后重试", 500)


@router.post("/logout", response_model=ApiResponse[LogoutResponse])
async def logout(
    authorization: Optional[str] = Header(None, description="Authorization Bearer token")
):
    """
    用户退出登录

    需要在Header中提供Authorization: Bearer <token>
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return business_error_response("缺少有效的Authorization header")

        token = authorization.split(" ")[1]
        success = auth_service.logout_user(token)

        if success:
            return success_response(result=LogoutResponse(), message="退出登录成功")
        else:
            return business_error_response("退出登录失败，token可能已过期")

    except Exception as e:
        logger.error(f"退出登录接口异常: {e}")
        return ApiResponse.error("退出登录失败，请稍后重试", 500)


@router.post("/change-password", response_model=ApiResponse[ChangePasswordResponse])
async def change_password(
    change_password_request: ChangePasswordRequest,
    current_user: UserInfo = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    修改密码

    - **old_password**: 旧密码
    - **new_password**: 新密码，至少8位ASCII可见字符
    - **confirm_password**: 确认新密码，必须与新密码一致

    需要登录认证
    """
    try:
        result = auth_service.change_password(
            db=db,
            user_id=current_user.id,
            change_password_request=change_password_request
        )
        return success_response(result=result, message="密码修改成功")

    except ValueError as e:
        return business_error_response(str(e))
    except Exception as e:
        logger.error(f"修改密码接口异常: {e}")
        return ApiResponse.error("密码修改失败，请稍后重试", 500)


@router.get("/me", response_model=ApiResponse[UserInfo])
async def get_current_user(
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    获取当前用户信息

    需要登录认证
    """
    return success_response(result=current_user, message="获取用户信息成功")


@router.post("/validate-token", response_model=ApiResponse[TokenValidationResponse])
async def validate_token(
    authorization: Optional[str] = Header(None, description="Authorization Bearer token"),
    db: Session = Depends(get_db)
):
    """
    验证token是否有效

    需要在Header中提供Authorization: Bearer <token>
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return success_response(
                result=TokenValidationResponse(valid=False),
                message="缺少有效的Authorization header"
            )

        token = authorization.split(" ")[1]
        is_valid = auth_service.validate_token(db, token)

        if is_valid:
            user_info = auth_service.get_current_user_info(db, token)
            # 获取token过期时间
            from src.service.token_service import token_service
            payload = token_service.verify_token(token)
            expires_at = None
            if payload and "exp" in payload:
                from datetime import datetime
                expires_at = datetime.fromtimestamp(payload["exp"])

            return success_response(
                result=TokenValidationResponse(
                    valid=True,
                    user_info=user_info,
                    expires_at=expires_at
                ),
                message="Token有效"
            )
        else:
            return success_response(
                result=TokenValidationResponse(valid=False),
                message="Token无效或已过期"
            )

    except Exception as e:
        logger.error(f"验证token接口异常: {e}")
        return ApiResponse.error("Token验证失败，请稍后重试", 500)


@router.post("/refresh-token", response_model=ApiResponse[dict])
async def refresh_token(
    authorization: Optional[str] = Header(None, description="Authorization Bearer token"),
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌

    需要在Header中提供Authorization: Bearer <token>
    返回新的访问令牌
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return business_error_response("缺少有效的Authorization header")

        token = authorization.split(" ")[1]
        new_token = auth_service.refresh_user_token(db, token)

        if new_token:
            from src.service.token_service import token_service
            result = {
                "access_token": new_token,
                "token_type": "Bearer",
                "expires_in": token_service.get_token_expire_time()
            }
            return success_response(result=result, message="Token刷新成功")
        else:
            return business_error_response("Token刷新失败，原token可能已过期")

    except Exception as e:
        logger.error(f"刷新token接口异常: {e}")
        return ApiResponse.error("Token刷新失败，请稍后重试", 500)


@router.get("/health")
async def auth_health():
    """
    认证服务健康检查
    """
    try:
        from src.service.token_service import token_service
        redis_status = "connected" if token_service.redis_client else "disconnected"

        return success_response(
            result={
                "status": "healthy",
                "redis_status": redis_status,
                "jwt_config": {
                    "algorithm": token_service.settings.jwt_algorithm,
                    "expire_minutes": token_service.settings.jwt_expire_minutes
                }
            },
            message="认证服务运行正常"
        )
    except Exception as e:
        logger.error(f"认证服务健康检查异常: {e}")
        return business_error_response("认证服务异常")