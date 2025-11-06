"""
MinIO 事件监听和向量化存储
"""
import json
import os
from typing import List, Optional
from io import BytesIO

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document

from src.config import settings
from src.rag.minio.my_minio import MyMinio
from src.rag.chunker import (
    Chunker,
    PDFChunker,
    MarkdownChunker,
    OfficeChunker,
    JSONChunker,
)
from src.utils import get_logger


class MinioEventListener:
    """MinIO 事件监听器"""
    
    def __init__(self):
        """初始化事件监听器"""
        self.logger = get_logger(__name__)
        self.minio_client = MyMinio()
        self.embeddings = DashScopeEmbeddings(
            model=settings.embedding_model,
            dashscope_api_key=settings.dashscope_api_key
        )
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            connection=settings.postgres_rag_connection_string,
            collection_name=settings.vector_store_collection,
        )
        
        # 初始化所有 chunker
        self.chunkers: List[Chunker] = [
            PDFChunker(),
            MarkdownChunker(),
            OfficeChunker(),
            JSONChunker(),
        ]
    
    def get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(filename)[1].lower()
    
    def get_content_type(self, filename: str) -> str:
        """
        根据文件扩展名获取 content_type
        
        Args:
            filename: 文件名
            
        Returns:
            content_type
        """
        ext = self.get_file_extension(filename)
        content_type_mapping = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        }
        return content_type_mapping.get(ext, 'application/octet-stream')
    
    def get_chunker(self, content_type: str) -> Optional[Chunker]:
        """
        根据内容类型获取合适的 chunker
        
        Args:
            content_type: 内容类型
            
        Returns:
            Chunker 实例或 None
        """
        for chunker in self.chunkers:
            if chunker.supports(content_type):
                return chunker
        return None
    
    def process_document(self, object_name: str):
        """
        处理文档：下载、加载、分割、向量化、存储
        
        Args:
            object_name: MinIO 对象名称
        """
        try:
            self.logger.info(f"开始处理文档: {object_name}")
            
            # 获取文件的 content_type
            content_type = self.get_content_type(object_name)
            
            # 获取合适的 chunker
            chunker = self.get_chunker(content_type)
            if chunker is None:
                self.logger.warning(f"跳过不支持的文件类型: {content_type} - {object_name}")
                return
            
            self.logger.info(f"使用 chunker: {chunker.__class__.__name__}")
            
            # 从 MinIO 下载文件数据
            response = self.minio_client.get_object(object_name)
            file_data = response.read()
            
            # 使用 chunker 分块
            self.logger.info(f"开始分块处理")
            chunks = chunker.chunk(file_data)
            
            if not chunks:
                self.logger.warning(f"文档分块结果为空: {object_name}")
                return
            
            self.logger.info(f"分块完成，共 {len(chunks)} 个文档块")
            
            # 将文本块转换为 Document 对象
            documents = []
            for i, chunk_text in enumerate(chunks):
                doc = Document(
                    page_content=chunk_text,
                    metadata={
                        'source': object_name,
                        'minio_bucket': self.minio_client.bucket,
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'content_type': content_type,
                    }
                )
                documents.append(doc)
            
            # 存储到向量数据库
            self.logger.info(f"开始向量化并存储到数据库")
            self.vector_store.add_documents(documents)
            self.logger.info(f"文档处理完成: {object_name}, 共 {len(documents)} 个文档块")
            
        except Exception as e:
            self.logger.error(f"处理文档时出错 {object_name}: {str(e)}", exc_info=True)
            raise
    
    def listen_events(self, prefix: str = ''):
        """
        监听 MinIO 桶的事件
        
        Args:
            prefix: 对象前缀过滤
        """
        self.logger.info(f"开始监听 MinIO 事件，桶: {self.minio_client.bucket}, 前缀: {prefix or '(所有)'}")
        
        try:
            # 监听桶通知事件
            events = self.minio_client.client.listen_bucket_notification(
                bucket_name=self.minio_client.bucket,
                prefix=prefix,
                events=("s3:ObjectCreated:*",)
            )
            
            self.logger.info("事件监听已启动，等待事件触发...")
            
            for event in events:
                try:
                    # 解析事件数据
                    event_data = json.loads(event)
                    
                    # 处理每个记录
                    for record in event_data.get('Records', []):
                        event_name = record.get('eventName', '')
                        
                        # 只处理对象创建事件
                        if event_name.startswith('s3:ObjectCreated:'):
                            s3_info = record.get('s3', {})
                            object_info = s3_info.get('object', {})
                            object_name = object_info.get('key', '')
                            
                            if object_name:
                                self.logger.info(f"\n检测到新对象创建: {object_name}")
                                self.logger.info(f"事件类型: {event_name}")
                                
                                # 处理文档
                                self.process_document(object_name)
                            
                except json.JSONDecodeError as e:
                    self.logger.error(f"解析事件数据失败: {str(e)}")
                except Exception as e:
                    self.logger.error(f"处理事件时出错: {str(e)}", exc_info=True)
                    
        except KeyboardInterrupt:
            self.logger.info("\n事件监听已停止")
        except Exception as e:
            self.logger.error(f"监听事件时出错: {str(e)}", exc_info=True)
            raise


def start_event_listener(prefix: str = ''):
    """
    启动事件监听器
    
    Args:
        prefix: 对象前缀过滤
    """
    listener = MinioEventListener()
    listener.listen_events(prefix=prefix)


if __name__ == "__main__":
    # 启动事件监听
    start_event_listener()