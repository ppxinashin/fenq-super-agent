from sqlalchemy.ext.declarative import declarative_base
from typing import List
from langchain_core.documents import Document
from sqlalchemy import Column, create_engine, Engine, Text, JSON
from sqlalchemy.exc import ProgrammingError
from langchain_postgres import PGEngine, PGVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from src.config import settings
Base = declarative_base()

class RAGDocument(Base):
    __tablename__ = settings.vector_store_collection
    
    langchain_id = Column(Text, primary_key=True)
    content = Column(Text)
    embedding = Column(Vector(dim=1024))
    langchain_metadata = Column(JSON)
    
    def to_document(self) -> Document:
        return Document(page_content=str(self.content), metadata=self.langchain_metadata)

class PGVectorMemory:
    _engine: PGEngine = PGEngine.from_connection_string(
        url=settings.postgres_rag_connection_string
    )
    _engine_sql: Engine = create_engine(settings.postgres_rag_connection_string)
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
        except ProgrammingError as e:
            # 表已存在，跳过创建
            if "already exists" not in str(e):
                raise
        
        # 无论表是否已存在，都创建 vector store 实例
        cls._vector_store: PGVectorStore = PGVectorStore.create_sync(
            engine=cls._engine,
            table_name=settings.vector_store_collection,
            embedding_service=cls._embedding_service
        )
            
        return cls._vector_store
    
    @classmethod
    def get_all_documents(cls) -> List[Document]:
        """
        从向量存储中获取所有文档，用于初始化 BM25 检索器

        Returns:
            List[Document]: 所有文档的列表
        """
        with cls._engine_sql.connect() as conn:
            session = sessionmaker(bind=conn)()
            result = session.query(RAGDocument).all()
            return [row.to_document() for row in result]

