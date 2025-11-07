from langchain_core.messages import HumanMessage
from src.agents import MyAgent
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware
from src.tools import create_web_search_tool, create_web_scraper_tool

search_tool = create_web_search_tool()
scrape_tool = create_web_scraper_tool()

if __name__ == "__main__":
    agent = MyAgent(
        checkpointer=RedisShortMemory.get_checkpointer(),
        middlewares=[get_my_logger_middleware()],
        tools=[search_tool, scrape_tool],
    )
    agent.invoke({"messages": [HumanMessage(content=(
        "请帮我搜索一下2025赛季中超联赛第29轮过后，谁是第一名，多少积分，必要时需要从搜索结果的链接中抓取信息来获得"
    ))]})