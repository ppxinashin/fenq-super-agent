"""
会话相关响应模型
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SessionResponse(BaseModel):
    """会话响应模型"""
    
    id: int = Field(..., description="记录ID")
    session_id: int = Field(..., description="会话ID")
    agent_id: str = Field(..., description="智能体ID")
    title: Optional[str] = Field(None, description="会话标题")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "session_id": 1000000001,
                "agent_id": "demo_agent",
                "title": "关于天气的讨论",
                "created_at": "2025-01-10T10:00:00",
                "updated_at": "2025-01-10T11:00:00"
            }
        }


class SessionListResponse(BaseModel):
    """会话列表响应模型（分页）"""
    
    items: List[SessionResponse] = Field(..., description="会话列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    has_prev: bool = Field(..., description="是否有上一页")
    has_next: bool = Field(..., description="是否有下一页")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "session_id": 1000000001,
                        "agent_id": "demo_agent",
                        "title": "关于天气的讨论",
                        "created_at": "2025-01-10T10:00:00",
                        "updated_at": "2025-01-10T11:00:00"
                    }
                ],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
                "has_prev": False,
                "has_next": True
            }
        }


class SessionCreateResponse(BaseModel):
    """会话创建响应模型"""
    
    session_id: int = Field(..., description="会话ID")
    agent_id: str = Field(..., description="智能体ID")
    title: Optional[str] = Field(None, description="会话标题")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1000000001,
                "agent_id": "demo_agent",
                "title": "新对话"
            }
        }

