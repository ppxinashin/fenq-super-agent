from .llm_rag import _response_model
from langchain_core.tools import create_retriever_tool
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode

from src.memory import PGVectorMemory
from src.utils import get_logger

logger = get_logger(__name__)
vector_store = PGVectorMemory.get_vectore_store()
retriever = vector_store.as_retriever()

TOOL_PROMPT = "请根据要求从知识库中检索出相关文档，并返回相关的信息"

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_from_knowledge_base",
    TOOL_PROMPT,
)

def generate_query_or_respond(state: MessagesState):
    """
    调用模型以根据当前状态生成响应。给定问题后，它会决定使用检索工具进行检索，还是直接回应用户。
    """
    response = (
        _response_model
        .bind_tools([retriever_tool]).invoke(state["messages"])  
    )
    logger.info(f"模型的决策: {response.content}")
    return {"messages": [response]}

def retrieve_node():
    """用于判断下一步该怎么做"""
    return ToolNode([retriever_tool])