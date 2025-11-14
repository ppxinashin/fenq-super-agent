"""
智能体管理控制器
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Dict, Any
from src.api_middlewares.role_middleware import require_roles, require_admin
from src.api_middlewares.jwt_middleware import get_current_user_from_token
from src.service.agent_manage_service import agent_manage_service
from src.request.agent_manage_request import (
    AgentCreateRequest, AgentUpdateRequest, AgentListRequest,
    AgentCardListRequest, AgentToolsUpdateRequest, AgentMcpUpdateRequest
)
from src.response.base_response import ApiResponse, success_response, error_response, business_error_response
from src.response.agent_manage_response import (
    AgentInfo, AgentSimpleInfo, AgentListItem,
    AgentCreateResponse, AgentUpdateResponse, AgentDeleteResponse
)
from src.response.auth_response import UserInfo
from src.response.pageable import Pageable
from src.consts.user_consts import UserConsts
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["智能体管理"])


@router.get("/agents/cards", response_model=ApiResponse[Pageable[AgentSimpleInfo]], summary="智能体卡片展示")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def get_agent_card_list(request: Request, page: int = 1, page_size: int = 20, keyword: str = None):
    """
    展示智能体列表卡片

    功能点：
    - 分页展示
    - 按创建时间倒序排列
    - 支持按名称、介绍关键词搜索

    权限控制：
    - 已登录用户可查看
    - 未登录用户无法查看
    """
    try:
        # 构建查询请求
        list_request = AgentCardListRequest(
            page=page,
            page_size=page_size,
            keyword=keyword
        )

        logger.info(f"查询智能体卡片列表: page={page}, page_size={page_size}, keyword={keyword}")

        page_result = agent_manage_service.get_agent_card_list(list_request)

        return success_response(
            result=page_result,
            message="查询成功"
        )

    except Exception as e:
        logger.error(f"查询智能体卡片列表失败: {e}")
        return business_error_response(str(e))


@router.get("/agents/{agent_id}", response_model=ApiResponse[AgentInfo], summary="智能体详情")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def get_agent_by_id(request: Request, agent_id: str):
    """
    查看智能体详细信息

    功能点：
    - 显示中文名、英文名、可用工具
    - 显示系统提示词、MCP状态和服务器配置
    - 显示创建人、创建时间、修改人、修改时间

    权限控制：
    - 管理员可查看所有智能体详情
    - 普通用户查看基本信息
    """
    try:
        logger.info(f"查询智能体详情: agent_id={agent_id}")

        agent_info = agent_manage_service.get_agent_by_id(agent_id)

        # TODO: 根据用户角色过滤返回的信息

        return success_response(
            result=agent_info,
            message="查询成功"
        )

    except Exception as e:
        logger.error(f"查询智能体详情失败: {e}")
        return business_error_response(str(e))


@router.get("/agents", response_model=ApiResponse[Pageable[AgentListItem]], summary="智能体列表管理")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def get_agent_management_list(request: Request, page: int = 1, page_size: int = 20, keyword: str = None, current_user: UserInfo = Depends(get_current_user_from_token)):
    """
    管理智能体列表

    功能点：
    - 分页展示
    - 按创建时间倒序排列

    权限控制：
    - 管理员查看所有智能体
    - 普通用户只查看自己创建的智能体
    """
    try:
        # 根据用户角色确定查询范围
        is_admin = current_user.role == UserConsts.USER_ROLE_ADMIN

        logger.info(f"查询智能体管理列表: page={page}, page_size={page_size}, keyword={keyword}, user_role={current_user.role}")

        page_result = agent_manage_service.get_agent_management_list(
            page=page,
            page_size=page_size,
            keyword=keyword,
            current_user_id=current_user.id if not is_admin else None,
            current_username=current_user.username
        )

        return success_response(
            result=page_result,
            message="查询成功"
        )

    except Exception as e:
        logger.error(f"查询智能体管理列表失败: {e}")
        return business_error_response(str(e))


@router.post("/agents", response_model=ApiResponse[AgentCreateResponse], summary="创建智能体")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def create_agent(request: Request, agent_create: AgentCreateRequest, current_user: UserInfo = Depends(get_current_user_from_token)):
    """
    创建新的智能体

    功能点：
    - 设置英文名（agent_id）：唯一标识，只允许大小写字母、数字和下划线
    - 设置中文名（agent_name）
    - 配置系统提示词
    - 配置可用工具和 MCP 状态
    - 配置 MCP 服务器信息
    """
    try:
        logger.info(f"创建新智能体: agent_id={agent_create.agent_id}, agent_name={agent_create.agent_name}")

        agent_response = agent_manage_service.create_agent(agent_create, current_user.id, current_user.username)

        return success_response(
            result=agent_response,
            message="智能体创建成功"
        )

    except Exception as e:
        logger.error(f"创建智能体失败: {e}")
        return business_error_response(str(e))


@router.put("/agents", response_model=ApiResponse[AgentUpdateResponse], summary="修改智能体")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def update_agent(request: Request, agent_update: AgentUpdateRequest, current_user: UserInfo = Depends(get_current_user_from_token)):
    """
    修改智能体信息

    功能点：
    - 修改基本信息和配置
    - 单独更新工具列表
    - 单独更新 MCP 配置

    权限控制：
    - 管理员可修改所有智能体
    - 普通用户只能修改自己的智能体
    """
    try:
        logger.info(f"修改智能体信息: agent_id={agent_update.agent_id}")

        # TODO: 检查用户权限
        agent_response = agent_manage_service.update_agent(agent_update, current_user.id, current_user.username)

        return success_response(
            result=agent_response,
            message="智能体信息更新成功"
        )

    except Exception as e:
        logger.error(f"修改智能体信息失败: {e}")
        return business_error_response(str(e))


@router.put("/agents/tools", response_model=ApiResponse[AgentUpdateResponse], summary="更新智能体工具")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def update_agent_tools(request: Request, tools_update: AgentToolsUpdateRequest, current_user: UserInfo = Depends(get_current_user_from_token)):
    """
    单独更新智能体工具列表

    功能点：
    - 单独更新工具列表

    权限控制：
    - 管理员可修改所有智能体
    - 普通用户只能修改自己的智能体
    """
    try:
        logger.info(f"更新智能体工具: agent_id={tools_update.agent_id}, tools={tools_update.tools}")

        # TODO: 检查用户权限
        agent_response = agent_manage_service.update_agent_tools(tools_update, current_user.id, current_user.username)

        return success_response(
            result=agent_response,
            message="智能体工具更新成功"
        )

    except Exception as e:
        logger.error(f"更新智能体工具失败: {e}")
        return business_error_response(str(e))


@router.put("/agents/mcp", response_model=ApiResponse[AgentUpdateResponse], summary="更新智能体MCP配置")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def update_agent_mcp(request: Request, mcp_update: AgentMcpUpdateRequest, current_user: UserInfo = Depends(get_current_user_from_token)):
    """
    单独更新智能体MCP配置

    功能点：
    - 单独更新 MCP 配置

    权限控制：
    - 管理员可修改所有智能体
    - 普通用户只能修改自己的智能体
    """
    try:
        logger.info(f"更新智能体MCP配置: agent_id={mcp_update.agent_id}, mcp_status={mcp_update.mcp_status}")

        # TODO: 检查用户权限
        agent_response = agent_manage_service.update_agent_mcp(mcp_update, current_user.id, current_user.username)

        return success_response(
            result=agent_response,
            message="智能体MCP配置更新成功"
        )

    except Exception as e:
        logger.error(f"更新智能体MCP配置失败: {e}")
        return business_error_response(str(e))


@router.delete("/agents/{agent_id}", response_model=ApiResponse[AgentDeleteResponse], summary="删除智能体")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def delete_agent(request: Request, agent_id: str, current_user: UserInfo = Depends(get_current_user_from_token)):
    """
    删除智能体

    功能点：
    - 逻辑删除（设置 is_deleted=true）

    权限控制：
    - 管理员可删除所有智能体
    - 普通用户只能删除自己的智能体
    """
    try:
        logger.info(f"删除智能体: agent_id={agent_id}, user_role={current_user.role}, username={current_user.username}")

        # 服务层会根据用户角色和智能体创建者进行权限检查
        agent_response = agent_manage_service.delete_agent(agent_id, current_user.id, current_user.username)

        return success_response(
            result=agent_response,
            message="智能体删除成功"
        )

    except Exception as e:
        logger.error(f"删除智能体失败: {e}")
        return business_error_response(str(e))