from langchain.agents.middleware import AgentState, AgentMiddleware
from typing import Any, Callable

from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from src.utils import get_logger
from src.context import BaseContext

class SessionMiddleware(AgentMiddleware[AgentState, BaseContext]):
    @property
    def name(self) -> str:
        return self.__class__.__name__
        
    def after_model(self, state: AgentState, runtime: Runtime[BaseContext]) -> dict[str, Any] | None:
        
        
        return None
    
def get_session_middleware() -> SessionMiddleware:
    return SessionMiddleware()