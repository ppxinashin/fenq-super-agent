"""
智能体管理相关请求模型
"""
import json
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re
from src.consts.agent_consts import AgentConsts


class AgentCreateRequest(BaseModel):
    """智能体创建请求模型"""

    agent_id: str = Field(..., description="智能体英文名（唯一标识）", min_length=AgentConsts.AGENT_ID_MIN_LENGTH, max_length=AgentConsts.AGENT_ID_MAX_LENGTH)
    agent_name: str = Field(..., description="智能体中文名", min_length=AgentConsts.AGENT_NAME_MIN_LENGTH, max_length=AgentConsts.AGENT_NAME_MAX_LENGTH)
    description: Optional[str] = Field(default=AgentConsts.DEFAULT_AGENT_DESCRIPTION, description="智能体介绍", max_length=AgentConsts.AGENT_DESCRIPTION_MAX_LENGTH)
    system_prompt: str = Field(default=AgentConsts.DEFAULT_SYSTEM_PROMPT, description="系统提示词", max_length=AgentConsts.AGENT_SYSTEM_PROMPT_MAX_LENGTH)
    tools: List[str] = Field(default=[], description="可用工具列表")
    mcp_status: bool = Field(default=False, description="MCP状态")
    mcp_config: Optional[str] = Field(default='{}', description="MCP服务器配置（JSON字符串）")

    @field_validator('agent_id')
    @classmethod
    def validate_agent_id(cls, v):
        """智能体ID格式校验"""
        if not re.match(AgentConsts.AGENT_ID_PATTERN, v):
            raise ValueError(AgentConsts.AGENT_ID_RULE_DESC)
        if v.lower() in AgentConsts.AGENT_ID_FORBIDDEN_NAMES:
            raise ValueError(f"禁止使用以下智能体名称: {', '.join(AgentConsts.AGENT_ID_FORBIDDEN_NAMES)}")
        return v

    @field_validator('tools')
    @classmethod
    def validate_tools(cls, v):
        """工具列表校验"""
        if v:
            for tool in v:
                if tool not in AgentConsts.AVAILABLE_TOOLS:
                    raise ValueError(f"不支持的工具: {tool}，可用工具: {', '.join(AgentConsts.AVAILABLE_TOOLS)}")
        return v

    @field_validator('mcp_config')
    @classmethod
    def validate_mcp_config(cls, v):
        """MCP配置校验（如果提供的话）"""
        if v:
            try:
                import json
                json.loads(v)  # 验证是否为有效的JSON字符串
            except json.JSONDecodeError:
                raise ValueError("MCP配置必须是有效的JSON字符串")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "web_assistant",
                "agent_name": "网页助手",
                "description": "专门处理网页相关任务的智能体",
                "system_prompt": "你是一个专业的网页分析助手，能够抓取和分析网页内容。",
                "tools": ["web_scraper", "web_search"],
                "mcp_status": False,
                "mcp_config": None
            }
        }


class AgentUpdateRequest(BaseModel):
    """智能体修改请求模型"""

    agent_id: str = Field(..., description="智能体英文名")
    agent_name: Optional[str] = Field(default=None, description="智能体中文名", min_length=AgentConsts.AGENT_NAME_MIN_LENGTH, max_length=AgentConsts.AGENT_NAME_MAX_LENGTH)
    description: Optional[str] = Field(default=None, description="智能体介绍", max_length=AgentConsts.AGENT_DESCRIPTION_MAX_LENGTH)
    system_prompt: Optional[str] = Field(default=None, description="系统提示词", max_length=AgentConsts.AGENT_SYSTEM_PROMPT_MAX_LENGTH)
    tools: Optional[List[str]] = Field(default=None, description="可用工具列表")
    mcp_status: Optional[bool] = Field(default=None, description="MCP状态")
    mcp_config: Optional[str] = Field(default='{}', description="MCP服务器配置（JSON字符串）")

    @field_validator('tools')
    @classmethod
    def validate_tools(cls, v):
        """工具列表校验"""
        if v is not None:
            for tool in v:
                if tool not in AgentConsts.AVAILABLE_TOOLS:
                    raise ValueError(f"不支持的工具: {tool}，可用工具: {', '.join(AgentConsts.AVAILABLE_TOOLS)}")
        return v

    @field_validator('mcp_config')
    @classmethod
    def validate_mcp_config(cls, v):
        """MCP配置校验（如果提供的话）"""
        if v is not None:
            try:
                import json
                json.loads(v)  # 验证是否为有效的JSON字符串
            except json.JSONDecodeError:
                raise ValueError("MCP配置必须是有效的JSON字符串")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "web_assistant",
                "agent_name": "高级网页助手",
                "description": "更新后的网页助手描述",
                "system_prompt": "你是一个高级的网页分析专家。",
                "tools": ["web_scraper", "web_search", "calculator"],
                "mcp_status": True,
                "mcp_config": '{"mcp-server-1": {"type":"sse", "url":"http://mcp.example.com/mcp"}}'
            }
        }


class AgentListRequest(BaseModel):
    """智能体列表查询请求模型"""

    page: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=20, description="每页数量", ge=1, le=100)
    keyword: Optional[str] = Field(default=None, description="关键词搜索（按名称或介绍）")
    creator_only: bool = Field(default=False, description="是否只查看自己创建的智能体")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "keyword": "网页",
                "creator_only": True
            }
        }


class AgentCardListRequest(BaseModel):
    """智能体卡片展示请求模型"""

    page: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=20, description="每页数量", ge=1, le=100)
    keyword: Optional[str] = Field(default=None, description="关键词搜索（按名称或介绍）")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "keyword": "助手"
            }
        }


class AgentToolsUpdateRequest(BaseModel):
    """智能体工具更新请求模型"""

    agent_id: str = Field(..., description="智能体英文名")
    tools: List[str] = Field(..., description="新的工具列表")

    @field_validator('tools')
    @classmethod
    def validate_tools(cls, v):
        """工具列表校验"""
        for tool in v:
            if tool not in AgentConsts.AVAILABLE_TOOLS:
                raise ValueError(f"不支持的工具: {tool}，可用工具: {', '.join(AgentConsts.AVAILABLE_TOOLS)}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "web_assistant",
                "tools": ["web_scraper", "web_search", "calculator"]
            }
        }


class AgentMcpUpdateRequest(BaseModel):
    """智能体MCP配置更新请求模型"""

    agent_id: str = Field(..., description="智能体英文名")
    mcp_status: bool = Field(..., description="MCP状态")
    mcp_config: Optional[str] = Field(default='{}', description="MCP服务器配置（JSON字符串）")

    @field_validator('mcp_config')
    @classmethod
    def validate_mcp_config(cls, v):
        """MCP配置校验（如果提供的话）"""
        if v is not None:
            try:
                import json
                json.loads(v)  # 验证是否为有效的JSON字符串
            except json.JSONDecodeError:
                raise ValueError("MCP配置必须是有效的JSON字符串")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "web_assistant",
                "mcp_status": True,
                "mcp_config": '{"server": "mcp-server-1", "port": 3000, "timeout": 30}'
            }
        }