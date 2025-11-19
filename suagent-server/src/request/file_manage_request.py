"""
文件管理请求模型
"""

from typing import Optional
from pydantic import BaseModel, Field
from src.request.base_request import BasePageKeywordRequest


class FileListRequest(BasePageKeywordRequest):
    """文件列表查询请求"""
    agent_id: str = Field(..., description="智能体ID")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "my_agent",
                "page": 1,
                "page_size": 20,
                "keyword": "文档"
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

