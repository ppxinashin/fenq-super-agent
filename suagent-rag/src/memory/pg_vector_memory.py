from langchain_core.documents import Document
import psycopg
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
        return f"{settings.vector_store_collection}_{agent_id}_{user_id}"
    
    @classmethod
    def get_vectore_store(cls, agent_id: str, user_id: str) -> PGVectorStore:
        try:
            cls._engine.init_vectorstore_table(
                table_name=cls._get_vectore_store_table_name(agent_id, user_id),
                vector_size=1024
            )
        except ProgrammingError as e:
            # 表已存在，跳过创建
            if "already exists" not in str(e):
                raise
        
        # 无论表是否已存在，都创建 vector store 实例
        cls._vector_store: PGVectorStore = PGVectorStore.create_sync(
            engine=cls._engine,
            table_name=cls._get_vectore_store_table_name(agent_id, user_id),
            embedding_service=cls._embedding_service
        )
            
        return cls._vector_store