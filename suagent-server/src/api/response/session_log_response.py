"""
会话日志相关响应模型
"""

from datetime import datetime
from pydantic import BaseModel, Field


class SessionLogResponse(BaseModel):
    """会话日志响应模型"""
    
    id: int = Field(..., description="日志ID")
    session_id: int = Field(..., description="会话ID")
    agent_id: str = Field(..., description="智能体英文名")
    role: str = Field(..., description="角色(user/assistant/system)")
    content: str = Field(..., description="消息内容")
    created_at: datetime = Field(..., description="创建时间")
    created_by: str = Field(..., description="创建人")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 3000000000001,
                "session_id": 1000000001,
                "agent_id": "demo_agent",
                "role": "user",
                "content": "你好，请介绍一下你自己",
                "created_at": "2025-01-10T10:30:00",
                "created_by": "system"
            }
        }


class SessionLogSimpleResponse(BaseModel):
    """会话日志简要响应模型"""
    
    id: int = Field(..., description="日志ID")
    role: str = Field(..., description="角色")
    content: str = Field(..., description="消息内容")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class SessionMessageResponse(BaseModel):
    """会话消息响应模型（用于对话展示）"""
    
    role: str = Field(..., description="角色(user/assistant/system)")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(..., description="时间戳")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "你好",
                "timestamp": "2025-01-10T10:30:00"
            }
        }


class SessionSummaryResponse(BaseModel):
    """会话摘要响应模型"""
    
    session_id: int = Field(..., description="会话ID")
    agent_id: str = Field(..., description="智能体英文名")
    message_count: int = Field(..., description="消息数量")
    first_message_time: datetime = Field(..., description="首条消息时间")
    last_message_time: datetime = Field(..., description="最后消息时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1000000001,
                "agent_id": "demo_agent",
                "message_count": 10,
                "first_message_time": "2025-01-10T10:00:00",
                "last_message_time": "2025-01-10T11:00:00"
            }
        }

