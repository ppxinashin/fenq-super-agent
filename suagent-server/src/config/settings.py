"""
配置管理 - 使用 Pydantic Settings 管理环境变量
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""

    # ===== 基础配置 =====
    app_name: str = Field(default="Fenq Super Agent", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    log_level: str = Field(default="INFO", description="日志级别")

    # ===== API 服务配置 =====
    api_host: str = Field(default="0.0.0.0", description="API 服务主机")
    api_port: int = Field(default=8000, description="API 服务端口")

    # ===== LLM 配置 - OpenAI =====
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    openai_api_base: Optional[str] = Field(default=None, description="OpenAI API Base URL")
    openai_model: str = Field(default="qwen3-max", description="OpenAI 模型名称")
    openai_temperature: float = Field(default=0.7, description="温度参数")
    
    # ===== LangSmith 跟踪 =====
    langsmith_tracing: Optional[bool] = Field(default=False, description="是否启用 LangSmith 跟踪")
    langsmith_api_key: Optional[str] = Field(default=None, description="LangSmith API Key")
    langsmith_workspace_id: Optional[str] = Field(default=None, description="LangSmith Workspace ID")

    # ===== LLM 配置 - 阿里云通义千问 =====
    dashscope_api_key: Optional[str] = Field(default=None, description="DashScope API Key")
    dashscope_model: str = Field(default="qwen-max", description="通义千问模型名称")

    # ===== PostgreSQL / PGVector 配置 =====
    postgres_host: str = Field(default="localhost", description="PostgreSQL 主机")
    postgres_port: int = Field(default=5432, description="PostgreSQL 端口")
    postgres_user: str = Field(default="suagent", description="PostgreSQL 用户名")
    postgres_password: str = Field(default="postgres", description="PostgreSQL 密码")
    postgres_db: str = Field(default="super_agent_db", description="PostgreSQL 数据库名")
    
    # ===== PostgreSQL / PGVector RAG 配置 =====
    postgres_rag_host: str = Field(default="localhost", description="PostgreSQL 主机")
    postgres_rag_port: int = Field(default=5432, description="PostgreSQL 端口")
    postgres_rag_user: str = Field(default="suagent_rag", description="PostgreSQL 用户名")
    postgres_rag_password: str = Field(default="postgres", description="PostgreSQL 密码")
    postgres_rag_db: str = Field(default="super_agent_rag_db", description="PostgreSQL 数据库名")

    @property
    def postgres_connection_string(self) -> str:
        """生成 PostgreSQL 连接字符串"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        
    @property
    def postgres_rag_connection_string(self) -> str:
        """生成 PostgreSQL 连接字符串"""
        return (
            f"postgresql+psycopg://{self.postgres_rag_user}:{self.postgres_rag_password}"
            f"@{self.postgres_rag_host}:{self.postgres_rag_port}/{self.postgres_rag_db}"
        )

    # ===== Redis 配置 =====
    redis_host: str = Field(default="localhost", description="Redis 主机")
    redis_port: int = Field(default=6379, description="Redis 端口")
    redis_db: int = Field(default=0, description="Redis 数据库编号")
    redis_password: Optional[str] = Field(default=None, description="Redis 密码")

    @property
    def redis_url(self) -> str:
        """生成 Redis URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # ===== 向量存储配置 =====
    embedding_model: str = Field(default="text-embedding-v4", description="嵌入模型")
    vector_store_collection: str = Field(default="suagent_documents", description="向量库集合名称")

    # ===== 搜索工具配置 =====
    enable_web_search: bool = Field(default=True, description="启用网页搜索")
    max_search_results: int = Field(default=5, description="最大搜索结果数")
    
    # ===== MinIO 配置 =====
    minio_endpoint: str = Field(default="localhost:9000", description="MinIO 主机")
    minio_access_key: Optional[str] = Field(default=None, description="MinIO 访问密钥")
    minio_secret_key: Optional[str] = Field(default=None, description="MinIO 秘密密钥")
    minio_bucket: str = Field(default="suagent", description="MinIO 桶名称")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()

