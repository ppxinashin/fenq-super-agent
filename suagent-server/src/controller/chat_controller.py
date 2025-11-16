"""
聊天管理控制器
"""

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from typing import Optional
from fastapi.responses import StreamingResponse
from src.api_middlewares.role_middleware import require_roles
from src.api_middlewares.jwt_middleware import get_current_user_from_token
from src.service.chat_service import chat_service
from src.request.chat_request import CreateSessionRequest, UpdateSessionTitleRequest
from src.response.base_response import ApiResponse, success_response, error_response, business_error_response
from src.response.chat_response import (
    ChatTitleResponse,
    CreateSessionResponse,
    SessionInfoResponse,
    ChatHistoryResponse
)
from src.response.auth_response import UserInfo
from src.response.pageable import Pageable
from src.consts.user_consts import UserConsts
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["聊天管理"])


@router.get("/chat", summary="智能体对话")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def chat(
    request: Request,
    agent_id: str = Query(..., description="智能体ID"),
    session_id: int = Query(..., description="会话ID"),
    message: str = Query(..., description="用户消息"),
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    智能体对话（核心接口）

    功能点：
    - 传入用户信息、智能体 ID、会话 ID
    - 加载智能体工具和系统提示词
    - 流式输出对话结果

    技术要求：
    - 若MCP开启时异步实现，以及异步输出结果至前端
    - 加载系统日志和会话记录中间件
    - 必须流式输出
    """
    try:
        logger.info(f"用户开始聊天: user_id={current_user.username}, agent_id={agent_id}, session_id={session_id}")

        return StreamingResponse(
            chat_service.chat(session_id, agent_id, message=message, user_id=current_user.username),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.error(f"聊天失败: {e}")
        return business_error_response(f"聊天失败: {str(e)}")


@router.post("/sessions", response_model=ApiResponse[CreateSessionResponse], summary="创建会话")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def create_session(
    request: Request,
    session_request: CreateSessionRequest,
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    创建会话

    功能点：
    - 绑定智能体 ID
    - 生成会话 ID（业务 ID，全局唯一）
    - 初始标题为空
    """
    try:
        logger.info(f"用户创建会话: user_id={current_user.username}, agent_id={session_request.agent_id}")

        result = chat_service.create_session(session_request.agent_id, current_user.username)

        return success_response(result=result, message="会话创建成功")
    except Exception as e:
        logger.error(f"创建会话失败: {e}")
        return business_error_response(f"创建会话失败: {str(e)}")


@router.post("/sessions/{session_id}/generate-title", response_model=ApiResponse[ChatTitleResponse], summary="生成会话标题")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def generate_session_title(
    request: Request,
    session_id: int,
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    生成会话标题

    功能点：
    - 分析第一轮对话内容
    - 生成标题（最大20字）
    - 更新会话标题
    """
    try:
        logger.info(f"用户生成会话标题: user_id={current_user.username}, session_id={session_id}")

        return StreamingResponse(
            chat_service.generate_title(session_id, user_id=current_user.username),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.error(f"生成标题失败: {e}")
        return business_error_response(f"生成标题失败: {str(e)}")


@router.put("/sessions/{session_id}/title", response_model=ApiResponse[None], summary="更新会话标题")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def update_session_title(
    request: Request,
    session_id: int,
    title_request: UpdateSessionTitleRequest,
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    更新会话标题

    功能点：
    - 用户自定义会话标题
    """
    try:
        logger.info(f"用户更新会话标题: user_id={current_user.username}, session_id={session_id}")

        success = chat_service.update_session_title(session_id, title_request.title, current_user.username)
        if success:
            return success_response(message="标题更新成功")
        else:
            return error_response(message="标题更新失败")
    except Exception as e:
        logger.error(f"更新标题失败: {e}")
        return business_error_response(f"更新标题失败: {str(e)}")


@router.delete("/sessions/{session_id}", response_model=ApiResponse[None], summary="删除会话")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def delete_session(
    request: Request,
    session_id: int,
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    删除会话

    功能点：
    - 逻辑删除会话记录（设置 is_deleted=true）
    - 保留对话历史
    """
    try:
        logger.info(f"用户删除会话: user_id={current_user.username}, session_id={session_id}")

        success = chat_service.delete_session(session_id, current_user.username)
        if success:
            return success_response(message="会话删除成功")
        else:
            return error_response(message="会话删除失败")
    except Exception as e:
        logger.error(f"删除会话失败: {e}")
        return business_error_response(f"删除会话失败: {str(e)}")


@router.get("/sessions", response_model=ApiResponse[Pageable[SessionInfoResponse]], summary="会话列表")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def get_sessions(
    request: Request,
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=20),
    agent_id: Optional[str] = Query(None, description="智能体ID（可选）"),
    keyword: Optional[str] = Query(None, description="搜索关键词（可选）"),
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    会话列表

    功能点：
    - 分页查询，每页固定20条记录
    - 按创建时间倒序排列
    - 支持按智能体ID筛选
    - 返回会话基本信息：会话ID、智能体ID、智能体名称、标题、创建时间、最后消息时间、消息数量

    权限控制：
    - 用户只能查看自己创建的会话
    """
    try:
        logger.info(f"用户查询会话列表: user_id={current_user.username}, page={page}, agent_id={agent_id}")

        result = chat_service.get_session_list(
            user_id=current_user.username,
            page=page,
            page_size=page_size,
            agent_id=agent_id,
            keyword=keyword
        )

        pageable_response = Pageable(
            data=result["items"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
        )

        return success_response(result=pageable_response, message="会话列表查询成功")
    except Exception as e:
        logger.error(f"查询会话列表失败: {e}")
        return business_error_response(f"查询会话列表失败: {str(e)}")


@router.get("/sessions/{session_id}/messages", response_model=ApiResponse[ChatHistoryResponse], summary="聊天记录")
@require_roles([UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER])
async def get_session_messages(
    request: Request,
    session_id: int,
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    """
    聊天记录

    功能点：
    - 按会话ID查询
    - 时间范围：仅查询前一天的对话记录
    - 轮次限制：最多显示5轮完整对话（人机交互算一轮）
    - 条数限制：总记录数不超过20条
    - 排序方式：按创建时间正序显示
    - 返回字段：角色（user/assistant/system）、内容、创建时间

    业务规则：
    - 一轮对话定义：用户发送消息 + 智能体回复（可能包含多轮工具调用）
    - 超过20条记录时，返回最后20条
    - 时间范围从当前时间往前推24小时

    权限控制：
    - 用户只能查看自己的会话记录
    """
    try:
        logger.info(f"用户查询聊天记录: user_id={current_user.username}, session_id={session_id}")

        result = chat_service.get_chat_history(session_id, current_user.username)

        return success_response(result=result, message="聊天记录查询成功")
    except Exception as e:
        logger.error(f"查询聊天记录失败: {e}")
        return business_error_response(f"查询聊天记录失败: {str(e)}")