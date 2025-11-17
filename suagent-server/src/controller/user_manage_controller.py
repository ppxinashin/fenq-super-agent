"""
用户管理控制器
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Dict, Any
from src.api_middlewares.role_middleware import require_admin
from src.api_middlewares.jwt_middleware import get_current_user_from_token
from src.service.user_manage_service import user_manage_service
from src.service.memory_setting_service import memory_setting_service
from src.request.user_manage_request import UserUpdateRequest, UserCreateRequest, UserListRequest
from src.request.base_request import BaseIDRequest
from src.request.memory_setting_request import MemorySettingRequest
from src.response.base_response import ApiResponse, success_response, error_response, business_error_response
from src.response.user_manage_response import UserInfo, UserListItem
from src.response.auth_response import UserInfo as AuthUserInfo
from src.response.pageable import Pageable
from src.response.memory_setting_response import MemorySettingResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["用户管理"])


@router.put("/users", response_model=ApiResponse[UserInfo], summary="修改用户信息")
@require_admin()
async def update_user(request: Request, user_update: UserUpdateRequest, current_user: AuthUserInfo = Depends(get_current_user_from_token)):
    """
    管理员修改用户信息

    功能点：
    - 修改用户密码（符合密码规则）
    - 修改用户角色
    - 用户名不可修改
    """
    try:
        logger.info(f"管理员修改用户信息: user_id={user_update.user_id}, role={user_update.role}")

        user_info = user_manage_service.update_user(user_update, current_user.id, current_user.username)

        return success_response(
            result=user_info,
            message="用户信息更新成功"
        )

    except Exception as e:
        logger.error(f"修改用户信息失败: {e}")
        return business_error_response(str(e))


@router.post("/users", response_model=ApiResponse[UserInfo], summary="创建新用户")
@require_admin()
async def create_user(request: Request, user_create: UserCreateRequest, current_user: AuthUserInfo = Depends(get_current_user_from_token)):
    """
    管理员创建新用户

    功能点：
    - 遵循注册规则创建用户
    - 指定用户角色
    """
    try:
        logger.info(f"管理员创建新用户: username={user_create.username}, role={user_create.role}")

        user_info = user_manage_service.create_user(user_create, current_user.id, current_user.username)

        return success_response(
            result=user_info,
            message="用户创建成功"
        )

    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        return business_error_response(str(e))


@router.get("/users/{user_id}", response_model=ApiResponse[UserInfo], summary="获取用户详情")
@require_admin()
async def get_user_by_id(request: Request, user_id: int):
    """
    管理员查看用户详细信息

    功能点：
    - 显示用户名、角色等基本信息
    """
    try:
        logger.info(f"管理员查询用户详情: user_id={user_id}")

        user_info = user_manage_service.get_user_by_id(user_id)

        return success_response(
            result=user_info,
            message="查询成功"
        )

    except Exception as e:
        logger.error(f"查询用户详情失败: {e}")
        return business_error_response(str(e))


@router.get("/users", response_model=ApiResponse[Pageable[UserListItem]], summary="分页查询用户列表")
@require_admin()
async def get_user_list(request: Request, page: int = 1, page_size: int = 20, keyword: str = None):
    """
    管理员分页查询用户列表

    功能点：
    - 分页展示用户
    - 按用户名关键词搜索
    """
    try:
        # 构建查询请求
        list_request = UserListRequest(
            page=page,
            page_size=page_size,
            keyword=keyword
        )

        logger.info(f"管理员查询用户列表: page={page}, page_size={page_size}, keyword={keyword}")

        page_result = user_manage_service.get_user_list(list_request)

        return success_response(
            result=page_result,
            message="查询成功"
        )

    except Exception as e:
        logger.error(f"查询用户列表失败: {e}")
        return business_error_response(str(e))


@router.delete("/users/{user_id}", response_model=ApiResponse[bool], summary="删除用户")
@require_admin()
async def delete_user(request: Request, user_id: int, current_user: AuthUserInfo = Depends(get_current_user_from_token)):
    """
    管理员删除用户

    功能点：
    - 逻辑删除用户账户（设置 is_deleted=true）
    """
    try:
        logger.info(f"管理员删除用户: user_id={user_id}")

        success = user_manage_service.delete_user(user_id, current_user.id, current_user.username)

        return success_response(
            result=success,
            message="用户删除成功"
        )

    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        return business_error_response(str(e))


@router.post("/memory-setting", response_model=ApiResponse[MemorySettingResponse], summary="设置长期记忆开关")
async def set_memory_setting(
    request: Request,
    memory_request: MemorySettingRequest,
    current_user: AuthUserInfo = Depends(get_current_user_from_token)
):
    """
    用户设置长期记忆开关

    功能点：
    - 用户可设置记忆开关状态
    - 状态持久化存储到 user_memory_settings 表
    - 查到了就修改状态，没查到就添加一个记录
    - 开启开关后，异步上传聊天记录到MinIO
    """
    try:
        logger.info(f"用户设置记忆开关: username={current_user.username}, enabled={memory_request.enabled}")

        success = memory_setting_service.set_memory_setting(
            username=current_user.username,
            enabled=memory_request.enabled
        )

        if not success:
            return business_error_response("设置记忆开关失败")

        response = MemorySettingResponse(
            username=current_user.username,
            enabled=memory_request.enabled,
            message=f"记忆开关已{'开启' if memory_request.enabled else '关闭'}"
        )

        return success_response(
            result=response,
            message="记忆开关设置成功"
        )

    except Exception as e:
        logger.error(f"设置记忆开关失败: {e}")
        return business_error_response(str(e))


@router.get("/memory-setting", response_model=ApiResponse[bool], summary="查询长期记忆状态")
async def get_memory_setting(
    request: Request,
    current_user: AuthUserInfo = Depends(get_current_user_from_token)
):
    """
    用户查询长期记忆状态

    功能点：
    - 查询当前用户的长期记忆开关状态
    - 如果没有查到就是关闭状态
    """
    try:
        logger.info(f"用户查询记忆状态: username={current_user.username}")

        memory_enabled = memory_setting_service.get_memory_status(current_user.username)

        return success_response(
            result=memory_enabled,
            message="查询记忆状态成功"
        )

    except Exception as e:
        logger.error(f"查询记忆状态失败: {e}")
        return business_error_response(str(e))


@router.post("/memory-sync", summary="手动同步长期记忆")
async def sync_memory(
    request: Request,
    current_user: AuthUserInfo = Depends(get_current_user_from_token)
):
    """
    用户手动同步长期记忆

    功能点：
    - 判断用户是否开启了长期记忆
    - 如果开启了，异步执行记忆文档上传
    - 如果没开启，返回299状态码提示用户
    """
    try:
        logger.info(f"用户同步记忆: username={current_user.username}")

        # 检查用户是否开启了长期记忆
        if not current_user.memory_enabled:
            return error_response("用户未开启长期记忆功能")

        # 执行记忆同步
        message = memory_setting_service.sync_memory(current_user.username)

        return success_response(
            result=True,
            message=message
        )

    except Exception as e:
        logger.error(f"同步记忆失败: {e}")
        return business_error_response(str(e))