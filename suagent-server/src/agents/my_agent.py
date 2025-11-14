"""
Agent 构建类 - 用于构建 Agent
"""

from dataclasses import dataclass
import uuid
from langchain.agents import AgentState, create_agent
from typing import Optional, List, Dict, Any, cast
from langchain.agents.factory import ResponseT
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore
from langgraph.types import Checkpointer

from src.config import settings
from src.context import BaseContext
from src.utils import get_logger

logger = get_logger(__name__)

class MyAgent:
    """Agent 类"""

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
        middlewares: Optional[List[AgentMiddleware[Any, Any]]] = None,
        checkpointer: Optional[Checkpointer] = None,
        store: Optional[BaseStore] = None,
        chat_id: Optional[int] = None,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        recursion_limit: Optional[int] = None,
        context: Optional[BaseContext] = None,
    ):
        """
        初始化 My Agent Builder
        
        Args:
            llm: 语言模型（可选）
            tools: 工具列表（可选）
            system_prompt: 系统提示词（可选）
            middlewares: 中间件列表（可选）
            checkpointer: 短期记忆检查点（可选）
            store: 长期记忆存储（可选）
            chat_id: 聊天 ID（可选）
            user_id: 用户 ID（可选）
            agent_id: 智能体 ID（可选）
            recursion_limit: 递归限制（可选）
            context: 上下文（可选）
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
        self.chat_id = chat_id or None
        # 初始化用户 ID
        self.user_id = user_id or None
        # 初始化智能体 ID
        self.agent_id = agent_id or None
        # 初始化递归限制
        self.recursion_limit = recursion_limit or 100
        # 初始化 Agent
        self._agent = self._build()
        # 初始化上下文
        self.context = context or BaseContext(user_id=self.user_id, chat_id=self.chat_id, agent_id=self.agent_id)

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
    
    def invoke(self, input, cfg:dict[str, Any] | None = None):
        config = self._build_config(cfg)
        return self._agent.invoke(input, config, context=self.context)
    
    def stream(self, input, cfg:dict[str, Any] | None = None):
        config = self._build_config(cfg)
        return self._agent.stream(input, config, context=self.context)
    
    def ainvoke(self, input, cfg:dict[str, Any] | None = None):
        config = self._build_config(cfg)
        return self._agent.ainvoke(input, config, context=self.context, stream_mode="messages")
    
    def astream(self, input, cfg:dict[str, Any] | None = None):
        config = self._build_config(cfg)
        return self._agent.astream(input, config, context=self.context, stream_mode="messages")
    
    def _build_config(self, cfg: dict[str, Any] | None = None) -> RunnableConfig:
        """构建配置字典
        
        Args:
            cfg: 额外的配置参数，可以包含 recursion_limit, configurable 等
            
        Returns:
            完整的配置字典
        """
        # 基础配置，包含 thread_id
        config = {"configurable": {"thread_id": f'{self.agent_id}_{self.chat_id}'}, "recursion_limit": self.recursion_limit}
        if self.user_id:
            config["configurable"]["user_id"] = self.user_id
        if self.agent_id:
            config["configurable"]["agent_id"] = self.agent_id
        if cfg:
            # 合并 configurable 中的配置
            if "configurable" in cfg:
                config["configurable"].update(cfg["configurable"])
            
            # 添加其他根级别的配置（如 recursion_limit）
            for key, value in cfg.items():
                if key != "configurable":
                    config[key] = value
        
        return cast(RunnableConfig, config)
