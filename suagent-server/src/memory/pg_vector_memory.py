from typing import List, Dict, Any
from langchain_core.documents import Document
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import text, create_engine
from langchain_postgres import PGEngine, PGVectorStore
from langchain_community.embeddings import DashScopeEmbeddings
from src.config import settings

class PGVectorMemory:
    _engine: PGEngine = PGEngine.from_connection_string(
        url=settings.postgres_rag_connection_string
    )
    _sqlalchemy_engine = create_engine(settings.postgres_rag_connection_string)
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
    
    @classmethod
    def get_all_files(cls, agent_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        获取指定agent_id和user_id下的所有文件列表
        
        Args:
            agent_id: 智能体ID
            user_id: 用户ID
            
        Returns:
            List[Dict[str, Any]]: 文件列表，每个文件包含source和total_chunks等信息
        """
        table_name = cls._get_vectore_store_table_name(agent_id, user_id)
        
        query = text(f"""
            SELECT DISTINCT
                langchain_metadata->>'source' as source,
                langchain_metadata->>'minio_bucket' as minio_bucket,
                langchain_metadata->>'content_type' as content_type,
                COUNT(*) as total_chunks
            FROM "{table_name}"
            WHERE langchain_metadata->>'source' IS NOT NULL
            GROUP BY 
                langchain_metadata->>'source',
                langchain_metadata->>'minio_bucket',
                langchain_metadata->>'content_type'
            ORDER BY langchain_metadata->>'source'
        """)
        
        try:
            with cls._sqlalchemy_engine.connect() as conn:
                result = conn.execute(query)
                files = []
                for row in result:
                    files.append({
                        "source": row[0],
                        "minio_bucket": row[1],
                        "content_type": row[2],
                        "total_chunks": row[3]
                    })
                return files
        except Exception as e:
            # 如果表不存在，返回空列表
            return []
    
    @classmethod
    def get_file_chunks(cls, agent_id: str, user_id: str, source: str) -> Dict[str, Any]:
        """
        根据文件名查询该文件的所有分块信息
        
        Args:
            agent_id: 智能体ID
            user_id: 用户ID
            source: 文件路径（source字段）
            
        Returns:
            Dict[str, Any]: 包含文件信息和所有分块的详细信息
            {
                "source": "文件路径",
                "total_chunks": 总分块数,
                "chunks": [
                    {
                        "chunk_index": 分块索引,
                        "content": 分块内容,
                        "content_length": 内容长度
                    },
                    ...
                ]
            }
        """
        table_name = cls._get_vectore_store_table_name(agent_id, user_id)
        
        query = text(f"""
            SELECT 
                langchain_metadata->>'source' as source,
                langchain_metadata->>'chunk_index' as chunk_index,
                langchain_metadata->>'total_chunks' as total_chunks,
                content,
                LENGTH(content) as content_length
            FROM "{table_name}"
            WHERE langchain_metadata->>'source' = :source
            ORDER BY (langchain_metadata->>'chunk_index')::int
        """)
        
        try:
            with cls._sqlalchemy_engine.connect() as conn:
                result = conn.execute(query, {"source": source})
                rows = result.fetchall()
                
                if not rows:
                    return {
                        "source": source,
                        "total_chunks": 0,
                        "chunks": []
                    }
                
                chunks = []
                total_chunks = 0
                file_source = source  # 默认值，防止未绑定错误
                
                for row in rows:
                    file_source = row[0]
                    chunk_index = int(row[1]) if row[1] is not None else 0
                    total_chunks = int(row[2]) if row[2] is not None else 0
                    content = row[3]
                    content_length = row[4]
                    
                    chunks.append({
                        "chunk_index": chunk_index,
                        "content": content,
                        "content_length": content_length
                    })
                
                return {
                    "source": file_source,
                    "total_chunks": total_chunks,
                    "chunks": chunks
                }
        except Exception as e:
            # 如果表不存在或查询失败，返回空结果
            return {
                "source": source,
                "total_chunks": 0,
                "chunks": []
            }

