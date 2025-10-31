"""
基础 Agent 类 - 提供通用的 Agent 功能
"""

from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)


class BaseAgent:
    """基础 Agent 类"""

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        初始化 Base Agent
        
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
                api_key=settings.openai_api_key,
            )
            logger.info(f"使用默认 OpenAI 模型: {settings.openai_model}")
        else:
            self.llm = llm
            logger.info(f"使用自定义语言模型: {type(llm).__name__}")
        
        # 初始化工具
        self.tools = tools or []
        logger.info(f"加载 {len(self.tools)} 个工具")
        
        # 系统提示词
        self.system_prompt = system_prompt or self._default_system_prompt()
        logger.info("Base Agent 初始化完成")

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

    def get_tools(self) -> List[BaseTool]:
        """获取工具列表"""
        return self.tools

    def add_tool(self, tool: BaseTool) -> None:
        """添加工具"""
        self.tools.append(tool)
        logger.info(f"添加工具: {tool.name}")

    def remove_tool(self, tool_name: str) -> None:
        """移除工具"""
        self.tools = [t for t in self.tools if t.name != tool_name]
        logger.info(f"移除工具: {tool_name}")

    def get_llm(self) -> BaseChatModel:
        """获取语言模型"""
        return self.llm

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return self.system_prompt

    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示词"""
        self.system_prompt = prompt
        logger.info("更新系统提示词")

