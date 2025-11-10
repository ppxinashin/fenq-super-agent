from typing import List
from langchain_core.documents import Document
from sqlalchemy.exc import ProgrammingError
from langchain_postgres import PGEngine, PGVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
from src.config import settings

class PGVectorMemory:
    _engine: PGEngine = PGEngine.from_connection_string(
        url=settings.postgres_rag_connection_string
    )
    _embedding_service: DashScopeEmbeddings = DashScopeEmbeddings(
        model=settings.embedding_model,
        dashscope_api_key=settings.dashscope_api_key
    )
    
    @classmethod
    def _get_vectore_store_table_name(cls, agent_id: str, user_id: str) -> str:
        """
        生成向量存储表名
        
        Args:
            agent_id: 智能体ID
            user_id: 用户ID
            
        Returns:
            表名格式: {vector_store_collection}_{agent_id}_{user_id}
        """
        return f"{settings.vector_store_collection}_{agent_id}_{user_id}"
    
    @classmethod
    def get_vectore_store(cls, agent_id: str, user_id: str) -> PGVectorStore:
        """
        获取向量存储实例
        
        Args:
            agent_id: 智能体ID
            user_id: 用户ID
            
        Returns:
            PGVectorStore: 向量存储实例
        """
        table_name = cls._get_vectore_store_table_name(agent_id, user_id)
        
        try:
            cls._engine.init_vectorstore_table(
                table_name=table_name,
                vector_size=1024
            )
        except ProgrammingError as e:
            # 表已存在，跳过创建
            if "already exists" not in str(e):
                raise
        
        # 无论表是否已存在，都创建 vector store 实例
        cls._vector_store: PGVectorStore = PGVectorStore.create_sync(
            engine=cls._engine,
            table_name=table_name,
            embedding_service=cls._embedding_service
        )
            
        return cls._vector_store
    
    @classmethod
    def get_all_documents(cls, agent_id: str, user_id: str) -> List[Document]:
        """
        从向量存储中获取所有文档，用于初始化 BM25 检索器
        
        Args:
            agent_id: 智能体ID
            user_id: 用户ID

        Returns:
            List[Document]: 所有文档的列表
        """
        vector_store = cls.get_vectore_store(agent_id, user_id)
        # 使用 similarity_search 获取所有文档（使用空查询和大的 k 值）
        try:
            documents = vector_store.similarity_search("", k=10000)
            return documents
        except Exception:
            # 如果表不存在或为空，返回空列表
            return []

