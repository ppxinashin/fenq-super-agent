"""
智能体管理请求模型
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from src.consts import AgentConsts


class AgentManageCreateRequest(BaseModel):
    """创建智能体请求模型"""
    
    agent_id: str = Field(
        ...,
        min_length=2,
        max_length=20,
        pattern=AgentConsts.AGENT_ID_PATTERN,
        description=f"智能体英文名（唯一标识），{AgentConsts.AGENT_ID_RULE_DESC}"
    )
    agent_name: str = Field(..., min_length=2, max_length=100, description="智能体中文名")
    description: Optional[str] = Field(None, description="智能体介绍")
    system_prompt: str = Field(..., min_length=1, description="系统提示词")
    tools: List[str] = Field(default_factory=list, description="绑定工具列表")
    mcp_enabled: bool = Field(default=False, description="是否启用MCP")
    mcp_servers: Optional[str] = Field(
        default=None,
        description="MCP服务器配置，前端传递JSON字符串，后端需要解析后入库"
    )
    scope: Literal["personal", "global"] = Field(
        default="personal",
        description="智能体作用域：personal=个人，global=全局（仅管理员可设置为global）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "demo_agent",
                "agent_name": "演示智能体",
                "description": "这是一个示例智能体",
                "system_prompt": "你是一个友好的AI助手",
                "tools": ["now_time", "web_search"],
                "mcp_enabled": True,
                "mcp_servers": "{\"default\": {\"type\": \"sse\", \"url\": \"https://example.com\"}}",
                "scope": "personal"
            }
        }


class AgentManageUpdateRequest(BaseModel):
    """编辑智能体请求模型"""
    
    agent_id: Optional[str] = Field(
        None,
        min_length=2,
        max_length=20,
        pattern=AgentConsts.AGENT_ID_PATTERN,
        description=f"智能体英文名（唯一标识），{AgentConsts.AGENT_ID_RULE_DESC}"
    )
    agent_name: Optional[str] = Field(None, min_length=2, max_length=100, description="智能体中文名")
    description: Optional[str] = Field(None, description="智能体介绍")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    tools: Optional[List[str]] = Field(None, description="绑定工具列表")
    mcp_enabled: Optional[bool] = Field(None, description="是否启用MCP")
    mcp_servers: Optional[str] = Field(
        default=None,
        description="MCP服务器配置，前端传递JSON字符串，后端需要解析后入库"
    )
    scope: Optional[Literal["personal", "global"]] = Field(
        default=None,
        description="智能体作用域调整（仅管理员可修改）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "新的智能体名称",
                "description": "更新后的介绍",
                "system_prompt": "你是一个更强大的AI助手",
                "tools": ["calculator"],
                "mcp_enabled": False,
                "mcp_servers": "{\"default\": {\"type\": \"sse\", \"url\": \"https://example.com\"}}",
                "scope": "global"
            }
        }
