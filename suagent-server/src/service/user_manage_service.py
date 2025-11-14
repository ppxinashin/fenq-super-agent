"""
用户管理服务层
"""

from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.model.crud_user import CRUDUser
from src.model.database import get_db
from src.request.user_manage_request import UserUpdateRequest, UserCreateRequest, UserListRequest
from src.response.user_manage_response import UserInfo, UserListItem
from src.consts.status_code import StatusCode
from src.consts.user_consts import UserConsts
from src.utils.logger import get_logger
from src.utils.snowflake_id import Snowflake
from src.utils.jwt_util import JWTUtil
from src.model.user import User
from src.response.pageable import Pageable
from src.response.base_response import business_error_response

logger = get_logger(__name__)


class UserManageService:
    """用户管理服务类"""

    def __init__(self):
        self.user_crud = CRUDUser(User)
        self.snowflake = Snowflake(worker_id=1, datacenter_id=1)

    def update_user(self, user_update: UserUpdateRequest, user_id: int, username: str) -> UserInfo:
        """
        修改用户信息

        Args:
            user_update: 用户信息修改请求

        Returns:
            UserInfo: 更新后的用户信息

        Raises:
            Exception: 更新失败时抛出异常
        """
        db = next(get_db())
        try:
            # 检查用户是否存在
            existing_user = self.user_crud.get_by_id(db, user_update.user_id)
            if not existing_user:
                raise Exception("用户不存在")

            # 检查用户是否已删除
            if existing_user.is_deleted:
                raise Exception("用户已删除，无法修改")

            # 准备更新数据
            update_data = {
                "role": user_update.role
            }

            # 如果提供了新密码，则更新密码
            if user_update.password:
                salt = User.generate_salt()
                password_hash = User.hash_password(user_update.password, salt)
                update_data["password"] = password_hash
                update_data["salt"] = salt

            # 更新用户信息
            updated_user = self.user_crud.update_user_info(db, user_update.user_id, update_data, updated_by=username)
            if not updated_user:
                raise Exception("用户信息更新失败")

            logger.info(f"用户信息更新成功: user_id={user_update.user_id}")

            return self._convert_to_user_info(updated_user)

        except IntegrityError as e:
            logger.error(f"用户信息更新失败 - 数据库错误: {e}")
            raise Exception("用户信息更新失败")
        except Exception as e:
            logger.error(f"用户信息更新失败: {e}")
            raise

        finally:
            db.close()

    def create_user(self, user_create: UserCreateRequest, user_id: int, username: str) -> UserInfo:
        """
        创建新用户

        Args:
            user_create: 用户创建请求

        Returns:
            UserInfo: 创建的用户信息

        Raises:
            Exception: 创建失败时抛出异常
        """
        db = next(get_db())
        try:
            # 检查用户名是否已存在
            existing_user = self.user_crud.get_by_username(db, user_create.username)
            if existing_user:
                raise Exception("用户名已存在")

            # 创建用户数据（基类CRUD会自动生成id）
            user_data = {
                "username": user_create.username,
                "password": user_create.password,  # 让CRUDUser.create_user处理密码
                "role": user_create.role
            }

            # 创建用户
            created_user = self.user_crud.create_user(
                db=db,
                username=user_data["username"],
                plain_password=user_data["password"],
                role=user_data["role"],
                created_by=username
            )
            if not created_user:
                raise Exception("用户创建失败")

            logger.info(f"用户创建成功: user_id={created_user.id}, username={user_create.username}")

            return self._convert_to_user_info(created_user)

        except IntegrityError as e:
            logger.error(f"用户创建失败 - 数据库错误: {e}")
            raise Exception("用户创建失败")
        except Exception as e:
            logger.error(f"用户创建失败: {e}")
            raise

        finally:
            db.close()

    def get_user_by_id(self, user_id: int) -> UserInfo:
        """
        根据用户ID获取用户详情

        Args:
            user_id: 用户ID

        Returns:
            UserInfo: 用户详情

        Raises:
            Exception: 查询失败时抛出异常
        """
        db = next(get_db())
        try:
            user = self.user_crud.get_by_id(db, user_id)
            if not user:
                raise Exception("用户不存在")

            return self._convert_to_user_info(user)

        except Exception as e:
            logger.error(f"获取用户详情失败: {e}")
            raise

        finally:
            db.close()

    def get_user_list(self, request: UserListRequest) -> Pageable[UserListItem]:
        """
        分页查询用户列表

        Args:
            request: 用户列表查询请求

        Returns:
            Pageable[UserListItem]: 分页用户列表

        Raises:
            Exception: 查询失败时抛出异常
        """
        db = next(get_db())
        try:
            # 查询用户列表
            users, total = self.user_crud.get_user_list(
                db=db,
                page=request.page,
                page_size=request.page_size,
                keyword=request.keyword
            )

            # 转换为响应格式
            user_items = [self._convert_to_user_list_item(user) for user in users]

            # 构建分页结果
            page_result = Pageable(
                page=request.page,
                page_size=request.page_size,
                total=total,
                data=user_items
            )

            logger.info(f"查询用户列表成功: page={request.page}, count={len(user_items)}, total={total}")

            return page_result

        except Exception as e:
            logger.error(f"查询用户列表失败: {e}")
            raise

        finally:
            db.close()

    def delete_user(self, user_id: int, current_user_id: int, current_username: str) -> bool:
        """
        逻辑删除用户

        Args:
            user_id: 用户ID

        Returns:
            bool: 删除是否成功

        Raises:
            Exception: 删除失败时抛出异常
        """
        db = next(get_db())
        try:
            # 检查用户是否存在
            user = self.user_crud.get_by_id(db, user_id)
            if not user:
                raise Exception("用户不存在")

            # 检查用户是否已删除
            if user.is_deleted:
                raise Exception("用户已删除")

            # 逻辑删除用户
            success = self.user_crud.soft_delete(db, user_id, deleted_by=current_username)
            if not success:
                raise Exception("用户删除失败")

            logger.info(f"用户删除成功: user_id={user_id}")

            return True

        except Exception as e:
            logger.error(f"用户删除失败: {e}")
            raise

        finally:
            db.close()

    def _convert_to_user_info(self, user: User) -> UserInfo:
        """将User模型转换为UserInfo响应模型"""
        return UserInfo(
            user_id=user.id,
            username=user.username,
            role=user.role,
            is_deleted=user.is_deleted,
            created_at=user.created_at,
            created_by=user.created_by,
            updated_at=user.updated_at,
            updated_by=user.updated_by
        )

    def _convert_to_user_list_item(self, user: User) -> UserListItem:
        """将User模型转换为UserListItem响应模型"""
        return UserListItem(
            user_id=user.id,
            username=user.username,
            role=user.role,
            is_deleted=user.is_deleted,
            created_at=user.created_at,
            created_by=user.created_by
        )


# 创建服务实例
user_manage_service = UserManageService()