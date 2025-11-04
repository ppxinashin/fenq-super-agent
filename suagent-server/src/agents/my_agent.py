"""
Agent 构建类 - 用于构建 Agent
"""

from dataclasses import dataclass
import uuid
from langchain.agents import AgentState, create_agent
from typing import Optional, List, Dict, Any
from langchain.agents.factory import ResponseT
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore
from langgraph.types import Checkpointer

from src.config import settings



class MyAgent:
    """Agent 类"""

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
        middlewares: Optional[List[AgentMiddleware]] = None,
        checkpointer: Optional[Checkpointer] = None,
        store: Optional[BaseStore] = None,
        chatId: Optional[str] = None,
    ):
        """
        初始化 My Agent Builder
        
        Args:
            llm: 语言模型（可选）
            tools: 工具列表（可选）
            system_prompt: 系统提示词（可选）
        """
        # 初始化语言模型
        if llm is None:
            self.llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
            )
        else:
            self.llm = llm
        
        # 初始化工具
        self.tools = tools or []
        # 系统提示词
        self.system_prompt = system_prompt or self._default_system_prompt()
        # 初始化中间件
        self.middlewares = middlewares or []
        # 初始化短期记忆
        self.checkpointer = checkpointer or None
        # 初始化长期记忆
        self.store = store or None
        # 初始化聊天 ID
        self.chatId = chatId or str(uuid.uuid4())
        # 初始化 Agent
        self._agent = self._build()

    def _default_system_prompt(self) -> str:
        """默认系统提示词"""
        return """你是一个智能 AI 助手，名叫 Fenq Super Agent。
        你的职责是：
        1. 理解用户的问题和需求
        2. 使用可用的工具来获取信息和完成任务
        3. 提供准确、有帮助的回答
        4. 保持友好、专业的态度

        如果你不确定如何回答，请诚实地告诉用户。
        如果需要使用工具，请选择最合适的工具并正确调用。
        """
    
    def _build(self):
        """创建 Agent"""
        return create_agent(
            model=self.llm,
            tools=self.tools,
            checkpointer=self.checkpointer,
            store=self.store,
            system_prompt=self.system_prompt,
            middleware=self.middlewares
        )
    
    def invoke(self, input):
        return self._agent.invoke(input, {"configurable": {"thread_id": self.chatId}})
    
    def stream(self, input):
        return self._agent.stream(input, {"configurable": {"thread_id": self.chatId}})
    
    def ainvoke(self, input):
        return self._agent.ainvoke(input, {"configurable": {"thread_id": self.chatId}})
    
    def astream(self, input):
        return self._agent.astream(input, {"configurable": {"thread_id": self.chatId}})
