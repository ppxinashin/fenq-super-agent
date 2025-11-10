"""
智能体相关响应模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """智能体响应模型"""
    
    id: int = Field(..., description="智能体ID")
    agent_id: str = Field(..., description="智能体英文名（唯一标识）")
    agent_name: str = Field(..., description="智能体中文名")
    description: Optional[str] = Field(None, description="智能体介绍")
    system_prompt: str = Field(..., description="系统提示词")
    tools: List[str] = Field(default_factory=list, description="绑定工具清单")
    mcp_enabled: bool = Field(default=False, description="MCP开关")
    mcp_servers: Dict[str, Any] = Field(default_factory=dict, description="MCP服务器列表")
    created_at: datetime = Field(..., description="创建时间")
    created_by: str = Field(..., description="创建人")
    updated_at: datetime = Field(..., description="更新时间")
    updated_by: str = Field(..., description="更新人")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 2000000000001,
                "agent_id": "demo_agent",
                "agent_name": "演示智能体",
                "description": "这是一个演示智能体",
                "system_prompt": "你是一个友好的AI助手",
                "tools": ["now_time", "web_search"],
                "mcp_enabled": True,
                "mcp_servers": {
                    "amap-maps": {
                        "type": "sse",
                        "url": "https://mcp.api-inference.modelscope.net/afbe1094621a49/sse"
                    }
                },
                "created_at": "2025-01-10T10:30:00",
                "created_by": "system",
                "updated_at": "2025-01-10T10:30:00",
                "updated_by": "system"
            }
        }


class AgentSimpleResponse(BaseModel):
    """智能体简要信息响应模型"""
    
    id: int = Field(..., description="智能体ID")
    agent_id: str = Field(..., description="智能体英文名")
    agent_name: str = Field(..., description="智能体中文名")
    description: Optional[str] = Field(None, description="智能体介绍")
    mcp_enabled: bool = Field(default=False, description="MCP开关")
    
    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """智能体列表项响应模型"""
    
    id: int = Field(..., description="智能体ID")
    agent_id: str = Field(..., description="智能体英文名")
    agent_name: str = Field(..., description="智能体中文名")
    description: Optional[str] = Field(None, description="智能体介绍")
    tools_count: int = Field(default=0, description="工具数量")
    mcp_enabled: bool = Field(default=False, description="MCP开关")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class AgentConfigResponse(BaseModel):
    """智能体配置响应模型（仅配置信息）"""
    
    agent_id: str = Field(..., description="智能体英文名")
    system_prompt: str = Field(..., description="系统提示词")
    tools: List[str] = Field(default_factory=list, description="绑定工具清单")
    mcp_enabled: bool = Field(default=False, description="MCP开关")
    mcp_servers: Dict[str, Any] = Field(default_factory=dict, description="MCP服务器列表")
    
    class Config:
        from_attributes = True

