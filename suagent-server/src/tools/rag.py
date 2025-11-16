"""
RAG工具 - 用于从向量库检索知识
"""

from langchain_classic.retrievers import BM25Retriever, EnsembleRetriever
from langchain_core.messages import HumanMessage
from langchain.tools import tool, ToolRuntime
from src.memory import PGVectorMemory
from src.workflow import rag_workflow
from src.context import BaseContext
from langchain_core.tools import create_retriever_tool

@tool(response_format="content_and_artifact")
def long_memroy(query: str, runtime: ToolRuntime[BaseContext]):
    """检索过往该用户与所有智能体的对话以帮助回答查询"""
    vector_store = PGVectorMemory.get_vectore_store("memory", str(runtime.context.user_id))
    retrieved_docs = vector_store.similarity_search(query, k=5)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs)
    return serialized, retrieved_docs
    
@tool
def retrieve_context(query: str, runtime: ToolRuntime[BaseContext]) -> str:
    """
    检索相关文档以帮助回答查询

    Args:
        query: 查询问题
        runtime: 工具运行时上下文

    Returns:
        通过RAG流检索到的回答
        
    Example:
    >>> retrieve_context("什么是越位规则？")
    "越位规则是足球比赛中的一种规则，当进攻方球员在对方半场内接到传球时，如果该球员比对方最后一名防守球员更靠近对方球门线，则视为越位。"
    """
    # 从运行时上下文获取 agent_id 和 user_id
    agent_id = getattr(runtime.context, 'agent_id', 'default')
    user_id = getattr(runtime.context, 'user_id', 'default')
    
    graph = rag_workflow(agent_id=agent_id, user_id=user_id)
    infomation = graph.invoke({"messages": [HumanMessage(content=query)]})
    return infomation["messages"][-1].content


def create_rag_tool():
    """创建RAG工具"""
    return retrieve_context

def create_long_memroy_tool():
    """创建长期记忆工具"""
    return long_memroy