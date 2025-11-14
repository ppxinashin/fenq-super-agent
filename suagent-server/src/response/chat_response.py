"""
聊天相关的响应模型
"""

from pydantic import BaseModel, Field

class ChatTitleResponse(BaseModel):
    """聊天标题响应模型"""
    title: str = Field(..., description="标题")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "聊天标题"
            }
        }