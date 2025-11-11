"""
聊天相关请求模型
"""

from typing import Optional, Union
from pydantic import BaseModel, Field
from src.consts import AgentConsts


class ChatRequest(BaseModel):
    """智能体聊天请求模型"""
    
    agent_id: str = Field(
        ...,
        description=f"智能体ID，{AgentConsts.AGENT_ID_RULE_DESC}",
        min_length=2,
        max_length=20,
        pattern=AgentConsts.AGENT_ID_PATTERN
    )
    message: str = Field(..., description="用户消息内容", min_length=1)
    chat_id: Optional[Union[str, int]] = Field(None, description="聊天会话ID（可选，不传则自动生成新会话）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "demo_agent",
                "message": "你好，请问今天天气怎么样？",
                "chat_id": "demo_agent_1"
            }
        }
