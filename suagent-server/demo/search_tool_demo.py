from langchain_core.messages import HumanMessage
from langchain.agents.middleware import ToolCallLimitMiddleware
from src.agents import MyAgent
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware, get_session_middleware
from src.tools import create_now_time_tool, create_web_search_tool, create_web_scraper_tool

search_tool = create_web_search_tool()
scrape_tool = create_web_scraper_tool()
now_time_tool = create_now_time_tool()

# 改进的系统提示词，明确告诉 AI 在搜索不到结果时应该如何处理
IMPROVED_SYSTEM_PROMPT = """你是一个智能 AI 助手，名叫 Fenq Super Agent。
你的职责是：
1. 理解用户的问题和需求
2. 使用可用的工具来获取信息和完成任务
3. 提供准确、有帮助的回答
4. 保持友好、专业的态度

重要规则：
- 如果搜索工具返回的结果不相关或无用，最多尝试2-3次不同的搜索关键词
- 如果多次搜索仍然找不到有用信息，应该诚实地告诉用户当前无法找到相关信息
- 不要无限循环搜索，要学会适时停止
- 当你已经尽力但仍然找不到信息时，直接回复用户说明情况

如果你不确定如何回答，请诚实地告诉用户。
如果需要使用工具，请选择最合适的工具并正确调用。
"""

if __name__ == "__main__":
    # 创建 agent，配置工具调用限制和递归限制
    agent = MyAgent(
        checkpointer=RedisShortMemory.get_checkpointer(),
        chat_id=2,
        user_id="admin",
        agent_id="search_tool",
        # 按顺序应用中间件：先记录日志，再限制工具调用次数
        middlewares=[
            get_my_logger_middleware(), 
            get_session_middleware(),
            ToolCallLimitMiddleware(run_limit=10, exit_behavior="end")
        ],
        tools=[now_time_tool, search_tool, scrape_tool],
        system_prompt=IMPROVED_SYSTEM_PROMPT,  # 使用改进的系统提示词
    )
    
    # ToolCallLimitMiddleware 的 run_limit=5 会限制工具调用次数：
    # - 当工具调用次数达到指定次数时，会跳到 end 节点并返回提示信息
    # - exit_behavior="end" 表示超过限制时优雅地结束，而不是抛出错误
    agent.invoke({"messages": [HumanMessage(content="今天是几号？")]})
    agent.invoke({"messages": [HumanMessage(content="获取一下截至今天的中超积分榜，必要的话需要做网页抓取")]})
    
