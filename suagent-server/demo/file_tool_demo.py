from langchain_core.messages import HumanMessage
from src.agents import MyAgent
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware
from src.tools import create_read_file_tool, create_write_file_tool


read_file_tool = create_read_file_tool()
write_file_tool = create_write_file_tool()

if __name__ == "__main__":
    agent = MyAgent(
        checkpointer=RedisShortMemory.get_checkpointer(),
        middlewares=[get_my_logger_middleware()],
        tools=[read_file_tool, write_file_tool],
    )
    agent.invoke({"messages": [HumanMessage(content=(
        "帮我写一个类似chrome的小恐龙的那种游戏，单网页HTML代码，文件名自己取，html格式，把你的代码写到文件里去，写完的话告诉我写完了就行"
    ))]})
    agent.invoke({"messages": [HumanMessage(content="请帮我读取你刚刚写的代码，并告诉我代码的结构和实现原理")]})