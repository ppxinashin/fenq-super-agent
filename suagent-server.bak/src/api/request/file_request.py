"""
文件上传相关请求模型
"""

from typing import Optional
from pydantic import BaseModel, Field
from src.consts import AgentConsts


class FileRequest(BaseModel):
    """文件上传至MinIO请求模型"""
    
    file_name: str = Field(..., description="文件名", min_length=1)
    file_content: bytes = Field(..., description="文件内容（二进制）")
    bucket_name: str = Field(default="suagent", description="MinIO桶名")
    content_type: Optional[str] = Field(None, description="文件MIME类型")
    object_path: Optional[str] = Field(None, description="对象存储路径（可选，默认使用文件名）")
    user_id: str = Field(..., description="用户ID")
    agent_id: Optional[str] = Field(
        None,
        description=f"智能体ID（可选），{AgentConsts.AGENT_ID_RULE_DESC}",
        min_length=2,
        max_length=20,
        pattern=AgentConsts.AGENT_ID_PATTERN
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_name": "document.pdf",
                "file_content": "b'binary_content_here'",
                "bucket_name": "suagent",
                "content_type": "application/pdf",
                "object_path": "football/admin/document.pdf",
                "user_id": "admin",
                "agent_id": "football"
            }
        }
