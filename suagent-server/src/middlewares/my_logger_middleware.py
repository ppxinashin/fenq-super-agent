from langchain.agents.middleware import AgentState, AgentMiddleware, PIIMiddleware
from typing import Any
from src.utils import get_logger

class MyLoggerMiddleware(AgentMiddleware[AgentState]):
    @property
    def name(self) -> str:
        return self.__class__.__name__
    
    def __init__(self):
        self._logger = get_logger(self.name)
        
    def before_model(self, state: AgentState, runtime) -> dict[str, Any] | None:
        msg = state.get("messages", [])[-1].content
        self._logger.info(f"我的提问: {msg}")
        return None
    
    def after_model(self, state: AgentState, runtime) -> dict[str, Any] | None:
        msg = state.get("messages", [])[-1].content
        self._logger.info(f"大模型的回答: {msg}")
        return None

def get_my_logger_middleware() -> MyLoggerMiddleware:
    return MyLoggerMiddleware()