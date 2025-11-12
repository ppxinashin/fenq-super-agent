"""
智能体管理控制器

提供智能体的增删改查功能，并区分普通用户与管理员权限
"""

import json
from typing import Dict, Any, Tuple
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.model.database import get_db
from src.model.agent import Agent
from src.model.crud_agent import crud_agent
from src.model.user import User, UserRole
from src.api.request.base_request import BasePageKeywordRequest
from src.api.request.agent_manage_request import (
    AgentManageCreateRequest,
    AgentManageUpdateRequest
)
from src.api.response.agent_response import (
    AgentResponse,
    AgentPublicResponse
)
from src.api.response.pageable import PageableResponse
from src.api.interceptor.auth_interceptor import (
    get_current_user,
    verify_admin_interceptor
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/agent/manage", tags=["智能体管理"])

GLOBAL_SCOPE_CREATED_BY = "system"


def _parse_mcp_servers(raw_value: Any) -> Dict[str, Any]:
    """将前端传来的字符串/字典统一转换为JSON对象"""
    if raw_value is None:
        return {}
    if isinstance(raw_value, dict):
        return raw_value
    if isinstance(raw_value, str):
        raw_value = raw_value.strip()
        if not raw_value:
            return {}
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            logger.warning(f"MCP服务器配置解析失败: {raw_value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MCP服务器配置格式错误: {exc.msg}"
            ) from exc
        if not isinstance(parsed, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MCP服务器配置必须是JSON对象"
            )
        return parsed
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="MCP服务器配置仅支持字符串或JSON对象"
    )


def _apply_keyword_filter(query, keyword: str):
    """根据关键词过滤智能体"""
    if keyword:
        like_pattern = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                Agent.agent_name.ilike(like_pattern),
                Agent.description.ilike(like_pattern)
            )
        )
    return query


def _paginate_agents(query, page: int, page_size: int) -> Tuple[list, int, int, int]:
    """对智能体查询结果进行分页"""
    total = query.count()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    max_page = total_pages if total_pages > 0 else 1
    page = max(1, min(page, max_page))
    offset = (page - 1) * page_size
    items = query.order_by(Agent.id.desc()).offset(offset).limit(page_size).all()
    return items, total, page, total_pages


def _build_pageable_response(items, total, page, page_size, total_pages, model_cls):
    """构建分页响应"""
    return PageableResponse[model_cls](  # type: ignore
        items=[model_cls.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_prev=page > 1 and total > 0,
        has_next=page < (total_pages or 1) and total > 0
    )


def _get_agent_by_identifier(db: Session, identifier: str) -> Agent:
    """支持ID或agent_id查询智能体"""
    identifier = identifier.strip()
    agent = None
    if identifier.isdigit():
        agent = crud_agent.get(db=db, id=int(identifier))
        if agent:
            return agent
    agent = crud_agent.get_by_agent_id(db=db, agent_id=identifier)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="智能体不存在"
        )
    return agent


def _check_agent_permission(agent: Agent, current_user: User):
    """校验普通用户是否拥有智能体操作权限"""
    if current_user.role == UserRole.ADMIN:
        return
    if str(agent.created_by) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作该智能体"
        )


def _resolve_created_by(scope: str, current_user: User) -> str:
    """根据作用域确定创建者字段"""
    if scope == "global" and current_user.role == UserRole.ADMIN:
        return GLOBAL_SCOPE_CREATED_BY
    return str(current_user.id)


@router.get(
    "/mine",
    response_model=PageableResponse[AgentResponse],
    summary="查询当前用户的智能体（需登录）"
)
async def list_my_agents(
    request: BasePageKeywordRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """普通用户查询自己创建的智能体，支持关键词搜索"""
    query = db.query(Agent).filter(
        Agent.is_deleted == False,
        Agent.created_by == str(current_user.id)
    )
    query = _apply_keyword_filter(query, request.keyword)
    agents, total, page, total_pages = _paginate_agents(
        query, request.page, request.page_size
    )
    logger.info(
        f"用户 {current_user.username} 查询个人智能体: "
        f"page={page}, page_size={request.page_size}, total={total}"
    )
    return _build_pageable_response(
        agents, total, page, request.page_size, total_pages, AgentResponse
    )


@router.get(
    "/public",
    response_model=PageableResponse[AgentPublicResponse],
    summary="查询所有智能体（公开，仅名称与介绍）"
)
async def list_public_agents(
    request: BasePageKeywordRequest = Depends(),
    db: Session = Depends(get_db)
):
    """公开接口，返回所有智能体的名称与介绍，可用于全局展示"""
    query = db.query(Agent).filter(Agent.is_deleted == False)
    query = _apply_keyword_filter(query, request.keyword)
    agents, total, page, total_pages = _paginate_agents(
        query, request.page, request.page_size
    )
    logger.info(
        f"公开查询智能体: page={page}, page_size={request.page_size}, total={total}"
    )
    return _build_pageable_response(
        agents, total, page, request.page_size, total_pages, AgentPublicResponse
    )


@router.get(
    "/all",
    response_model=PageableResponse[AgentResponse],
    summary="管理员查询所有智能体"
)
async def list_all_agents(
    request: BasePageKeywordRequest = Depends(),
    admin: User = Depends(verify_admin_interceptor),
    db: Session = Depends(get_db)
):
    """管理员可查看全部智能体并支持关键词搜索"""
    query = db.query(Agent).filter(Agent.is_deleted == False)
    query = _apply_keyword_filter(query, request.keyword)
    agents, total, page, total_pages = _paginate_agents(
        query, request.page, request.page_size
    )
    logger.info(
        f"管理员 {admin.username} 查询全部智能体: "
        f"page={page}, page_size={request.page_size}, total={total}"
    )
    return _build_pageable_response(
        agents, total, page, request.page_size, total_pages, AgentResponse
    )


@router.get(
    "/{agent_identifier}",
    response_model=AgentResponse,
    summary="根据ID查询智能体详情（需验证权限）"
)
async def get_agent_detail(
    agent_identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据智能体ID或agent_id查询详情
    
    - 普通用户仅能查看自己创建的智能体
    - 管理员可查看所有智能体
    """
    agent = _get_agent_by_identifier(db, agent_identifier)
    _check_agent_permission(agent, current_user)
    logger.info(
        f"用户 {current_user.username} 查询智能体详情: "
        f"identifier={agent_identifier}, agent_db_id={agent.id}"
    )
    return AgentResponse.model_validate(agent)


@router.post(
    "/",
    response_model=AgentResponse,
    summary="新增智能体（所有登录用户）"
)
async def create_agent(
    request: AgentManageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建智能体，管理员可根据scope选择全局/个人"""
    existing_agent = crud_agent.get_by_agent_id(db=db, agent_id=request.agent_id)
    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="智能体英文名已存在"
        )
    
    if request.scope == "global" and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可以创建全局智能体"
        )
    
    mcp_servers = _parse_mcp_servers(request.mcp_servers)
    created_by = _resolve_created_by(request.scope, current_user)
    
    agent = crud_agent.create_agent(
        db=db,
        agent_id=request.agent_id.strip(),
        agent_name=request.agent_name.strip(),
        system_prompt=request.system_prompt,
        description=request.description,
        tools=request.tools,
        mcp_enabled=request.mcp_enabled,
        mcp_servers=mcp_servers,
        created_by=created_by
    )
    
    logger.info(
        f"用户 {current_user.username} 创建智能体: {agent.agent_id}, scope={request.scope}"
    )
    return AgentResponse.model_validate(agent)


@router.put(
    "/{agent_identifier}",
    response_model=AgentResponse,
    summary="编辑智能体"
)
async def update_agent(
    agent_identifier: str,
    request: AgentManageUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """仅创建者或管理员可编辑智能体"""
    agent = _get_agent_by_identifier(db, agent_identifier)
    _check_agent_permission(agent, current_user)
    
    update_data: Dict[str, Any] = {}
    
    if request.agent_id and request.agent_id != agent.agent_id:
        if crud_agent.get_by_agent_id(db=db, agent_id=request.agent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新的智能体英文名已存在"
            )
        update_data["agent_id"] = request.agent_id.strip()
    
    if request.agent_name is not None:
        update_data["agent_name"] = request.agent_name.strip()
    if request.description is not None:
        update_data["description"] = request.description
    if request.system_prompt is not None:
        update_data["system_prompt"] = request.system_prompt
    if request.tools is not None:
        update_data["tools"] = request.tools
    if request.mcp_enabled is not None:
        update_data["mcp_enabled"] = request.mcp_enabled
    if request.mcp_servers is not None:
        update_data["mcp_servers"] = _parse_mcp_servers(request.mcp_servers)
    
    if request.scope:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="仅管理员可调整智能体作用域"
            )
        update_data["created_by"] = _resolve_created_by(request.scope, current_user)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未提供任何可更新字段"
        )
    
    updated_agent = crud_agent.update(
        db=db,
        db_obj=agent,
        obj_in=update_data,
        updated_by=str(current_user.id)
    )
    
    logger.info(
        f"用户 {current_user.username} 更新智能体: {updated_agent.agent_id}"
    )
    return AgentResponse.model_validate(updated_agent)


@router.delete(
    "/{agent_identifier}",
    summary="删除智能体"
)
async def delete_agent(
    agent_identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """仅创建者或管理员可删除智能体"""
    agent = _get_agent_by_identifier(db, agent_identifier)
    _check_agent_permission(agent, current_user)
    
    success = crud_agent.delete(
        db=db,
        id=agent.id,
        deleted_by=str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="智能体删除失败，请稍后重试"
        )
    
    logger.info(
        f"用户 {current_user.username} 删除智能体: {agent.agent_id}"
    )
    return {"message": "智能体删除成功"}
