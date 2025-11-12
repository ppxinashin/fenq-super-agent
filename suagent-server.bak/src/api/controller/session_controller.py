"""
会话管理控制器
"""

from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.model.database import get_db
from src.model.crud_session import crud_session
from src.model.crud_session_log import crud_session_log
from src.model.user import User
from src.api.request.session_request import (
    SessionCreateRequest,
    SessionUpdateRequest,
    SessionDeleteRequest,
    SessionListRequest,
    SessionTitleGenerateRequest,
)
from src.api.request.session_log_request import SessionLogListRequest
from src.api.response.session_response import (
    SessionResponse,
    SessionListResponse,
    SessionCreateResponse,
)
from src.api.response.session_log_response import (
    SessionLogResponse,
    SessionLogListResponse,
)
from src.api.response.base_response import success_response, error_response
from src.api.interceptor.auth_interceptor import get_current_user
from src.utils.logger import get_logger
from langchain_openai import ChatOpenAI
from src.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/session", tags=["会话管理"])


def _build_internal_session_id(agent_id: str, index: int) -> int:
    """构建内部会话ID"""
    prefix = abs(hash(agent_id)) % (10 ** 8)
    return int(f"{prefix}{index}")


@router.post("/create", summary="创建新会话")
async def create_session(
    request: SessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新会话
    
    - **agent_id**: 智能体ID
    - **user_id**: 用户ID
    - **title**: 会话标题（可选）
    
    说明：点击新对话时调用，session_id = 全部会话总数 + 1
    """
    try:
        # 统计全部会话数量
        session_count = crud_session.count_all(db=db)
        next_index = session_count + 1
        
        # 生成会话ID
        session_id = _build_internal_session_id(request.agent_id, next_index)
        
        # 检查会话ID是否已存在，如果存在则递增索引
        while crud_session.get_by_session_id(db=db, session_id=session_id):
            next_index += 1
            session_id = _build_internal_session_id(request.agent_id, next_index)
        
        # 创建会话
        session = crud_session.create_session(
            db=db,
            agent_id=request.agent_id,
            session_id=session_id,
            title=request.title or "新对话",
            created_by=str(current_user.id)
        )
        
        logger.info(f"用户 {current_user.id} 创建会话: session_id={session_id}, agent_id={request.agent_id}")
        
        # 获取会话标题
        session_title = str(session.title) if session.title is not None else None
        
        return success_response(
            result=SessionCreateResponse(
                session_id=session_id,
                agent_id=request.agent_id,
                title=session_title
            ),
            message="会话创建成功"
        )
        
    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}"
        )


@router.put("/update", summary="更新会话标题")
async def update_session(
    request: SessionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新会话标题（改名）
    
    - **session_id**: 会话ID
    - **title**: 新的会话标题
    
    权限：只能修改自己创建的会话
    """
    try:
        # 检查会话是否存在
        session = crud_session.get_by_session_id(db=db, session_id=request.session_id)
        if not session:
            return error_response(
                message=f"会话 {request.session_id} 不存在",
                code=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限：只能修改自己创建的会话
        if str(session.created_by) != str(current_user.id):
            return error_response(
                message="无权修改该会话，只能修改自己创建的会话",
                code=status.HTTP_403_FORBIDDEN
            )
        
        # 更新标题
        updated_session = crud_session.update_title(
            db=db,
            session_id=request.session_id,
            title=request.title,
            updated_by=str(current_user.id)
        )
        
        logger.info(f"用户 {current_user.id} 更新会话标题: session_id={request.session_id}, title={request.title}")
        
        return success_response(
            result=SessionResponse.model_validate(updated_session),
            message="会话标题更新成功"
        )
        
    except Exception as e:
        logger.error(f"更新会话标题失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新会话标题失败: {str(e)}"
        )


@router.delete("/delete", summary="删除会话")
async def delete_session(
    request: SessionDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除会话（软删除）
    
    - **session_id**: 会话ID
    
    说明：删除会话时，同时删除会话相关的所有日志
    
    权限：只能删除自己创建的会话
    """
    try:
        # 检查会话是否存在
        session = crud_session.get_by_session_id(db=db, session_id=request.session_id)
        if not session:
            return error_response(
                message=f"会话 {request.session_id} 不存在",
                code=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限：只能删除自己创建的会话
        if str(session.created_by) != str(current_user.id):
            return error_response(
                message="无权删除该会话，只能删除自己创建的会话",
                code=status.HTTP_403_FORBIDDEN
            )
        
        # 删除会话
        success = crud_session.delete_by_session_id(
            db=db,
            session_id=request.session_id,
            deleted_by=str(current_user.id)
        )
        
        if success:
            # 同时删除会话的所有日志
            crud_session_log.delete_by_session_id(
                db=db,
                session_id=request.session_id,
                deleted_by=str(current_user.id)
            )
            
            logger.info(f"用户 {current_user.id} 删除会话: session_id={request.session_id}")
            return success_response(message="会话删除成功")
        else:
            return error_response(message="会话删除失败")
        
    except Exception as e:
        logger.error(f"删除会话失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除会话失败: {str(e)}"
        )


@router.post("/list", summary="查询会话列表")
async def list_sessions(
    request: SessionListRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询会话列表（分页）
    
    - **agent_id**: 智能体ID
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（固定20条）
    
    说明：分页查询该智能体下当前用户创建的所有会话，按创建时间倒序排列
    
    权限：只能查看当前登录用户创建的会话
    """
    try:
        # 每页数量（限制最大20）
        page_size = request.page_size
        
        # 计算跳过的记录数
        skip = (request.page - 1) * page_size
        
        # 获取当前用户ID
        user_id_str = str(current_user.id)
        
        # 查询会话列表（只查询当前用户创建的会话）
        sessions = crud_session.get_by_agent_and_user(
            db=db,
            agent_id=request.agent_id,
            created_by=user_id_str,
            skip=skip,
            limit=page_size
        )
        
        # 计算总数和总页数（只统计当前用户创建的会话）
        total = crud_session.count_by_agent_and_user(
            db=db, 
            agent_id=request.agent_id,
            created_by=user_id_str
        )
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        # 构建响应
        result = SessionListResponse(
            items=[SessionResponse.model_validate(s) for s in sessions],
            total=total,
            page=request.page,
            page_size=page_size,
            total_pages=total_pages,
            has_prev=request.page > 1,
            has_next=request.page < total_pages
        )
        
        logger.info(f"用户 {current_user.id} 查询会话列表: agent_id={request.agent_id}, page={request.page}, total={total}")
        
        return success_response(result=result, message="查询成功")
        
    except Exception as e:
        logger.error(f"查询会话列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询会话列表失败: {str(e)}"
        )


@router.post("/logs", summary="查询会话对话记录")
async def list_session_logs(
    request: SessionLogListRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询指定会话的对话记录（最近7天，分页）
    
    - **session_id**: 会话ID
    - **page**: 页码（从1开始，固定每页20条）
    
    说明：仅能查询当前用户创建的会话日志，日志时间范围限定在最近7天
    """
    try:
        session = crud_session.get_by_session_id(db=db, session_id=request.session_id)
        if not session:
            return error_response(
                message=f"会话 {request.session_id} 不存在",
                code=status.HTTP_404_NOT_FOUND
            )
        
        if str(session.created_by) != str(current_user.id):
            return error_response(
                message="无权查看该会话，只能查看自己创建的会话",
                code=status.HTTP_403_FORBIDDEN
            )
        
        page_data = crud_session_log.get_recent_paginated_by_session(
            db=db,
            session_id=request.session_id,
            days=7,
            page=request.page,
            page_size=request.page_size
        )
        
        log_items = [
            SessionLogResponse.model_validate(log)
            for log in page_data["items"]
        ]
        
        result = SessionLogListResponse(
            items=log_items,
            total=page_data["total"],
            page=page_data["page"],
            page_size=page_data["page_size"],
            total_pages=page_data["total_pages"],
            has_prev=page_data["has_prev"],
            has_next=page_data["has_next"]
        )
        
        logger.info(
            f"用户 {current_user.id} 查询会话日志: "
            f"session_id={request.session_id}, page={page_data['page']}, total={page_data['total']}"
        )
        
        return success_response(result=result, message="查询成功")
    
    except Exception as e:
        logger.error(f"查询会话日志失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询会话日志失败: {str(e)}"
        )


async def generate_title_stream(
    session_id: int,
    agent_id: str,
    db: Session
) -> AsyncGenerator[str, None]:
    """
    流式生成会话标题
    
    Args:
        session_id: 会话ID
        agent_id: 智能体ID
        db: 数据库会话
        
    Yields:
        流式标题内容
    """
    try:
        # 获取会话的最近几条日志（用于生成标题）
        logs = crud_session_log.get_latest_by_session_id(
            db=db,
            session_id=session_id,
            limit=10
        )
        
        if not logs:
            yield "data: 新对话\n\n"
            yield "data: [DONE]\n\n"
            return
        
        # 构建对话内容摘要
        conversation_summary = ""
        for log in reversed(logs):  # 按时间正序
            role_name = "用户" if str(log.role) == "user" else "助手"
            log_content = str(log.content)
            content_text = log_content[:200] if len(log_content) > 200 else log_content  # 限制长度
            conversation_summary += f"{role_name}: {content_text}\n"
        
        # 使用LLM生成标题
        llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.7,
        )
        
        prompt = f"""请根据以下对话内容，生成一个简洁的标题（20字以内）。
要求：
1. 标题要准确概括对话的主要内容
2. 使用中文
3. 不超过20个字
4. 不要使用引号
5. 只返回标题文本，不要其他内容

对话内容：
{conversation_summary}

标题："""
        
        # 流式生成标题
        full_title = ""
        async for chunk in llm.astream(prompt):
            if hasattr(chunk, 'content') and chunk.content:
                chunk_content = str(chunk.content)
                full_title += chunk_content
                # 限制20字
                if len(full_title) <= 20:
                    yield f"data: {chunk_content}\n\n"
                else:
                    break
        
        # 截取前20个字符
        final_title = full_title[:20].strip()
        
        # 更新数据库中的标题
        crud_session.update_title(
            db=db,
            session_id=session_id,
            title=final_title,
            updated_by="system"
        )
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"生成标题失败: {str(e)}", exc_info=True)
        yield f"data: [ERROR] {str(e)}\n\n"


@router.post("/generate-title", summary="流式生成会话标题")
async def generate_title(
    request: SessionTitleGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    流式生成会话标题
    
    - **session_id**: 会话ID
    
    说明：根据会话的对话内容，使用LLM生成一个20字以内的简洁标题
    
    权限：只能为自己创建的会话生成标题
    
    返回：Server-Sent Events (SSE) 流式响应
    """
    try:
        # 检查会话是否存在
        session = crud_session.get_by_session_id(db=db, session_id=request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"会话 {request.session_id} 不存在"
            )
        
        # 检查权限：只能为自己创建的会话生成标题
        if str(session.created_by) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权操作该会话，只能为自己创建的会话生成标题"
            )
        
        logger.info(f"用户 {current_user.id} 请求生成会话标题: session_id={request.session_id}")
        
        # 返回流式响应
        return StreamingResponse(
            generate_title_stream(
                session_id=request.session_id,
                agent_id=str(session.agent_id),
                db=db
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成标题请求处理失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成标题请求处理失败: {str(e)}"
        )
