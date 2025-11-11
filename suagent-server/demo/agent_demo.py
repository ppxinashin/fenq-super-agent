from langchain_core.messages import HumanMessage
from src.agents import MyAgent
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware, get_session_middleware

logger_middleware = get_my_logger_middleware()
session_middleware = get_session_middleware()
SYSTEM_PROMPT = """
你是专业足球智能体，专注足球全场景咨询，服务爱好者、新手、球员、教练等。

核心能力：
- 精准解答足球规则、阵型、战术、门将技巧、数据解读等问题
- 回复遵循“结论先行+分点解析+实战建议”，通俗或专业按需调整
- 补充可操作的训练方法、战术方案，不堆砌理论

回复规范：
- 关键信息突出，分点清晰，教程类含“要点+训练方法”
- 内容准确无错，不模糊表述，不评球队/球员优劣

互动原则：
- 精准抓用户需求，模糊提问简洁追问
- 核心问题答完后，按需补充相关知识点
- 积极引导不同水平用户，提供针对性方向
"""

if __name__ == "__main__":
    agent = MyAgent(
        checkpointer=RedisShortMemory.get_checkpointer(),
        user_id="admin",
        agent_id="football",
        chat_id=1,
        middlewares=[logger_middleware, session_middleware],
        system_prompt=SYSTEM_PROMPT,
    )
    agent.invoke({"messages": [HumanMessage(content="你好，我是fenq同学，我是一位足球新人，平时喜欢看球，但很多规则不知道，不过很高兴认识你。")]})
    agent.invoke({"messages": [HumanMessage(content="我不知道越位规则是什么，能帮我解释一下吗？")]})
    agent.invoke({"messages": [HumanMessage(content="还记得我是谁吗？")]})
    agent.invoke({"messages": [HumanMessage(content="把本次对话总结一下吧")]})