"""
基于 LangGraph 的 Agent 实现 - 支持复杂的工作流和状态管理
"""

from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.graph.message import add_messages

from src.agents.base_agent import BaseAgent
from src.utils import get_logger

logger = get_logger(__name__)


class AgentState(TypedDict):
    """Agent 状态定义"""
    messages: Annotated[List[BaseMessage], add_messages]
    # 可以添加更多状态字段


class GraphAgent(BaseAgent):
    """基于 LangGraph 的 Agent"""

    def __init__(
        self,
        llm=None,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        初始化 Graph Agent
        
        Args:
            llm: 语言模型
            tools: 工具列表
            system_prompt: 系统提示词
        """
        super().__init__(llm, tools, system_prompt)
        
        # 创建工具执行器
        self.tool_executor = ToolExecutor(self.tools) if self.tools else None
        
        # 构建状态图
        self.graph = self._build_graph()
        self.app = self.graph.compile()
        
        logger.info("Graph Agent 初始化完成")

    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 状态图"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("agent", self._agent_node)
        
        if self.tools:
            workflow.add_node("tools", self._tool_node)
        
        # 设置入口点
        workflow.set_entry_point("agent")
        
        # 添加条件边
        if self.tools:
            workflow.add_conditional_edges(
                "agent",
                self._should_continue,
                {
                    "continue": "tools",
                    "end": END,
                }
            )
            workflow.add_edge("tools", "agent")
        else:
            workflow.add_edge("agent", END)
        
        logger.info("LangGraph 状态图构建完成")
        return workflow

    def _agent_node(self, state: AgentState) -> AgentState:
        """Agent 节点 - 调用 LLM"""
        messages = state["messages"]
        
        # 添加系统提示词（如果是第一条消息）
        if len(messages) == 1 or not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=self.system_prompt)] + messages
        
        # 如果有工具，绑定到 LLM
        if self.tools:
            llm_with_tools = self.llm.bind_tools(self.tools)
            response = llm_with_tools.invoke(messages)
        else:
            response = self.llm.invoke(messages)
        
        return {"messages": [response]}

    def _tool_node(self, state: AgentState) -> AgentState:
        """工具节点 - 执行工具调用"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # 提取工具调用
        tool_calls = getattr(last_message, "tool_calls", [])
        
        if not tool_calls:
            return {"messages": []}
        
        # 执行工具
        outputs = []
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            logger.info(f"调用工具: {tool_name}, 参数: {tool_args}")
            
            # 执行工具
            action = ToolInvocation(
                tool=tool_name,
                tool_input=tool_args,
            )
            
            try:
                output = self.tool_executor.invoke(action)
                logger.info(f"工具 {tool_name} 执行成功")
            except Exception as e:
                output = f"工具执行失败: {str(e)}"
                logger.error(f"工具 {tool_name} 执行失败: {str(e)}")
            
            # 创建工具消息
            from langchain_core.messages import ToolMessage
            tool_message = ToolMessage(
                content=str(output),
                tool_call_id=tool_call["id"],
            )
            outputs.append(tool_message)
        
        return {"messages": outputs}

    def _should_continue(self, state: AgentState) -> str:
        """判断是否继续执行"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # 检查是否有工具调用
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        
        return "end"

    def invoke(self, message: str, **kwargs) -> str:
        """
        同步调用 Agent
        
        Args:
            message: 用户消息
            **kwargs: 其他参数
        
        Returns:
            Agent 的回复
        """
        logger.info(f"收到用户消息: {message[:100]}...")
        
        # 准备输入
        inputs = {"messages": [HumanMessage(content=message)]}
        
        # 执行图
        result = self.app.invoke(inputs, **kwargs)
        
        # 提取最后一条 AI 消息
        messages = result.get("messages", [])
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                logger.info("Agent 回复生成完成")
                return msg.content
        
        logger.warning("未找到 AI 回复消息")
        return "抱歉，我无法生成回复。"

    async def ainvoke(self, message: str, **kwargs) -> str:
        """
        异步调用 Agent
        
        Args:
            message: 用户消息
            **kwargs: 其他参数
        
        Returns:
            Agent 的回复
        """
        logger.info(f"收到用户消息（异步）: {message[:100]}...")
        
        # 准备输入
        inputs = {"messages": [HumanMessage(content=message)]}
        
        # 异步执行图
        result = await self.app.ainvoke(inputs, **kwargs)
        
        # 提取最后一条 AI 消息
        messages = result.get("messages", [])
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                logger.info("Agent 回复生成完成（异步）")
                return msg.content
        
        logger.warning("未找到 AI 回复消息")
        return "抱歉，我无法生成回复。"

    def stream(self, message: str, **kwargs):
        """
        流式调用 Agent
        
        Args:
            message: 用户消息
            **kwargs: 其他参数
        
        Yields:
            Agent 的回复流
        """
        logger.info(f"收到用户消息（流式）: {message[:100]}...")
        
        # 准备输入
        inputs = {"messages": [HumanMessage(content=message)]}
        
        # 流式执行图
        for output in self.app.stream(inputs, **kwargs):
            for key, value in output.items():
                logger.debug(f"流式输出节点: {key}")
                yield value


def create_graph_agent(
    tools: Optional[List[BaseTool]] = None,
    system_prompt: Optional[str] = None,
) -> GraphAgent:
    """
    创建 Graph Agent
    
    Args:
        tools: 工具列表
        system_prompt: 系统提示词
    
    Returns:
        GraphAgent 实例
    """
    return GraphAgent(tools=tools, system_prompt=system_prompt)

