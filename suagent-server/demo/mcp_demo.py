import asyncio

from langchain_core.messages import HumanMessage
from src.mcp import MyMCPClient
from src.agents import MyAgent
from langgraph.checkpoint.memory import InMemorySaver
from src.middlewares import get_my_logger_middleware

async def main():
    my_mcp_client = MyMCPClient()
    tools = await my_mcp_client.get_tools()
    agent = MyAgent(
        checkpointer=InMemorySaver(),
        middlewares=[get_my_logger_middleware()],
        tools=tools,
    )
    await agent.ainvoke({"messages": [HumanMessage(content="帮我查询一下从黄龙体育场到西湖的路线")]})
    
if __name__ == "__main__":
    asyncio.run(main())