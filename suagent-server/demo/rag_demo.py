from langchain.tools import tool
from langchain_core.messages import HumanMessage
from src.agents import MyAgent
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware
from src.tools import create_rag_tool
from src.utils import get_logger

SYSTEM_PROMPT = """
你是专业足球智能体，专注足球全场景咨询，服务爱好者、新手、球员、教练等。

核心能力：
- 请优先在知识库范围内回答问题，如果知识库没有就请根据经验回答
- 精准解答足球规则、阵型、战术、门将技巧、数据解读等问题
- 回复遵循“结论先行+分点解析+实战建议”，通俗或专业按需调整
- 补充可操作的训练方法、战术方案，不堆砌理论
- 还可以提供链接供同学学习

回复规范：
- 关键信息突出，分点清晰，教程类含“要点+训练方法”
- 内容准确无错，不模糊表述，不评球队/球员优劣

互动原则：
- 精准抓用户需求，模糊提问简洁追问
- 核心问题答完后，按需补充相关知识点
- 积极引导不同水平用户，提供针对性方向

"""

rag_tool = create_rag_tool()

logger = get_logger(__name__)

if __name__ == "__main__":
    agent = MyAgent(
            checkpointer=RedisShortMemory.get_checkpointer(),
            middlewares=[get_my_logger_middleware()],
            system_prompt=SYSTEM_PROMPT,
            tools=[rag_tool],
        )
    
    agent.invoke({"messages": [HumanMessage(content="我是一位足球新人，请帮我介绍一下3-5-2阵型")]})