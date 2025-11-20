"""
MinIO数据访问
"""
from minio import Minio
from src.config import settings
from io import BytesIO
from typing import List, Dict, Optional, BinaryIO


class MyMinio:
    """MinIO数据访问"""
    
    def __init__(self):
        """初始化MinIO客户端"""
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False
        )
        self.bucket = settings.minio_bucket
        
        # 确保bucket存在
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """确保bucket存在，不存在则创建"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except Exception:
            # 如果创建失败，忽略错误（可能已经存在或权限问题）
            pass
    
    def bucket_exists(self) -> bool:
        """检查桶是否存在"""
        return self.client.bucket_exists(self.bucket)
    
    def list_objects(self, prefix: str = '', recursive: bool = False):
        """
        列出对象
        
        Args:
            prefix: 前缀
            recursive: 是否递归
            
        Returns:
            生成器，包含对象列表
        """
        return self.client.list_objects(self.bucket, prefix=prefix, recursive=recursive)
    
    def stat_object(self, object_name: str):
        """
        获取对象统计信息
        
        Args:
            object_name: 对象名称
            
        Returns:
            对象统计信息
        """
        return self.client.stat_object(self.bucket, object_name)
    
    def get_object(self, object_name: str):
        """
        获取对象
        
        Args:
            object_name: 对象名称
            
        Returns:
            对象响应
        """
        return self.client.get_object(self.bucket, object_name)
    
    def put_object(self, object_name: str, data: BinaryIO, length: int, content_type: str = 'application/octet-stream'):
        """
        上传对象
        
        Args:
            object_name: 对象名称
            data: 数据流
            length: 数据长度
            content_type: 内容类型
            
        Returns:
            上传结果
        """
        return self.client.put_object(
            self.bucket,
            object_name,
            data,
            length,
            content_type=content_type
        )
    
    def remove_object(self, object_name: str):
        """
        删除对象
        
        Args:
            object_name: 对象名称
        """
        self.client.remove_object(self.bucket, object_name)
    
    def create_directory(self, dir_path: str):
        """
        创建目录（通过上传空对象）
        
        Args:
            dir_path: 目录路径
        """
        if not dir_path.endswith('/'):
            dir_path += '/'
        
        self.client.put_object(
            self.bucket,
            dir_path,
            BytesIO(b''),
            0,
            content_type='application/x-directory'
        )
    
    def object_exists(self, object_name: str) -> bool:
        """
        检查对象是否存在
        
        Args:
            object_name: 对象名称
            
        Returns:
            是否存在
        """
        try:
            self.client.stat_object(self.bucket, object_name)
            return True
        except:
            return False

