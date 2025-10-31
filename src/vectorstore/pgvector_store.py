"""
PGVector 向量存储 - 使用 PostgreSQL + PGVector 实现 RAG
"""

from typing import List, Optional, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)


class PGVectorStore:
    """PGVector 向量存储封装类"""

    def __init__(
        self,
        collection_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ):
        """
        初始化 PGVector 存储
        
        Args:
            collection_name: 集合名称
            embedding_model: 嵌入模型名称
        """
        self.collection_name = collection_name or settings.vector_store_collection
        self.embedding_model = embedding_model or settings.embedding_model
        
        logger.info(f"初始化 PGVector 存储，集合: {self.collection_name}")
        
        # 创建嵌入模型
        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            api_key=settings.openai_api_key,
        )
        
        # 创建向量存储
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=settings.postgres_connection_string,
            use_jsonb=True,
        )
        
        logger.info("PGVector 存储初始化完成")

    def add_documents(
        self,
        documents: List[Document],
        **kwargs: Any,
    ) -> List[str]:
        """
        添加文档到向量存储
        
        Args:
            documents: 文档列表
            **kwargs: 其他参数
        
        Returns:
            文档 ID 列表
        """
        try:
            logger.info(f"添加 {len(documents)} 个文档到向量存储")
            ids = self.vector_store.add_documents(documents, **kwargs)
            logger.info(f"成功添加 {len(ids)} 个文档")
            return ids
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            raise

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """
        添加文本到向量存储
        
        Args:
            texts: 文本列表
            metadatas: 元数据列表
            **kwargs: 其他参数
        
        Returns:
            文档 ID 列表
        """
        try:
            logger.info(f"添加 {len(texts)} 条文本到向量存储")
            ids = self.vector_store.add_texts(texts, metadatas, **kwargs)
            logger.info(f"成功添加 {len(ids)} 条文本")
            return ids
        except Exception as e:
            logger.error(f"添加文本失败: {str(e)}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        **kwargs: Any,
    ) -> List[Document]:
        """
        相似度搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            **kwargs: 其他参数
        
        Returns:
            相关文档列表
        """
        try:
            logger.info(f"执行相似度搜索: {query[:50]}...")
            results = self.vector_store.similarity_search(query, k=k, **kwargs)
            logger.info(f"找到 {len(results)} 个相关文档")
            return results
        except Exception as e:
            logger.error(f"相似度搜索失败: {str(e)}")
            raise

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        **kwargs: Any,
    ) -> List[tuple[Document, float]]:
        """
        相似度搜索（带分数）
        
        Args:
            query: 查询文本
            k: 返回结果数量
            **kwargs: 其他参数
        
        Returns:
            (文档, 相似度分数) 元组列表
        """
        try:
            logger.info(f"执行相似度搜索（带分数）: {query[:50]}...")
            results = self.vector_store.similarity_search_with_score(query, k=k, **kwargs)
            logger.info(f"找到 {len(results)} 个相关文档")
            return results
        except Exception as e:
            logger.error(f"相似度搜索失败: {str(e)}")
            raise

    def delete(self, ids: List[str]) -> None:
        """
        删除文档
        
        Args:
            ids: 文档 ID 列表
        """
        try:
            logger.info(f"删除 {len(ids)} 个文档")
            self.vector_store.delete(ids)
            logger.info("文档删除成功")
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}")
            raise

    def as_retriever(self, **kwargs: Any):
        """
        转换为 Retriever
        
        Args:
            **kwargs: Retriever 参数
        
        Returns:
            VectorStoreRetriever 实例
        """
        return self.vector_store.as_retriever(**kwargs)


def get_vector_store(
    collection_name: Optional[str] = None,
    embedding_model: Optional[str] = None,
) -> PGVectorStore:
    """
    获取向量存储实例
    
    Args:
        collection_name: 集合名称
        embedding_model: 嵌入模型名称
    
    Returns:
        PGVectorStore 实例
    """
    return PGVectorStore(
        collection_name=collection_name,
        embedding_model=embedding_model,
    )

