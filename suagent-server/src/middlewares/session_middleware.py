"""
Session日志中间件 - 用于记录对话日志到数据库
"""

from langchain.agents.middleware import AgentState, AgentMiddleware
from typing import Any, Callable

from langchain_core.messages import ToolMessage, HumanMessage, AIMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from src.utils import get_logger
from src.context import BaseContext
from src.model import get_db_session, crud_session_log

logger = get_logger(__name__)


def _has_content(payload: Any) -> bool:
    """判断消息内容是否为空"""
    if payload is None:
        return False
    if isinstance(payload, str):
        return bool(payload.strip())
    if isinstance(payload, (list, tuple, set)):
        return any(_has_content(item) for item in payload)
    if isinstance(payload, dict):
        return any(_has_content(item) for item in payload.values())
    return True

class SessionMiddleware(AgentMiddleware[AgentState, BaseContext]):
    """Session日志中间件 - 自动记录用户消息和AI响应"""
    
    @property
    def name(self) -> str:
        return self.__class__.__name__
    
    def before_model(self, state: AgentState, runtime: Runtime[BaseContext]) -> dict[str, Any] | None:
        """
        在模型调用之前，记录用户消息
        
        Args:
            state: Agent状态
            runtime: 运行时上下文
            
        Returns:
            None
        """
        try:
            # 获取上下文信息
            context = runtime.context
            session_id = context.chat_id
            agent_id = context.agent_id
            user_id = context.user_id
            
            # 如果缺少必要信息，跳过记录
            if not session_id or not agent_id or not user_id:
                logger.warning(f"缺少必要信息，跳过记录用户消息: session_id={session_id}, agent_id={agent_id}, user_id={user_id}")
                return None
            
            # 获取最后一条消息
            messages = state.get("messages", [])
            if not messages:
                return None
            
            last_message = messages[-1]
            
            # 只记录人类消息
            if isinstance(last_message, HumanMessage):
                content = last_message.content
                if not _has_content(content):
                    logger.debug("用户消息为空，跳过日志记录")
                    return None
                
                # 保存到数据库
                with get_db_session() as db:
                    crud_session_log.create_log(
                        db=db,
                        session_id=session_id,
                        agent_id=agent_id,
                        role="user",
                        content=content,
                        created_by=str(user_id)
                    )
                    logger.info(f"用户消息已记录: session_id={session_id}, content_length={len(content)}")
                    
        except Exception as e:
            logger.error(f"记录用户消息失败: {str(e)}", exc_info=True)
        
        return None
        
    def after_model(self, state: AgentState, runtime: Runtime[BaseContext]) -> dict[str, Any] | None:
        """
        在模型调用之后，记录AI响应
        
        Args:
            state: Agent状态
            runtime: 运行时上下文
            
        Returns:
            None
        """
        try:
            # 获取上下文信息
            context = runtime.context
            session_id = context.chat_id
            agent_id = context.agent_id
            user_id = context.user_id
            
            # 如果缺少必要信息，跳过记录
            if not session_id or not agent_id or not user_id:
                logger.warning(f"缺少必要信息，跳过记录AI响应: session_id={session_id}, agent_id={agent_id}, user_id={user_id}")
                return None
            
            # 获取最后一条消息
            messages = state.get("messages", [])
            if not messages:
                return None
            
            last_message = messages[-1]
            
            # 只记录AI消息
            if isinstance(last_message, AIMessage):
                content = last_message.content
                if not _has_content(content):
                    logger.debug("AI响应为空，跳过日志记录")
                    return None
                
                # 保存到数据库
                with get_db_session() as db:
                    crud_session_log.create_log(
                        db=db,
                        session_id=session_id,
                        agent_id=agent_id,
                        role="assistant",
                        content=content,
                        created_by=str(user_id)
                    )
                    logger.info(f"AI响应已记录: session_id={session_id}, content_length={len(content)}")
                    
        except Exception as e:
            logger.error(f"记录AI响应失败: {str(e)}", exc_info=True)
        
        return None
    
def get_session_middleware() -> SessionMiddleware:
    """获取Session日志中间件实例"""
    return SessionMiddleware()
