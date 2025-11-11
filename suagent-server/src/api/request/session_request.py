"""
会话相关请求模型
"""

from typing import Optional
from pydantic import BaseModel, Field
from src.consts import AgentConsts
from src.api.request.base_request import BasePageKeywordRequest


class SessionCreateRequest(BaseModel):
    """会话创建请求模型"""
    
    agent_id: str = Field(
        ...,
        description=f"智能体ID，{AgentConsts.AGENT_ID_RULE_DESC}",
        min_length=2,
        max_length=20,
        pattern=AgentConsts.AGENT_ID_PATTERN
    )
    user_id: str = Field(..., description="用户ID")
    title: Optional[str] = Field(None, description="会话标题（可选）", max_length=200)
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "demo_agent",
                "user_id": "1",
                "title": "新对话"
            }
        }


class SessionUpdateRequest(BaseModel):
    """会话更新请求模型（修改标题）"""
    
    session_id: int = Field(..., description="会话ID", gt=0)
    title: str = Field(..., description="新的会话标题", min_length=1, max_length=200)
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1000000001,
                "title": "修改后的标题"
            }
        }


class SessionDeleteRequest(BaseModel):
    """会话删除请求模型"""
    
    session_id: int = Field(..., description="会话ID", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1000000001
            }
        }


class SessionListRequest(BasePageKeywordRequest):
    """会话列表查询请求模型（分页，按智能体）"""
    
    agent_id: str = Field(
        ...,
        description=f"智能体ID，{AgentConsts.AGENT_ID_RULE_DESC}",
        min_length=2,
        max_length=20,
        pattern=AgentConsts.AGENT_ID_PATTERN
    )
    keyword: Optional[str] = Field(
        default=None,
        description="无需传递该字段"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "demo_agent",
                "page": 1,
                "page_size": 20
            }
        }


class SessionTitleGenerateRequest(BaseModel):
    """会话标题生成请求模型"""
    
    session_id: int = Field(..., description="会话ID", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1000000001
            }
        }
