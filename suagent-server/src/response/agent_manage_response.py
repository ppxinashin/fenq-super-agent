"""
智能体管理相关响应模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_serializer


class AgentInfo(BaseModel):
    """智能体详细信息响应模型"""

    agent_id: str = Field(..., description="智能体英文名")
    agent_name: str = Field(..., description="智能体中文名")
    description: str = Field(..., description="智能体介绍")
    system_prompt: str = Field(..., description="系统提示词")
    tools: List[str] = Field(..., description="可用工具列表")
    mcp_status: bool = Field(..., description="MCP状态")
    mcp_config: Optional[str] = Field(default=None, description="MCP服务器配置")
    creator_id: int = Field(..., description="创建人ID")
    creator_username: str = Field(..., description="创建人用户名")
    created_at: datetime = Field(..., description="创建时间")
    updated_by_id: Optional[int] = Field(default=None, description="修改人ID")
    updated_by_username: Optional[str] = Field(default=None, description="修改人用户名")
    updated_at: Optional[datetime] = Field(default=None, description="修改时间")

    @field_serializer('created_at', 'updated_at')
    def format_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "agent_id": "web_assistant",
                "agent_name": "网页助手",
                "description": "专门处理网页相关任务的智能体",
                "system_prompt": "你是一个专业的网页分析助手，能够抓取和分析网页内容。",
                "tools": ["web_scraper", "web_search"],
                "mcp_status": True,
                "mcp_config": '{"server": "mcp-server-1", "port": 3000}',
                "creator_id": 231073032568705024,
                "creator_username": "admin",
                "created_at": "2025-01-01 00:00:00",
                "updated_by_id": 231073032568705024,
                "updated_by_username": "admin",
                "updated_at": "2025-01-01 12:00:00"
            }
        }


class AgentSimpleInfo(BaseModel):
    """智能体简单信息响应模型（用于卡片展示）"""

    agent_id: str = Field(..., description="智能体英文名")
    agent_name: str = Field(..., description="智能体中文名")
    description: str = Field(..., description="智能体介绍")
    tools_count: int = Field(..., description="可用工具数量")
    mcp_enabled: bool = Field(..., description="是否启用MCP")
    creator_username: str = Field(..., description="创建人用户名")
    created_at: datetime = Field(..., description="创建时间")

    @field_serializer('created_at')
    def format_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "agent_id": "web_assistant",
                "agent_name": "网页助手",
                "description": "专门处理网页相关任务的智能体",
                "tools_count": 3,
                "mcp_enabled": True,
                "creator_username": "admin",
                "created_at": "2025-01-01 00:00:00"
            }
        }


class AgentListItem(BaseModel):
    """智能体列表项响应模型（用于管理列表）"""

    agent_id: str = Field(..., description="智能体英文名")
    agent_name: str = Field(..., description="智能体中文名")
    description: str = Field(..., description="智能体介绍")
    tools_count: int = Field(..., description="可用工具数量")
    mcp_enabled: bool = Field(..., description="是否启用MCP")
    creator_username: str = Field(..., description="创建人用户名")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="修改时间")

    @field_serializer('created_at', 'updated_at')
    def format_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "agent_id": "web_assistant",
                "agent_name": "网页助手",
                "description": "专门处理网页相关任务的智能体",
                "tools_count": 2,
                "mcp_enabled": False,
                "creator_username": "admin",
                "created_at": "2025-01-01 00:00:00",
                "updated_at": "2025-01-01 12:00:00"
            }
        }


class AgentCreateResponse(BaseModel):
    """智能体创建响应模型"""

    agent_id: str = Field(..., description="智能体英文名")
    agent_name: str = Field(..., description="智能体中文名")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "agent_id": "web_assistant",
                "agent_name": "网页助手"
            }
        }


class AgentUpdateResponse(BaseModel):
    """智能体更新响应模型"""

    agent_id: str = Field(..., description="智能体英文名")
    updated_fields: List[str] = Field(..., description="更新的字段列表")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "agent_id": "web_assistant",
                "updated_fields": ["agent_name", "description", "mcp_status"]
            }
        }


class AgentDeleteResponse(BaseModel):
    """智能体删除响应模型"""

    agent_id: str = Field(..., description="智能体英文名")
    deleted: bool = Field(..., description="是否删除成功")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "agent_id": "web_assistant",
                "deleted": True
            }
        }