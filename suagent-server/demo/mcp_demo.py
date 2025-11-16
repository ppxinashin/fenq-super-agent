import asyncio

from langchain_core.messages import HumanMessage
from src.mcp_client import MyMCPClient
from src.agents import MyAgent
from langgraph.checkpoint.memory import InMemorySaver
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware
from src.tools import create_calculator_tool

async def main():
    my_mcp_client = MyMCPClient()
    tools = await my_mcp_client.get_tools()
    tools.append(create_calculator_tool())
    agent = MyAgent(
        checkpointer=await RedisShortMemory.get_acheckpointer(),
        middlewares=[get_my_logger_middleware()],
        tools=tools,
    )
    await agent.ainvoke({"messages": [HumanMessage(content="114*514+1919-810=?")]})
    
if __name__ == "__main__":
    asyncio.run(main())