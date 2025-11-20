"""
配置管理 - 使用 Pydantic Settings 管理环境变量
"""

from typing import Optional
from urllib.parse import quote

from pydantic import Field
from pydantic_settings import BaseSettings


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
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
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

    # ===== RabbitMQ 配置 =====
    rabbitmq_host: str = Field(default="localhost", description="RabbitMQ 主机")
    rabbitmq_port: int = Field(default=5672, description="RabbitMQ 端口")
    rabbitmq_username: str = Field(default="guest", description="RabbitMQ 用户名")
    rabbitmq_password: str = Field(default="guest", description="RabbitMQ 密码")
    rabbitmq_virtual_host: str = Field(default="/", description="RabbitMQ vhost")

    mq_exchange: str = Field(default="memory.sync", description="主交换机")
    mq_routing_key: str = Field(default="memory.sync", description="路由键")
    mq_queue: str = Field(default="memory.sync.queue", description="主队列")
    mq_dead_letter_exchange: str = Field(default="memory.sync.dlx", description="死信交换机")
    mq_dead_letter_routing_key: str = Field(default="memory.sync.dlx", description="死信路由键")
    mq_dead_letter_queue: str = Field(default="memory.sync.dlx.queue", description="死信队列")
    mq_message_ttl_ms: int = Field(default=30 * 60 * 1000, description="消息TTL（毫秒）")
    mq_prefetch_count: int = Field(default=10, description="消费者预取数量")

    @property
    def rabbitmq_url(self) -> str:
        """构建 AMQP 连接串"""
        vhost = quote(self.rabbitmq_virtual_host, safe="")
        return (
            f"amqp://{self.rabbitmq_username}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/{vhost}"
        )

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

    # ===== JWT 配置 =====
    jwt_secret_key: str = Field(default="your-secret-key-change-this-in-production", description="JWT 密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT 加密算法")
    jwt_expire_minutes: int = Field(default=1440, description="JWT 过期时间（分钟，默认24小时）")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()
