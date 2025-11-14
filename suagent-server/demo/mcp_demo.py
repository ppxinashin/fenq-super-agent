import asyncio

from langchain_core.messages import HumanMessage
from src.mcp_client import MyMCPClient
from src.agents import MyAgent
from langgraph.checkpoint.memory import InMemorySaver
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware

async def main():
    my_mcp_client = MyMCPClient()
    tools = await my_mcp_client.get_tools()
    agent = MyAgent(
        checkpointer=await RedisShortMemory.get_acheckpointer(),
        middlewares=[get_my_logger_middleware()],
        tools=tools,
    )
    await agent.ainvoke({"messages": [HumanMessage(content="大连中山广场到梭鱼湾足球场开车怎么走？")]})
    
if __name__ == "__main__":
    asyncio.run(main())