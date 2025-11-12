"""
RAG文件查询相关响应模型
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class RAGFileListResponse(BaseModel):
    """RAG文件列表响应模型"""
    
    source: str = Field(..., description="文件路径")
    minio_bucket: Optional[str] = Field(None, description="MinIO桶名")
    content_type: Optional[str] = Field(None, description="文件类型")
    total_chunks: int = Field(..., description="总分块数")
    agent_id: str = Field(..., description="智能体ID")
    user_id: str = Field(..., description="用户ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "football/admin/足球知识详细教程文档四：数据解读.md",
                "minio_bucket": "suagent",
                "content_type": "text/markdown",
                "total_chunks": 5,
                "agent_id": "football",
                "user_id": "admin"
            }
        }


class RAGFileChunkResponse(BaseModel):
    """RAG文件分块响应模型"""
    
    langchain_id: str = Field(..., description="唯一标识")
    chunk_index: int = Field(..., description="分块编号")
    content: str = Field(..., description="分块内容")
    content_length: int = Field(..., description="分块内容长度")
    metadata: Dict[str, Any] = Field(..., description="完整元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "langchain_id": "550e8400-e29b-41d4-a716-446655440000",
                "chunk_index": 0,
                "content": "这是第一块内容...",
                "content_length": 1024,
                "metadata": {
                    "source": "football/admin/足球知识详细教程文档四：数据解读.md",
                    "minio_bucket": "suagent",
                    "chunk_index": 0,
                    "total_chunks": 5,
                    "content_type": "text/markdown",
                    "agent_id": "football",
                    "user_id": "admin"
                }
            }
        }


class RAGFileSummaryResponse(BaseModel):
    """RAG文件摘要响应模型"""
    
    source: str = Field(..., description="文件路径")
    total_chunks: int = Field(..., description="总分块数")
    total_content_length: int = Field(..., description="所有分块内容总长度")
    minio_bucket: Optional[str] = Field(None, description="MinIO桶名")
    content_type: Optional[str] = Field(None, description="内容类型")
    agent_id: str = Field(..., description="智能体ID")
    user_id: str = Field(..., description="用户ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "football/admin/足球知识详细教程文档四：数据解读.md",
                "total_chunks": 5,
                "total_content_length": 5120,
                "minio_bucket": "suagent",
                "content_type": "text/markdown",
                "agent_id": "football",
                "user_id": "admin"
            }
        }


class RAGFileChunkSimpleResponse(BaseModel):
    """RAG文件分块简要响应模型（不含完整内容）"""
    
    chunk_index: int = Field(..., description="分块编号")
    content_length: int = Field(..., description="分块内容长度")
    content_preview: str = Field(..., description="内容预览（前100字符）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunk_index": 0,
                "content_length": 1024,
                "content_preview": "这是第一块内容的预览..."
            }
        }

