"""
文件管理请求模型
"""

from typing import Optional
from pydantic import BaseModel, Field


class FileListRequest(BaseModel):
    """文件列表查询请求"""
    agent_id: str = Field(..., description="智能体ID")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "my_agent",
                "page": 1,
                "page_size": 20
            }
        }


class FileChunksRequest(BaseModel):
    """文件分块查询请求"""
    agent_id: str = Field(..., description="智能体ID")
    source: str = Field(..., description="文件路径")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "my_agent",
                "source": "document.pdf"
            }
        }


class FileDeleteRequest(BaseModel):
    """文件删除请求"""
    agent_id: str = Field(..., description="智能体ID")
    source: str = Field(..., description="文件路径")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "my_agent",
                "source": "document.pdf"
            }
        }


class FileBatchDeleteRequest(BaseModel):
    """批量删除请求"""
    agent_id: str = Field(..., description="智能体ID")
    sources: list[str] = Field(..., description="文件路径列表", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "my_agent",
                "sources": [
                    "document1.pdf",
                    "document2.docx",
                    "notes.txt"
                ]
            }
        }

