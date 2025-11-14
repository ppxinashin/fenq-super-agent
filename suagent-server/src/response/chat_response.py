"""
聊天相关的响应模型
"""

from typing import Optional, List
from datetime import datetime
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


class CreateSessionResponse(BaseModel):
    """创建会话响应模型"""
    session_id: int = Field(..., description="会话ID")
    agent_id: str = Field(..., description="智能体ID")
    title: str = Field(..., description="会话标题（初始为空）")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1000000000001,
                "agent_id": "agent_123",
                "title": "",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class SessionInfoResponse(BaseModel):
    """会话信息响应模型"""
    session_id: int = Field(..., description="会话ID")
    agent_id: str = Field(..., description="智能体ID")
    agent_name: str = Field(..., description="智能体名称")
    title: str = Field(..., description="会话标题")
    created_at: datetime = Field(..., description="创建时间")
    last_message_time: Optional[datetime] = Field(None, description="最后消息时间")
    message_count: int = Field(..., description="消息数量")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1000000000001,
                "agent_id": "agent_123",
                "agent_name": "智能助手",
                "title": "讨论AI技术",
                "created_at": "2024-01-01T00:00:00Z",
                "last_message_time": "2024-01-01T01:00:00Z",
                "message_count": 15
            }
        }


class ChatMessageResponse(BaseModel):
    """聊天消息响应模型"""
    role: str = Field(..., description="角色（user/assistant/system）")
    content: str = Field(..., description="消息内容")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "你好，请帮我分析这个问题",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class ChatHistoryResponse(BaseModel):
    """聊天历史响应模型"""
    session_id: int = Field(..., description="会话ID")
    messages: List[ChatMessageResponse] = Field(..., description="消息列表")
    total_count: int = Field(..., description="总消息数量")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1000000000001,
                "messages": [
                    {
                        "role": "user",
                        "content": "你好",
                        "created_at": "2024-01-01T00:00:00Z"
                    },
                    {
                        "role": "assistant",
                        "content": "你好！有什么可以帮助您的吗？",
                        "created_at": "2024-01-01T00:00:01Z"
                    }
                ],
                "total_count": 2
            }
        }