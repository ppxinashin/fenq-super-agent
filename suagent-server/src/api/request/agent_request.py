"""
智能体相关请求模型
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AgentAddRequest(BaseModel):
    """智能体新增请求模型"""
    
    agent_id: str = Field(..., description="智能体英文名（唯一标识）", min_length=2, max_length=100)
    agent_name: str = Field(..., description="智能体中文名", min_length=2, max_length=100)
    description: Optional[str] = Field(None, description="智能体介绍")
    system_prompt: str = Field(..., description="系统提示词", min_length=1)
    tools: List[str] = Field(default_factory=list, description="绑定工具清单")
    mcp_enabled: bool = Field(default=False, description="MCP开关")
    mcp_servers: Dict[str, Any] = Field(default_factory=dict, description="MCP服务器列表")
    created_by: str = Field(..., description="创建人")
    
    class Config:
        json_schema_extra = {
            "example": {
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
                "created_by": "system"
            }
        }


class AgentEditRequest(BaseModel):
    """智能体编辑请求模型"""
    
    id: int = Field(..., description="智能体ID", gt=0)
    agent_id: Optional[str] = Field(None, description="智能体英文名（唯一标识）", min_length=2, max_length=100)
    agent_name: Optional[str] = Field(None, description="智能体中文名", min_length=2, max_length=100)
    description: Optional[str] = Field(None, description="智能体介绍")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    tools: Optional[List[str]] = Field(None, description="绑定工具清单")
    mcp_enabled: Optional[bool] = Field(None, description="MCP开关")
    mcp_servers: Optional[Dict[str, Any]] = Field(None, description="MCP服务器列表")
    updated_by: str = Field(..., description="更新人")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 2000000000001,
                "agent_id": "demo_agent",
                "agent_name": "演示智能体（已修改）",
                "description": "这是一个更新后的演示智能体",
                "system_prompt": "你是一个更加友好的AI助手",
                "tools": ["now_time", "web_search", "calculator"],
                "mcp_enabled": True,
                "mcp_servers": {
                    "amap-maps": {
                        "type": "sse",
                        "url": "https://mcp.api-inference.modelscope.net/afbe1094621a49/sse"
                    }
                },
                "updated_by": "admin"
            }
        }

