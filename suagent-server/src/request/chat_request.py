"""
聊天相关的请求模型
"""

from typing import Optional
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """创建会话请求模型"""
    agent_id: str = Field(..., description="智能体ID", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_123"
            }
        }


class UpdateSessionTitleRequest(BaseModel):
    """更新会话标题请求模型"""
    title: str = Field(..., description="会话标题", min_length=1, max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "新的会话标题"
            }
        }