from traceback import print_tb
from langchain_core.messages import HumanMessage
from src.agents import MyAgent
from src.config import settings
from src.memory import RedisShortMemory
from src.middlewares import get_my_logger_middleware

SYSTEM_PROMPT = """
扮演深耕恋爱心理领域的专家。开场向用户表明身份，告知用户可倾诉恋爱难题。
围绕单身、恋爱、已婚三种状态提问：单身状态询问社交圈拓展及追求心仪对象的困扰；
恋爱状态询问沟通、习惯差异引发的矛盾；已婚状态询问家庭责任与亲属关系处理的问题。
引导用户详述事情经过、对方反应及自身想法，以便给出专属解决方案。
"""

if __name__ == "__main__":
        agent = MyAgent(
            checkpointer=RedisShortMemory.get_checkpointer(),
            middlewares=[get_my_logger_middleware()],
            system_prompt=SYSTEM_PROMPT,
        )
        agent.invoke({"messages": [HumanMessage(content="你好，我是fenq同学，很高兴认识你。")]})
        agent.invoke({"messages": [HumanMessage(content="我的另一半叫安安")]})
        agent.invoke({"messages": [HumanMessage(content="她总是怀疑我出轨，但我并未出轨，我该怎么帮助她？")]})
        agent.invoke({"messages": [HumanMessage(content="还记得我是谁吗？")]})
        agent.invoke({"messages": [HumanMessage(content="还记得我另一半叫什么？")]})