from .llm_rag import _response_model
from langgraph.graph import MessagesState

from src.utils import get_logger

logger = get_logger(__name__)

REWRITE_PROMPT = (
    "请阅读输入内容，并尝试推理其潜在的语义意图。\n"
    "以下是用户的初始问题："
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "请将其表达为一个更优雅、更清晰的问题。"
)


def rewrite_question(state: MessagesState):
    """重写用户的原始问题。"""
    messages = state["messages"]
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)
    logger.info(f"重写提示词: {prompt}")
    response = _response_model.invoke([{"role": "user", "content": prompt}])
    content = response.content
    logger.info(f"重写: {content}")
    return {"messages": [{"role": "user", "content": content}]}