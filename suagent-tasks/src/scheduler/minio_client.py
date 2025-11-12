"""
MinIO Client - MinIO 对象存储客户端
"""

import io
import logging
import mimetypes
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, BinaryIO
from minio import Minio
from minio.error import S3Error

from src.scheduler.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_SECURE,
    MINIO_MEMORY_BUCKET
)
from src.scheduler.utils.retry_handler import storage_retry

logger = logging.getLogger(__name__)

class MinIOClient:
    """MinIO 客户端封装"""

    def __init__(self):
        self.client = None
        self.bucket_name = MINIO_MEMORY_BUCKET
        self._initialize_client()

    def _initialize_client(self):
        """初始化 MinIO 客户端"""
        try:
            self.client = Minio(
                endpoint=MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE
            )
            logger.info(f"MinIO client initialized for endpoint: {MINIO_ENDPOINT}")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise

    @storage_retry
    def check_bucket_exists(self) -> bool:
        """
        检查存储桶是否存在

        Returns:
            存储桶是否存在
        """
        try:
            exists = self.client.bucket_exists(self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' exists: {exists}")
            return exists
        except S3Error as e:
            logger.error(f"Error checking bucket existence: {e}")
            raise

    @storage_retry
    def create_bucket(self):
        """创建存储桶"""
        try:
            if not self.check_bucket_exists():
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")

                # 设置存储桶策略（如果需要）
                self._set_bucket_policy()
            else:
                logger.info(f"Bucket '{self.bucket_name}' already exists")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise

    def _set_bucket_policy(self):
        """设置存储桶访问策略"""
        try:
            # 设置公共读取策略（根据实际需求调整）
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                    }
                ]
            }

            import json
            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
            logger.info(f"Set bucket policy for: {self.bucket_name}")

        except Exception as e:
            logger.warning(f"Failed to set bucket policy: {e}")

    @storage_retry
    def upload_file(
        self,
        user_id: str,
        filename: str,
        content: str,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传文件到 MinIO

        Args:
            user_id: 用户ID
            filename: 文件名
            content: 文件内容
            content_type: 内容类型

        Returns:
            上传结果信息
        """
        try:
            # 构建对象名称
            object_name = f"memory/{user_id}/{filename}"

            # 确定内容类型
            if content_type is None:
                content_type, _ = mimetypes.guess_type(filename)
                if content_type is None:
                    content_type = "text/markdown"

            # 将内容转换为字节流
            content_bytes = content.encode('utf-8')
            data_stream = io.BytesIO(content_bytes)

            # 设置元数据
            metadata = {
                "user-id": user_id,
                "upload-time": datetime.utcnow().isoformat(),
                "content-length": str(len(content_bytes)),
                "file-type": "memory-sync"
            }

            # 上传文件
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data_stream,
                length=len(content_bytes),
                content_type=content_type,
                metadata=metadata
            )

            upload_info = {
                "bucket": self.bucket_name,
                "object_name": object_name,
                "etag": result.etag,
                "size": len(content_bytes),
                "content_type": content_type,
                "upload_time": datetime.utcnow().isoformat(),
                "url": self._get_object_url(object_name)
            }

            logger.info(f"Successfully uploaded file: {object_name}")
            return upload_info

        except S3Error as e:
            logger.error(f"Error uploading file {filename}: {e}")
            raise

    @storage_retry
    def upload_file_from_path(
        self,
        user_id: str,
        file_path: str,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        从文件路径上传文件

        Args:
            user_id: 用户ID
            file_path: 本地文件路径
            filename: 目标文件名，默认为路径中的文件名

        Returns:
            上传结果信息
        """
        try:
            import os

            if filename is None:
                filename = os.path.basename(file_path)

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return self.upload_file(user_id, filename, content)

        except Exception as e:
            logger.error(f"Error uploading file from path {file_path}: {e}")
            raise

    @storage_retry
    def download_file(self, user_id: str, filename: str) -> str:
        """
        下载文件内容

        Args:
            user_id: 用户ID
            filename: 文件名

        Returns:
            文件内容
        """
        try:
            object_name = f"memory/{user_id}/{filename}"
            response = self.client.get_object(self.bucket_name, object_name)

            content = response.read().decode('utf-8')
            response.close()
            response.release_conn()

            logger.info(f"Successfully downloaded file: {object_name}")
            return content

        except S3Error as e:
            logger.error(f"Error downloading file {filename}: {e}")
            raise

    @storage_retry
    def file_exists(self, user_id: str, filename: str) -> bool:
        """
        检查文件是否存在

        Args:
            user_id: 用户ID
            filename: 文件名

        Returns:
            文件是否存在
        """
        try:
            object_name = f"memory/{user_id}/{filename}"
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

    @storage_retry
    def list_user_files(self, user_id: str, prefix: str = "") -> list:
        """
        列出用户文件

        Args:
            user_id: 用户ID
            prefix: 文件名前缀

        Returns:
            文件信息列表
        """
        try:
            object_prefix = f"memory/{user_id}/{prefix}"
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=object_prefix,
                recursive=True
            )

            files = []
            for obj in objects:
                file_info = {
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag,
                    "content_type": obj.content_type,
                    "filename": obj.object_name.replace(f"memory/{user_id}/", "")
                }
                files.append(file_info)

            return files

        except S3Error as e:
            logger.error(f"Error listing files for user {user_id}: {e}")
            raise

    @storage_retry
    def delete_file(self, user_id: str, filename: str) -> bool:
        """
        删除文件

        Args:
            user_id: 用户ID
            filename: 文件名

        Returns:
            是否删除成功
        """
        try:
            object_name = f"memory/{user_id}/{filename}"
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Successfully deleted file: {object_name}")
            return True

        except S3Error as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False

    def get_user_storage_stats(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户存储统计信息

        Args:
            user_id: 用户ID

        Returns:
            存储统计信息
        """
        try:
            files = self.list_user_files(user_id)

            total_files = len(files)
            total_size = sum(f['size'] for f in files)

            if files:
                oldest_file = min(f['last_modified'] for f in files)
                newest_file = max(f['last_modified'] for f in files)
            else:
                oldest_file = newest_file = None

            stats = {
                "user_id": user_id,
                "total_files": total_files,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "oldest_file": oldest_file,
                "newest_file": newest_file,
                "bucket": self.bucket_name
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting storage stats for user {user_id}: {e}")
            return {"error": str(e)}

    def _get_object_url(self, object_name: str) -> str:
        """
        获取对象访问URL

        Args:
            object_name: 对象名称

        Returns:
            访问URL
        """
        protocol = "https" if MINIO_SECURE else "http"
        return f"{protocol}://{MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"

    def generate_presigned_url(
        self,
        user_id: str,
        filename: str,
        expires: timedelta = timedelta(hours=1)
    ) -> Optional[str]:
        """
        生成预签名URL

        Args:
            user_id: 用户ID
            filename: 文件名
            expires: 过期时间

        Returns:
            预签名URL
        """
        try:
            object_name = f"memory/{user_id}/{filename}"
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=expires
            )
            return url

        except S3Error as e:
            logger.error(f"Error generating presigned URL for {filename}: {e}")
            return None