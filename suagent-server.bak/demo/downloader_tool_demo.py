from langchain_core.messages import HumanMessage
from src.agents import MyAgent
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware
from src.tools import create_downloader_tool

downloader_tool = create_downloader_tool()

if __name__ == "__main__":
    agent = MyAgent(
        checkpointer=RedisShortMemory.get_checkpointer(),
        middlewares=[get_my_logger_middleware()],
        tools=[downloader_tool],
    )
    agent.invoke({"messages": [HumanMessage(content=(
        "请帮我下载https://www.codefather.cn/logo.png"
    ))]})