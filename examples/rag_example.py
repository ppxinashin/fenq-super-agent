"""
RAG 示例 - 展示如何使用向量存储进行检索增强生成
"""

import asyncio
from langchain_core.documents import Document

from src.agents import create_graph_agent
from src.vectorstore import get_vector_store
from src.utils import get_logger

logger = get_logger(__name__)


async def main():
    """RAG 示例"""
    
    print("=" * 60)
    print("Fenq Super Agent - RAG 示例")
    print("=" * 60)
    print()
    
    # 创建向量存储
    print("📦 初始化向量存储...")
    vector_store = get_vector_store(collection_name="example_docs")
    
    # 准备示例文档
    documents = [
        Document(
            page_content="Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年发布。",
            metadata={"source": "python_intro", "category": "编程语言"},
        ),
        Document(
            page_content="LangChain 是一个用于开发由语言模型驱动的应用程序的框架。",
            metadata={"source": "langchain_intro", "category": "AI 框架"},
        ),
        Document(
            page_content="LangGraph 是 LangChain 的扩展，用于构建复杂的状态机和工作流。",
            metadata={"source": "langgraph_intro", "category": "AI 框架"},
        ),
        Document(
            page_content="FastAPI 是一个现代、快速的 Web 框架，用于构建 API。",
            metadata={"source": "fastapi_intro", "category": "Web 框架"},
        ),
        Document(
            page_content="Redis 是一个开源的内存数据库，常用于缓存和消息队列。",
            metadata={"source": "redis_intro", "category": "数据库"},
        ),
    ]
    
    # 添加文档到向量存储
    print("📝 添加文档到向量存储...")
    doc_ids = vector_store.add_documents(documents)
    print(f"✅ 成功添加 {len(doc_ids)} 个文档")
    print()
    
    # 测试检索
    queries = [
        "什么是 LangChain？",
        "Python 是什么时候发布的？",
        "Redis 的主要用途是什么？",
    ]
    
    print("🔍 测试向量检索:")
    print()
    
    for query in queries:
        print(f"查询: {query}")
        
        # 相似度搜索
        results = vector_store.similarity_search_with_score(query, k=2)
        
        print("检索结果:")
        for idx, (doc, score) in enumerate(results, 1):
            print(f"  {idx}. [相似度: {score:.4f}] {doc.page_content}")
        print()
    
    # 使用 Retriever 与 Agent 结合
    print("-" * 60)
    print("🤖 结合 Agent 进行 RAG 问答:")
    print()
    
    # 创建检索器
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # 创建自定义 RAG 工具
    from langchain_core.tools import tool
    
    @tool
    def search_knowledge_base(query: str) -> str:
        """在知识库中搜索相关信息"""
        docs = retriever.invoke(query)
        if not docs:
            return "未找到相关信息"
        
        result = "知识库中找到以下相关信息:\n\n"
        for idx, doc in enumerate(docs, 1):
            result += f"{idx}. {doc.page_content}\n"
            result += f"   来源: {doc.metadata.get('source', '未知')}\n\n"
        
        return result
    
    # 创建带 RAG 工具的 Agent
    agent = create_graph_agent(tools=[search_knowledge_base])
    
    # 测试问答
    questions = [
        "请告诉我关于 LangChain 和 LangGraph 的信息",
        "Python 和 FastAPI 分别是什么？",
    ]
    
    for question in questions:
        print(f"👤 用户: {question}")
        response = await agent.ainvoke(question)
        print(f"🤖 Agent: {response}")
        print()
        print("-" * 60)
        print()
    
    print("\n✅ RAG 示例完成！")


if __name__ == "__main__":
    asyncio.run(main())

