"""
RAG工具 - 用于检索和更新向量库
"""

from langchain.tools import tool
from src.memory import PGVectorMemory

vector_store = PGVectorMemory.get_vectore_store()

@tool
def retrieve_context(query: str):
    """
    检索相关文档以帮助回答查询
    
    Args:
        query: 查询问题
    
    Returns:
        检索到的文档
        
    Example:
        >>> retrieve_context("什么是越位规则？")
        "越位规则是足球比赛中的一种规则，当进攻方球员在对方半场内接到传球时，如果该球员比对方最后一名防守球员更靠近对方球门线，则视为越位。"
    """
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

def create_rag_tool():
    """创建RAG工具"""
    return retrieve_context