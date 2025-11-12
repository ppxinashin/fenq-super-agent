from langchain_core.messages import HumanMessage
from src.agents import MyAgent
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware
from src.tools import create_execute_command_tool

execute_command_tool = create_execute_command_tool()

if __name__ == "__main__":
    agent = MyAgent(
        checkpointer=RedisShortMemory.get_checkpointer(),
        middlewares=[get_my_logger_middleware()],
        tools=[execute_command_tool],
    )
    agent.invoke({"messages": [HumanMessage(content="请帮我看一下当前项目需要哪些依赖")]})