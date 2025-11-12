from .llm_rag import _response_model
from langchain_core.tools import create_retriever_tool
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

from src.memory import PGVectorMemory
from src.utils import get_logger

logger = get_logger(__name__)

TOOL_PROMPT = "请根据要求从知识库中检索出相关文档，并返回相关的信息"

def get_retriever(agent_id: str, user_id: str):
    """
    获取检索器实例
    
    Args:
        agent_id: 智能体ID
        user_id: 用户ID
        
    Returns:
        EnsembleRetriever: 混合检索器实例
    """
    vector_store = PGVectorMemory.get_vectore_store(agent_id, user_id)
    vector_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    all_documents = PGVectorMemory.get_all_documents(agent_id, user_id)
    if all_documents:
        bm25_retriever = BM25Retriever.from_documents(all_documents)
        retriever = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[0.7, 0.3]
        )
    else:
        # 如果没有文档，只使用向量检索器
        retriever = vector_retriever
    
    return retriever

def get_retriever_tool(agent_id: str, user_id: str):
    """
    获取检索工具
    
    Args:
        agent_id: 智能体ID
        user_id: 用户ID
        
    Returns:
        检索工具实例
    """
    retriever = get_retriever(agent_id, user_id)
    retriever_tool = create_retriever_tool(
        retriever,
        "retrieve_from_knowledge_base",
        TOOL_PROMPT,
    )
    return retriever_tool

def generate_query_or_respond_factory(agent_id: str = "default", user_id: str = "default"):
    """
    创建一个绑定了 agent_id 和 user_id 的 generate_query_or_respond 函数
    
    Args:
        agent_id: 智能体ID
        user_id: 用户ID
        
    Returns:
        绑定了参数的节点函数
    """
    retriever_tool = get_retriever_tool(agent_id, user_id)
    
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
    
    # 设置函数名称以便在图中识别
    generate_query_or_respond.__name__ = "generate_query_or_respond"
    return generate_query_or_respond

def retrieve_node(agent_id: str = "default", user_id: str = "default"):
    """
    用于判断下一步该怎么做
    
    Args:
        agent_id: 智能体ID
        user_id: 用户ID
    """
    retriever_tool = get_retriever_tool(agent_id, user_id)
    return ToolNode([retriever_tool])