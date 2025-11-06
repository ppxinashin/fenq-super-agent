from langchain_core.documents import Document
import psycopg
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
    def get_vectore_store(cls) -> PGVectorStore:
        try:
            cls._engine.init_vectorstore_table(
                table_name=settings.vector_store_collection,
                vector_size=1024
            )
            cls._vector_store: PGVectorStore = PGVectorStore.create_sync(
                engine=cls._engine,
                table_name=settings.vector_store_collection,
                embedding_service=cls._embedding_service
            )
        except psycopg.errors.DuplicateTable as e:
            pass
            
        return cls._vector_store