from langchain.agents.middleware import AgentState, AgentMiddleware, PIIMiddleware
from typing import Any

from langchain_core.messages import ToolMessage
from langgraph.types import Command
from src.utils import get_logger

class MyLoggerMiddleware(AgentMiddleware[AgentState]):
    @property
    def name(self) -> str:
        return self.__class__.__name__
    
    def __init__(self):
        self._logger = get_logger(self.name)
        
    def before_model(self, state: AgentState, runtime) -> dict[str, Any] | None:
        msg = state.get("messages", [])[-1].content
        self._logger.info(f"AI Request: {msg}")
        return None
    
    def wrap_tool_call(self, request, handler) -> ToolMessage | Command:
        result = handler(request)
        tool_name = request.tool.get_name() if request.tool else "Unknown"
        tool_call = request.tool_call if request.tool_call else {}
        self._logger.info(f"AI Call Tool Name: {tool_name}, Args: {tool_call.get('args', {})}")
        return result
    
    async def awrap_tool_call(self, request, handler) -> ToolMessage | Command:
        result = await handler(request)
        tool_name = request.tool.get_name() if request.tool else "Unknown"
        tool_call = request.tool_call if request.tool_call else {}
        self._logger.info(f"AI Call Tool Name: {tool_name}, Args: {tool_call.get('args', {})}")
        return result
    
    def after_model(self, state: AgentState, runtime) -> dict[str, Any] | None:
        msg = state.get("messages", [])[-1].content
        self._logger.info(f"AI Response: {msg}")
        return None

def get_my_logger_middleware() -> MyLoggerMiddleware:
    return MyLoggerMiddleware()