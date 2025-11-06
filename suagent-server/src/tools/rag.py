"""
RAG工具 - 用于检索和更新向量库
"""

from langchain.tools import tool
from src.memory import PGVectorMemory

vector_store = PGVectorMemory.get_vectore_store()

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """检索相关文档以帮助回答查询"""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

def create_rag_tool():
    """创建RAG工具"""
    return retrieve_context