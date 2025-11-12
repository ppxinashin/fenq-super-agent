"""
智能体聊天相关控制器
"""

import json
from typing import AsyncGenerator, Optional, Union, Tuple
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from langchain_mcp_adapters.client import MultiServerMCPClient
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage

from src.model.database import get_db
from src.model.crud_agent import crud_agent
from src.model.crud_session_log import crud_session_log
from src.model.user import User
from src.api.request.chat_request import ChatRequest
from src.api.interceptor.auth_interceptor import get_current_user
from src.agents import MyAgent
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware, get_session_middleware
from src.mcp import MyMCPClient
from src.utils.logger import get_logger
from src.context import BaseContext
from src.tools import (
    create_web_scraper_tool,
    create_calculator_tool,
    create_rag_tool,
    create_read_file_tool,
    create_write_file_tool,
    create_execute_command_tool,
    create_web_search_tool,
    create_downloader_tool,
    create_now_time_tool,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/agent", tags=["智能体聊天"])


# 工具映射表：工具名称到工具创建函数的映射
TOOL_FACTORY_MAP = {
    "web_scraper": create_web_scraper_tool,
    "calculator": create_calculator_tool,
    "rag": create_rag_tool,
    "read_file": create_read_file_tool,
    "write_file": create_write_file_tool,
    "execute_command": create_execute_command_tool,
    "web_search": create_web_search_tool,
    "downloader": create_downloader_tool,
    "now_time": create_now_time_tool,
}


def _normalize_chat_id(chat_id: Optional[Union[str, int]]) -> Optional[str]:
    """将传入的 chat_id 规整为非空字符串"""
    if chat_id is None:
        return None
    if isinstance(chat_id, int):
        return str(chat_id)
    normalized = chat_id.strip()
    return normalized or None


def _build_session_key(agent_id: str, index: int) -> str:
    return f"{agent_id}_{index}"


def _build_internal_session_id(agent_id: str, index: int) -> int:
    prefix = abs(hash(agent_id)) % (10 ** 8)
    return int(f"{prefix}{index}")


def _parse_session_key(agent_id: str, session_key: str) -> Tuple[int, int]:
    prefix = f"{agent_id}_"
    if not session_key.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="会话ID与智能体不匹配"
        )
    index_part = session_key[len(prefix):]
    if not index_part.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="会话ID格式不正确"
        )
    index = int(index_part)
    if index <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="会话ID必须为正整数序号"
        )
    session_id = _build_internal_session_id(agent_id, index)
    return index, session_id


def _create_session_identity(agent_id: str, db: Session) -> Tuple[int, str]:
    session_count = crud_session_log.count_sessions_by_agent(db=db, agent_id=agent_id)
    next_index = max(session_count, 0) + 1
    while True:
        session_id = _build_internal_session_id(agent_id, next_index)
        bound_agent = crud_session_log.get_session_agent(db=db, session_id=session_id)
        if bound_agent is None or bound_agent == agent_id:
            session_key = _build_session_key(agent_id, next_index)
            return session_id, session_key
        next_index += 1


def _resolve_session_identity(
    agent_id: str,
    incoming_chat_id: Optional[Union[str, int]],
    db: Session
) -> Tuple[int, str]:
    normalized = _normalize_chat_id(incoming_chat_id)
    if normalized:
        if "_" in normalized:
            _, session_id = _parse_session_key(agent_id, normalized)
            bound_agent = crud_session_log.get_session_agent(db=db, session_id=session_id)
            if bound_agent and bound_agent != agent_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="会话ID已绑定到其他智能体"
                )
            return session_id, normalized
        try:
            session_id = int(normalized)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="会话ID格式不正确"
            )
        bound_agent = crud_session_log.get_session_agent(db=db, session_id=session_id)
        if bound_agent and bound_agent != agent_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="会话ID已绑定到其他智能体"
            )
        return session_id, normalized
    return _create_session_identity(agent_id, db)


async def generate_chat_stream(
    agent: MyAgent,
    message: str,
    session_id: int,
    agent_id: str,
    user_id: int,
    db: Session
) -> AsyncGenerator[str, None]:
    """
    生成聊天流式响应
    
    注意：用户消息和AI响应的记录由SessionMiddleware自动处理
    
    Args:
        agent: 智能体实例
        message: 用户消息
        session_id: 会话ID
        agent_id: 智能体ID
        user_id: 用户ID
        db: 数据库会话
    
    Yields:
        流式响应内容
    """
    try:
        # 流式调用智能体（中间件会自动记录对话）
        async for chunk in agent.astream({"messages": [HumanMessage(content=message)]}):
            # 根据chunk的类型提取内容
            if hasattr(chunk, 'messages') and chunk.messages:
                # 获取最后一条消息
                last_message = chunk.messages[-1]
                if hasattr(last_message, 'content') and last_message.content:
                    content = last_message.content
                    yield f"data: {content}\n\n"
            elif hasattr(chunk, 'content') and chunk.content:
                content = chunk.content
                yield f"data: {content}\n\n"
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"流式响应生成失败: {str(e)}", exc_info=True)
        yield f"data: [ERROR] {str(e)}\n\n"


@router.post("/chat", summary="智能体聊天（流式输出）")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    向智能体发送聊天消息（流式输出）
    
    - **agent_id**: 智能体ID
    - **message**: 用户消息内容
    - **chat_id**: 聊天会话ID（可选，不传则自动生成新会话）
    
    权限：所有已登录用户
    
    返回：Server-Sent Events (SSE) 流式响应
    """
    try:
        # 1. 从token中提取user_id
        user_id = current_user.id
        logger.info(f"用户 {user_id} 请求与智能体 {request.agent_id} 聊天")
        
        # 2. 根据agent_id查询智能体信息
        agent_db = crud_agent.get_by_agent_id(db=db, agent_id=request.agent_id)
        if not agent_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"智能体 {request.agent_id} 不存在"
            )
        
        # 3. 生成/解析会话ID
        session_id, public_chat_id = _resolve_session_identity(
            agent_id=request.agent_id,
            incoming_chat_id=request.chat_id,
            db=db
        )

        logger.info(f"内部会话ID: {session_id}，外部会话标识: {public_chat_id}")
        
        # 4. 创建上下文（包含session_id用于中间件记录对话）
        context = BaseContext(
            user_id=str(user_id),
            chat_id=session_id,
            agent_id=request.agent_id,
            session_id=session_id
        )
        
        # 5. 检查智能体是否开启MCP模式
        if agent_db.mcp_enabled:
            # MCP模式：使用MCP客户端获取工具
            logger.info(f"智能体 {request.agent_id} 已开启MCP模式，使用MCP工具")
            mcp_servers = agent_db.mcp_servers
            # 创建MCP客户端并获取工具
            mcp_client = MyMCPClient(mcp_servers=mcp_servers.dict())
            tools = await mcp_client.get_tools()
            
            # 创建智能体（异步模式）
            agent = MyAgent(
                checkpointer=await RedisShortMemory.get_acheckpointer(),
                middlewares=[get_my_logger_middleware(), get_session_middleware()],
                tools=tools,
                system_prompt=agent_db.system_prompt,
                user_id=str(user_id),
                agent_id=request.agent_id,
                chat_id=session_id,
                context=context
            )
        else:
            # 非MCP模式：使用系统自带工具
            logger.info(f"智能体 {request.agent_id} 未开启MCP模式，使用系统工具")
            
            # 从智能体配置中加载工具
            tools = []
            if agent_db.tools:
                for tool_name in agent_db.tools:
                    if tool_name in TOOL_FACTORY_MAP:
                        try:
                            tool = TOOL_FACTORY_MAP[tool_name]()
                            tools.append(tool)
                            logger.info(f"已加载工具: {tool_name}")
                        except Exception as e:
                            logger.error(f"加载工具 {tool_name} 失败: {str(e)}")
                    else:
                        logger.warning(f"工具 {tool_name} 不存在于工具映射表中")
            
            # 创建智能体（异步模式）
            agent = MyAgent(
                checkpointer=await RedisShortMemory.get_acheckpointer(),
                middlewares=[get_my_logger_middleware(), get_session_middleware()],
                tools=tools,
                system_prompt=agent_db.system_prompt,
                user_id=str(user_id),
                agent_id=request.agent_id,
                chat_id=session_id,
                context=context
            )
        
        # 6. 返回流式响应
        return StreamingResponse(
            generate_chat_stream(
                agent=agent,
                message=request.message,
                session_id=session_id,
                agent_id=request.agent_id,
                user_id=user_id,
                db=db
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
                "X-Chat-Id": public_chat_id,
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天请求处理失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聊天请求处理失败: {str(e)}"
        )
