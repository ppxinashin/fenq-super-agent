"""
配置管理 - 使用 Pydantic Settings 管理环境变量
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""

    # ===== MCP 服务配置 =====
    fastmcp_host: str = Field(default="0.0.0.0", description="FastMCP 服务主机")
    fastmcp_port: int = Field(default=10086, description="FastMCP 服务端口")

    # ===== YouTube 工具配置 =====
    youtube_api_key: Optional[str] = Field(default=None, description="YouTube API Key")
    youtube_search_limit: int = Field(default=5, description="YouTube 搜索最大结果数")
  
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()

