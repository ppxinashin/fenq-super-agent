"""
会话日志相关请求模型
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class SessionLogAddRequest(BaseModel):
    """会话日志新增请求模型"""
    
    session_id: int = Field(..., description="会话ID", gt=0)
    agent_id: str = Field(..., description="智能体英文名", min_length=1)
    role: str = Field(..., description="角色(user/assistant/system)")
    content: str = Field(..., description="消息内容", min_length=1)
    created_by: str = Field(..., description="创建人")
    
    @validator('role')
    def validate_role(cls, v):
        """验证角色"""
        if v not in ['user', 'assistant', 'system']:
            raise ValueError('角色必须是 user、assistant 或 system')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1000000001,
                "agent_id": "demo_agent",
                "role": "user",
                "content": "你好，请介绍一下你自己",
                "created_by": "system"
            }
        }


class SessionLogEditRequest(BaseModel):
    """会话日志编辑请求模型"""
    
    id: int = Field(..., description="日志ID", gt=0)
    session_id: Optional[int] = Field(None, description="会话ID", gt=0)
    agent_id: Optional[str] = Field(None, description="智能体英文名")
    role: Optional[str] = Field(None, description="角色(user/assistant/system)")
    content: Optional[str] = Field(None, description="消息内容")
    updated_by: str = Field(..., description="更新人")
    
    @validator('role')
    def validate_role(cls, v):
        """验证角色"""
        if v is not None and v not in ['user', 'assistant', 'system']:
            raise ValueError('角色必须是 user、assistant 或 system')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 3000000000001,
                "session_id": 1000000001,
                "agent_id": "demo_agent",
                "role": "user",
                "content": "你好，请介绍一下你自己（已修改）",
                "updated_by": "admin"
            }
        }

