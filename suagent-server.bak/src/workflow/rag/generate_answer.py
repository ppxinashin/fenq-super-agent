from langgraph.graph import MessagesState

from src.config import settings
from src.utils import get_logger
from .llm_rag import _response_model

logger = get_logger(__name__)


GENERATE_PROMPT = (
    "你是一个问答助手。"
    "请依据以下检索到的文档内容回答问题，无需对答案进行润色或优化，仅返回原始答案即可，不要添加任何额外解释。\n"
    "若文档中不包含问题的答案，请直接返回“我不知道”。\n"
    "问题：{question}\n"
    "文档：{context}"
)


def generate_answer(state: MessagesState):
    """根据检索到的文档生成回答。"""
    question = state["messages"][0].content
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    logger.info(f'生成答案提示词: {prompt}')
    response = _response_model.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}