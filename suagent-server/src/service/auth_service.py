"""
用户认证服务
"""

from typing import Optional
from sqlalchemy.orm import Session
from src.model.crud_user import crud_user
from src.model.crud_user_memory_setting import crud_user_memory_setting
from src.model.user import UserRole
from src.request.auth_request import RegisterRequest, LoginRequest, ChangePasswordRequest
from src.response.auth_response import LoginResponse, RegisterResponse, UserInfo, ChangePasswordResponse
from src.service.token_service import token_service
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """用户认证服务"""

    @staticmethod
    def register_user(db: Session, register_request: RegisterRequest) -> RegisterResponse:
        """
        用户注册

        Args:
            db: 数据库会话
            register_request: 注册请求

        Returns:
            注册响应

        Raises:
            ValueError: 用户名已存在或其他业务错误
        """
        try:
            # 检查用户名是否已存在
            existing_user = crud_user.get_by_username(db, register_request.username)
            if existing_user:
                raise ValueError(f"用户名 '{register_request.username}' 已被注册，请选择其他用户名")

            # 创建新用户
            user = crud_user.create_user(
                db=db,
                username=register_request.username,
                plain_password=register_request.password,
                role=UserRole.USER,
                created_by="register_api"
            )

            logger.info(f"用户注册成功: {user.username}")

            # 处理 role 可能是字符串或枚举对象的情况
            role_value = user.role.value if hasattr(user.role, 'value') else user.role
            return RegisterResponse(
                user_id=user.id,
                username=user.username,
                role=role_value,
                message="注册成功"
            )

        except ValueError as e:
            logger.warning(f"用户注册失败 - {register_request.username}: {e}")
            raise
        except Exception as e:
            logger.error(f"用户注册异常 - {register_request.username}: {e}")
            # 根据不同类型的错误提供不同的提示
            error_msg = str(e).lower()
            if "invalid input value for enum" in error_msg:
                raise ValueError("系统配置错误，请联系管理员")
            elif "duplicate key" in error_msg or "unique constraint" in error_msg:
                raise ValueError(f"用户名 '{register_request.username}' 已被注册，请选择其他用户名")
            elif "too many connections" in error_msg:
                raise ValueError("服务器繁忙，请稍后重试")
            else:
                raise ValueError("注册失败，请检查输入信息或稍后重试")

    @staticmethod
    def login_user(db: Session, login_request: LoginRequest) -> LoginResponse:
        """
        用户登录

        Args:
            db: 数据库会话
            login_request: 登录请求

        Returns:
            登录响应

        Raises:
            ValueError: 用户名或密码错误
        """
        try:
            # 用户认证
            user = crud_user.authenticate(
                db=db,
                username=login_request.username,
                plain_password=login_request.password
            )

            if not user:
                logger.warning(f"登录失败 - 用户名或密码错误: {login_request.username}")
                raise ValueError("用户名或密码错误")

            # 创建用户信息
            # 处理 role 可能是字符串或枚举对象的情况
            role_value = user.role.value if hasattr(user.role, 'value') else user.role
            user_info = {
                "id": user.id,
                "username": user.username,
                "role": role_value
            }

            # 生成访问令牌
            access_token = token_service.create_access_token(user_info)

            # 构建用户信息响应
            # 处理 role 可能是字符串或枚举对象的情况
            role_value = user.role.value if hasattr(user.role, 'value') else user.role
            user_info_response = UserInfo(
                id=user.id,
                username=user.username,
                role=role_value,
                created_at=user.created_at,
                updated_at=user.updated_at
            )

            logger.info(f"用户登录成功: {user.username}")

            return LoginResponse(
                access_token=access_token,
                token_type="Bearer",
                expires_in=token_service.get_token_expire_time(),
                user_info=user_info_response
            )

        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"用户登录异常 - {login_request.username}: {e}")
            raise ValueError("登录失败，请稍后重试")

    @staticmethod
    def logout_user(token: str) -> bool:
        """
        用户退出登录

        Args:
            token: 访问令牌

        Returns:
            是否成功退出
        """
        try:
            # 验证token
            payload = token_service.verify_token(token)
            if not payload:
                logger.warning("退出登录失败 - token无效")
                return False

            # 从Redis中删除token
            revoke_status = token_service.revoke_token(token)

            if revoke_status == 1:
                logger.info(f"用户退出登录成功: {payload.get('username', 'unknown')}")
                return True
            elif revoke_status == 0:
                logger.info(f"用户退出登录成功 - token已过期: {payload.get('username', 'unknown')}")
                return True
            else:  # revoke_status == -1
                logger.error(f"用户退出登录失败 - Redis连接异常: {payload.get('username', 'unknown')}")
                return False

        except Exception as e:
            logger.error(f"用户退出登录异常: {e}")
            return False

    @staticmethod
    def change_password(
        db: Session,
        user_id: int,
        change_password_request: ChangePasswordRequest
    ) -> ChangePasswordResponse:
        """
        修改密码

        Args:
            db: 数据库会话
            user_id: 用户ID
            change_password_request: 修改密码请求

        Returns:
            修改密码响应

        Raises:
            ValueError: 旧密码错误或其他业务错误
        """
        try:
            # 获取用户
            user = crud_user.get(db, user_id)
            if not user:
                raise ValueError("用户不存在")

            # 验证旧密码
            if not user.verify_password(change_password_request.old_password):
                logger.warning(f"修改密码失败 - 旧密码错误: {user.username}")
                raise ValueError("旧密码错误")

            # 更新密码
            updated_user = crud_user.update_password(
                db=db,
                user_id=user_id,
                new_password=change_password_request.new_password,
                updated_by="user_self"
            )

            if not updated_user:
                raise ValueError("密码更新失败")

            logger.info(f"用户修改密码成功: {user.username}")

            return ChangePasswordResponse(message="密码修改成功")

        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"用户修改密码异常 - user_id={user_id}: {e}")
            raise ValueError("密码修改失败，请稍后重试")

    @staticmethod
    def get_current_user_info(db: Session, token: str) -> Optional[UserInfo]:
        """
        根据token获取当前用户信息

        Args:
            db: 数据库会话
            token: 访问令牌

        Returns:
            用户信息，失败返回None
        """
        try:
            # 验证token
            payload = token_service.verify_token(token)
            if not payload:
                return None

            # 从数据库获取用户信息
            user_id = int(payload["sub"])
            user = crud_user.get(db, user_id)
            if not user:
                return None

            # 获取用户记忆开关状态
            memory_enabled = crud_user_memory_setting.is_enabled(db=db, username=user.username)

            # 构建用户信息响应
            # 处理 role 可能是字符串或枚举对象的情况
            role_value = user.role.value if hasattr(user.role, 'value') else user.role
            return UserInfo(
                id=user.id,
                username=user.username,
                role=role_value,
                created_at=user.created_at,
                updated_at=user.updated_at,
                memory_enabled=memory_enabled
            )

        except Exception as e:
            logger.error(f"获取当前用户信息异常: {e}")
            return None

    @staticmethod
    def validate_token(db: Session, token: str) -> bool:
        """
        验证token是否有效

        Args:
            db: 数据库会话
            token: 访问令牌

        Returns:
            是否有效
        """
        try:
            # JWT验证
            payload = token_service.verify_token(token)
            if not payload:
                return False

            # Redis验证
            if not token_service.get_user_info_from_redis(token):
                return False

            # 数据库验证（确保用户仍然存在且未被删除）
            user_id = int(payload["sub"])
            user = crud_user.get(db, user_id)
            if not user:
                return False

            return True

        except Exception as e:
            logger.error(f"token验证异常: {e}")
            return False

    @staticmethod
    def refresh_user_token(db: Session, token: str) -> Optional[str]:
        """
        刷新用户token

        Args:
            db: 数据库会话
            token: 原token

        Returns:
            新token，失败返回None
        """
        try:
            # 验证原token
            if not AuthService.validate_token(db, token):
                return None

            # 刷新token
            new_token = token_service.refresh_token(token)
            if new_token:
                logger.info(f"Token刷新成功")
            else:
                logger.warning(f"Token刷新失败")

            return new_token

        except Exception as e:
            logger.error(f"Token刷新异常: {e}")
            return None


# 全局认证服务实例
auth_service = AuthService()