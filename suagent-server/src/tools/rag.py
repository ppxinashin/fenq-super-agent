"""
RAG工具 - 用于从向量库检索知识
"""

from langchain.tools import tool
from langchain_core.messages import HumanMessage
from src.workflow import rag_workflow

@tool
def retrieve_context(query: str) -> str:
    """
    检索相关文档以帮助回答查询

    Args:
        query: 查询问题

    Returns:
        通过RAG流检索到的回答
        
    Example:
    >>> retrieve_context("什么是越位规则？")
    "越位规则是足球比赛中的一种规则，当进攻方球员在对方半场内接到传球时，如果该球员比对方最后一名防守球员更靠近对方球门线，则视为越位。"
    """
    graph = rag_workflow()
    infomation = graph.invoke({"messages": [HumanMessage(content=query)]})
    return infomation["messages"][-1].content


def create_rag_tool():
    """创建RAG工具"""
    return retrieve_context