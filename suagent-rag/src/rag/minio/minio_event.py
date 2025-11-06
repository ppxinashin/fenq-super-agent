"""
MinIO 事件监听和向量化存储
"""
import json
import os
from typing import List, Optional
from io import BytesIO
import psycopg
from psycopg import sql

from src.memory import PGVectorMemory
from langchain_core.documents import Document

from src.config import settings
from src.rag.minio.my_minio import MyMinio
from src.rag.chunker import (
    Chunker,
    PDFChunker,
    MarkdownChunker,
    OfficeChunker,
    JSONChunker,
    PureTextChunker,
    OCRChunker,
)
from src.utils import get_logger


class MinioEventListener:
    """MinIO 事件监听器"""
    
    def __init__(self):
        """初始化事件监听器"""
        self.logger = get_logger(__name__)
        self.minio_client = MyMinio()
        self.vector_store = PGVectorMemory.get_vectore_store()
        
        # 初始化所有 chunker
        self.chunkers: List[Chunker] = [
            OCRChunker(),  # OCR优先，支持需要OCR的各种格式
            PDFChunker(),
            MarkdownChunker(),
            OfficeChunker(),
            JSONChunker(),
            PureTextChunker(),
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
                if chunker.__class__.__name__ == "OCRChunker" and not settings.open_ocr:
                    continue
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
            
            chunckerType = chunker.__class__.__name__
            self.logger.info(f"使用 chunker: {chunckerType}")
            
            # 从 MinIO 下载文件数据
            response = self.minio_client.get_object(object_name)
            file_data = response.read()
            
            # 使用 chunker 分块
            self.logger.info(f"开始分块处理")
            if chunckerType != "OCRChunker":
                chunks = chunker.chunk(file_data)
            else:
                chunks = chunker.chunk(f'http://{settings.minio_endpoint}/{settings.minio_bucket}/{object_name}'.encode('utf-8'))
            
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
            self.vector_store.add_documents(documents=documents)
            self.logger.info(f"文档处理完成: {object_name}, 共 {len(documents)} 个文档块")
            
        except Exception as e:
            self.logger.error(f"处理文档时出错 {object_name}: {str(e)}", exc_info=True)
            raise
    
    def delete_document(self, object_name: str):
        """
        删除文档的向量索引
        
        Args:
            object_name: MinIO 对象名称
        """
        try:
            self.logger.info(f"开始删除文档索引: {object_name}")
            
            # 获取表名
            table_name = settings.vector_store_collection
            
            # 使用 psycopg 连接执行删除操作
            with psycopg.connect(settings.postgres_rag_connection_string) as conn:
                with conn.cursor() as cur:
                    # 使用 sql.SQL 构建查询以避免 SQL 注入并满足类型检查
                    query = sql.SQL("DELETE FROM {} WHERE metadata->>'source' = %s").format(
                        sql.Identifier(table_name)
                    )
                    cur.execute(query, (object_name,))
                    deleted_count = cur.rowcount
                    conn.commit()
                
            self.logger.info(f"文档索引删除完成: {object_name}, 共删除 {deleted_count} 条记录")
            
        except Exception as e:
            self.logger.error(f"删除文档索引时出错 {object_name}: {str(e)}", exc_info=True)
            raise
    
    def delete_documents_batch(self, object_names: List[str]):
        """
        批量删除文档的向量索引（一次数据库连接处理多个删除）
        
        Args:
            object_names: MinIO 对象名称列表
        """
        if not object_names:
            return
            
        try:
            self.logger.info(f"开始批量删除文档索引，共 {len(object_names)} 个文档")
            
            # 获取表名
            table_name = settings.vector_store_collection
            
            # 使用一个数据库连接批量删除
            with psycopg.connect(settings.postgres_rag_connection_string.replace('+psycopg','')) as conn:
                with conn.cursor() as cur:
                    total_deleted = 0
                    for object_name in object_names:
                        query = sql.SQL("DELETE FROM {} WHERE langchain_metadata->>'source' = %s").format(
                            sql.Identifier(table_name)
                        )
                        cur.execute(query, (object_name,))
                        deleted_count = cur.rowcount
                        total_deleted += deleted_count
                        self.logger.info(f"删除文档索引: {object_name}, 删除 {deleted_count} 条记录")
                    
                    conn.commit()
                
            self.logger.info(f"批量删除完成，共删除 {total_deleted} 条记录")
            
        except Exception as e:
            self.logger.error(f"批量删除文档索引时出错: {str(e)}", exc_info=True)
            raise
    
    def listen_events(self, prefix: str = ''):
        """
        监听 MinIO 桶的事件
        
        Args:
            prefix: 对象前缀过滤
        """
        self.logger.info(f"开始监听 MinIO 事件，桶: {self.minio_client.bucket}, 前缀: {prefix or '(所有)'}")
        
        try:
            # 监听桶通知事件（包括创建和删除事件）
            events = self.minio_client.client.listen_bucket_notification(
                bucket_name=self.minio_client.bucket,
                prefix=prefix,
                events=("s3:ObjectCreated:*", "s3:ObjectRemoved:*")
            )
            
            self.logger.info("事件监听已启动，等待事件触发...")
            
            for event_data in events:
                try:
                    # 收集需要删除的对象列表（批量处理）
                    objects_to_delete = []
                    
                    # 处理每个记录
                    for record in event_data.get('Records', []):
                        event_name = record.get('eventName', '')
                        s3_info = record.get('s3', {})
                        object_info = s3_info.get('object', {})
                        object_name = object_info.get('key', '')
                        
                        if not object_name:
                            continue
                        
                        # 处理对象创建事件
                        if event_name.startswith('s3:ObjectCreated:'):
                            self.logger.info(f"\n检测到新对象创建: {object_name}")
                            self.logger.info(f"事件类型: {event_name}")
                            
                            # 处理文档
                            self.process_document(object_name)
                        
                        # 处理对象删除事件
                        elif event_name.startswith('s3:ObjectRemoved:'):
                            self.logger.info(f"\n检测到对象删除: {object_name}")
                            self.logger.info(f"事件类型: {event_name}")
                            
                            # 收集待删除的对象
                            objects_to_delete.append(object_name)
                    
                    # 批量删除文档索引（避免循环创建数据库连接）
                    if objects_to_delete:
                        self.delete_documents_batch(objects_to_delete)
                            
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
