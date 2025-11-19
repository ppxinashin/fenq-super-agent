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
    FileChunksResponse, ChunkInfo, FileDeleteResponse,
    FileBatchDeleteResponse, FileDeleteResult
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
        page_size: int = 20,
        keyword: Optional[str] = None
    ):
        """
        从MinIO获取文件列表

        Args:
            agent_id: 智能体ID
            username: 用户名
            page: 页码
            page_size: 每页数量
            keyword: 关键词搜索（可选）

        Returns:
            分页响应数据

        Raises:
            Exception: 查询失败时抛出异常
        """
        try:
            # 构建搜索前缀
            prefix = f"{agent_id}/{username}/"

            # 从MinIO获取文件列表
            objects = list(self.minio_client.list_objects(prefix=prefix, recursive=True))

            # 过滤掉目录对象（以/结尾的空对象）
            file_objects = [obj for obj in objects if not obj.object_name.endswith('/')]

            # 获取PGVector中的文件信息（用于分块状态等）
            pg_files = {}
            try:
                pg_file_list = PGVectorMemory.get_all_files(agent_id=agent_id, user_id=username)
                for pg_file in pg_file_list:
                    pg_files[pg_file.get("source", "")] = pg_file
            except Exception as e:
                logger.warning(f"获取PGVector文件信息失败: {e}")

            # 构建文件信息列表
            file_infos = []
            for obj in file_objects:
                object_name = obj.object_name
                file_name = os.path.basename(object_name)

                # 关键词过滤
                if keyword and keyword.lower() not in file_name.lower():
                    continue

                # 获取PGVector文件信息
                pg_file = pg_files.get(object_name, {})

                # 确定文件状态
                status = "已处理" if pg_file.get("total_chunks", 0) > 0 else "处理中"

                file_info = {
                    "source": object_name,
                    "file_name": file_name,
                    "content_type": pg_file.get("content_type") or "application/octet-stream",
                    "minio_bucket": self.minio_client.bucket,
                    "total_chunks": pg_file.get("total_chunks", 0),
                    "status": status,
                    "author": username,
                    "file_size": obj.size,
                    "created_at": obj.last_modified,
                    "updated_at": obj.last_modified
                }
                file_infos.append(file_info)

            # 按创建时间倒序排列
            file_infos.sort(key=lambda x: x["created_at"], reverse=True)

            # 分页处理
            total = len(file_infos)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_files = file_infos[start_idx:end_idx]

            logger.info(f"从MinIO获取文件列表成功: agent_id={agent_id}, user={username}, total={total}")

            # 返回分页数据
            from src.response.pageable import create_pageable
            return create_pageable(
                page=page,
                page_size=page_size,
                total=total,
                data=paginated_files
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

    def batch_delete_files(
        self,
        agent_id: str,
        username: str,
        sources: list[str]
    ) -> FileBatchDeleteResponse:
        """
        批量删除文件

        Args:
            agent_id: 智能体ID
            username: 用户名
            sources: 文件路径列表

        Returns:
            FileBatchDeleteResponse: 批量删除结果

        Raises:
            Exception: 删除失败时抛出异常
        """
        results = []
        success_count = 0
        failed_count = 0

        logger.info(f"开始批量删除文件: agent_id={agent_id}, user={username}, count={len(sources)}")

        for source in sources:
            try:
                # 删除单个文件
                self.minio_client.remove_object(source)
                
                results.append(FileDeleteResult(
                    source=source,
                    success=True,
                    message="删除成功"
                ))
                success_count += 1
                logger.info(f"文件删除成功: {source}")

            except S3Error as e:
                results.append(FileDeleteResult(
                    source=source,
                    success=False,
                    message=f"MinIO删除失败: {str(e)}"
                ))
                failed_count += 1
                logger.error(f"文件删除失败 (MinIO): {source}, error={e}")

            except Exception as e:
                results.append(FileDeleteResult(
                    source=source,
                    success=False,
                    message=f"删除异常: {str(e)}"
                ))
                failed_count += 1
                logger.error(f"文件删除失败 (异常): {source}, error={e}")

        logger.info(f"批量删除完成: total={len(sources)}, success={success_count}, failed={failed_count}")

        return FileBatchDeleteResponse(
            total=len(sources),
            success_count=success_count,
            failed_count=failed_count,
            results=results
        )


# 创建服务实例
file_manage_service = FileManageService()

