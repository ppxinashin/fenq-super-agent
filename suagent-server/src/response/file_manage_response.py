"""
文件管理响应模型
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_path: str = Field(..., description="文件在MinIO中的路径")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    content_type: str = Field(..., description="文件类型")
    message: str = Field(default="文件上传成功", description="消息")


class FileInfo(BaseModel):
    """文件信息"""
    source: str = Field(..., description="文件路径")
    file_name: str = Field(..., description="文件名")
    content_type: Optional[str] = Field(None, description="文件类型")
    minio_bucket: Optional[str] = Field(None, description="MinIO桶名")
    total_chunks: int = Field(default=0, description="分块总数")
    status: str = Field(default="已上传", description="文件状态")
    author: Optional[str] = Field(None, description="作者")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class FileListResponse(BaseModel):
    """文件列表响应"""
    files: List[FileInfo] = Field(default_factory=list, description="文件列表")
    total: int = Field(default=0, description="总数")


class ChunkInfo(BaseModel):
    """分块信息"""
    chunk_index: int = Field(..., description="分块索引")
    content: str = Field(..., description="分块内容")
    content_length: int = Field(..., description="内容长度")


class FileChunksResponse(BaseModel):
    """文件分块响应"""
    source: str = Field(..., description="文件路径")
    file_name: str = Field(..., description="文件名")
    total_chunks: int = Field(..., description="分块总数")
    chunks: List[ChunkInfo] = Field(default_factory=list, description="分块列表")


class FileDeleteResponse(BaseModel):
    """文件删除响应"""
    source: str = Field(..., description="文件路径")
    deleted: bool = Field(..., description="是否删除成功")
    message: str = Field(default="文件删除成功", description="消息")


class FileDeleteResult(BaseModel):
    """单个文件删除结果"""
    source: str = Field(..., description="文件路径")
    success: bool = Field(..., description="是否成功")
    message: Optional[str] = Field(None, description="消息")


class FileBatchDeleteResponse(BaseModel):
    """批量删除响应"""
    total: int = Field(..., description="总文件数")
    success_count: int = Field(..., description="成功删除数量")
    failed_count: int = Field(..., description="失败删除数量")
    results: List[FileDeleteResult] = Field(default_factory=list, description="每个文件的删除结果")

