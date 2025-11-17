"""
文件管理服务层
"""

import os
from typing import Optional, BinaryIO
from datetime import datetime
from io import BytesIO
from minio.error import S3Error
from src.minio_client.my_minio import MyMinio
from src.memory.pg_vector_memory import PGVectorMemory
from src.response.file_manage_response import (
    FileUploadResponse, FileInfo, FileListResponse,
    FileChunksResponse, ChunkInfo, FileDeleteResponse
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FileManageService:
    """文件管理服务类"""

    def __init__(self):
        self.minio_client = MyMinio()

    def upload_file(
        self,
        file_data: BinaryIO,
        file_name: str,
        file_size: int,
        content_type: str,
        agent_id: str,
        username: str
    ) -> FileUploadResponse:
        """
        上传文件到MinIO

        Args:
            file_data: 文件数据流
            file_name: 文件名
            file_size: 文件大小
            content_type: 文件类型
            agent_id: 智能体ID
            username: 用户名

        Returns:
            FileUploadResponse: 上传结果

        Raises:
            Exception: 上传失败时抛出异常
        """
        try:
            # 构建文件路径: agent_id/username/filename
            file_path = f"{agent_id}/{username}/{file_name}"

            # 检查目录是否存在，不存在则创建
            dir_path = f"{agent_id}/{username}/"
            if not self.minio_client.object_exists(dir_path):
                logger.info(f"创建目录: {dir_path}")
                self.minio_client.create_directory(dir_path)

            # 上传文件
            logger.info(f"开始上传文件: {file_path}, 大小: {file_size} bytes")
            result = self.minio_client.put_object(
                object_name=file_path,
                data=file_data,
                length=file_size,
                content_type=content_type
            )

            logger.info(f"文件上传成功: {file_path}, etag={result.etag}")

            return FileUploadResponse(
                file_path=file_path,
                file_name=file_name,
                file_size=file_size,
                content_type=content_type
            )

        except S3Error as e:
            logger.error(f"MinIO上传失败: {e}")
            raise Exception(f"文件上传失败: {str(e)}")
        except Exception as e:
            logger.error(f"文件上传异常: {e}")
            raise

    def get_file_list(
        self,
        agent_id: str,
        username: str,
        page: int = 1,
        page_size: int = 20
    ) -> FileListResponse:
        """
        获取文件列表

        Args:
            agent_id: 智能体ID
            username: 用户名
            page: 页码
            page_size: 每页数量

        Returns:
            FileListResponse: 文件列表

        Raises:
            Exception: 查询失败时抛出异常
        """
        try:
            # 从PGVector获取文件列表（包含分块信息）
            pg_files = PGVectorMemory.get_all_files(agent_id=agent_id, user_id=username)

            # 构建文件信息列表
            file_infos = []
            for pg_file in pg_files:
                source = pg_file.get("source", "")
                file_name = os.path.basename(source)

                # 获取MinIO中的文件信息（用于获取创建时间等）
                minio_info = None
                try:
                    minio_info = self.minio_client.stat_object(source)
                except Exception as e:
                    logger.warning(f"无法获取MinIO文件信息: {source}, error={e}")

                # 确定文件状态
                status = "已处理" if pg_file.get("total_chunks", 0) > 0 else "处理中"

                file_info = FileInfo(
                    source=source,
                    file_name=file_name,
                    content_type=pg_file.get("content_type"),
                    minio_bucket=pg_file.get("minio_bucket"),
                    total_chunks=pg_file.get("total_chunks", 0),
                    status=status,
                    author=username,
                    created_at=minio_info.last_modified if minio_info else None,
                    updated_at=minio_info.last_modified if minio_info else None
                )
                file_infos.append(file_info)

            # 分页处理
            total = len(file_infos)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_files = file_infos[start_idx:end_idx]

            logger.info(f"获取文件列表成功: agent_id={agent_id}, user={username}, total={total}")

            return FileListResponse(
                files=paginated_files,
                total=total
            )

        except Exception as e:
            logger.error(f"获取文件列表失败: {e}")
            raise

    def get_file_chunks(
        self,
        agent_id: str,
        username: str,
        source: str
    ) -> FileChunksResponse:
        """
        获取文件分块详情

        Args:
            agent_id: 智能体ID
            username: 用户名
            source: 文件路径

        Returns:
            FileChunksResponse: 文件分块信息

        Raises:
            Exception: 查询失败时抛出异常
        """
        try:
            # 从PGVector获取文件分块信息
            chunks_data = PGVectorMemory.get_file_chunks(
                agent_id=agent_id,
                user_id=username,
                source=source
            )

            if not chunks_data or chunks_data.get("total_chunks", 0) == 0:
                raise ValueError(f"文件不存在或未分块: {source}")

            # 构建分块信息列表
            chunk_infos = [
                ChunkInfo(
                    chunk_index=chunk["chunk_index"],
                    content=chunk["content"],
                    content_length=chunk["content_length"]
                )
                for chunk in chunks_data.get("chunks", [])
            ]

            file_name = os.path.basename(source)

            logger.info(f"获取文件分块成功: source={source}, chunks={len(chunk_infos)}")

            return FileChunksResponse(
                source=source,
                file_name=file_name,
                total_chunks=chunks_data.get("total_chunks", 0),
                chunks=chunk_infos
            )

        except Exception as e:
            logger.error(f"获取文件分块失败: {e}")
            raise

    def delete_file(
        self,
        agent_id: str,
        username: str,
        source: str
    ) -> FileDeleteResponse:
        """
        删除文件

        Args:
            agent_id: 智能体ID
            username: 用户名
            source: 文件路径

        Returns:
            FileDeleteResponse: 删除结果

        Raises:
            Exception: 删除失败时抛出异常
        """
        try:
            # 删除MinIO中的文件
            logger.info(f"开始删除MinIO文件: {source}")
            self.minio_client.remove_object(source)

            logger.info(f"文件删除成功: {source}")

            return FileDeleteResponse(
                source=source,
                deleted=True
            )

        except S3Error as e:
            logger.error(f"MinIO删除失败: {e}")
            raise Exception(f"文件删除失败: {str(e)}")
        except Exception as e:
            logger.error(f"文件删除异常: {e}")
            raise


# 创建服务实例
file_manage_service = FileManageService()

