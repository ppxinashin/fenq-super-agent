from typing import Literal
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)

grader_model = ChatOpenAI(
    model=settings.openai_model,
    temperature=0
)

# 相关性评分基准线
PASS_SCORE = 6.0

GRADE_PROMPT = (
    "你需要对检索到的文档与用户问题的相关性进行评分。\n"
    "以下是检索到的文档：{context}\n"
    "以下是用户的问题：{question}\n"
    "请在0到10分的范围内对文档与问题的相关性进行评分，\n"
    "其中 {pass_score} 分作为相关的基准线：{pass_score} 分及以上表示相关（文档包含与问题相关的关键词或语义，且分数越高说明相关性越强）；"
    "{pass_score} 分以下表示不相关（分数越低说明相关性越弱，0 分表示完全不相关，即文档中不包含任何与问题相关的关键词或语义）。"
    "10 分表示高度相关，即文档能充分解答问题，且包含高度相关的关键词和语义。"
    "0到10分之间的分数应反映相关性程度，分数越高表示相关性越强。\n"
    "请给出一个最多保留两位小数的得分，请用JSON格式返回\n"
    "格式：{{'score': 6.0 }}，6.0需要替换成实际得分"
)

class GradeDocuments(BaseModel):  
    """对检索到的文档与用户问题的相关性进行评分。"""

    score: float = Field(
        description=f"相关性评分：0到10分，0分表示完全不相关，{PASS_SCORE}分为相关基准线，10分表示高度相关"
    )

def grade_documents(
    state: MessagesState,
) -> Literal["generate_answer", "rewrite_question"]:
    """确定检索到的文档与用户问题的相关性是否足够，决定是否直接回答或重新生成问题。"""
    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context, pass_score=PASS_SCORE)
    logger.info(f'相关性评分提示词: {prompt}')
    response = (
        grader_model
        .with_structured_output(GradeDocuments).invoke(  
            [{"role": "user", "content": prompt}]
        )
    )
    logger.info(response)
    score = response.score

    if score >= PASS_SCORE:
        return "generate_answer"
    else:
        return "rewrite_question"