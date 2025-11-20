"""配置管理 - 仅保留定时任务、消息队列和存储相关配置。"""

from typing import Optional
from urllib.parse import quote

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # ===== 基础配置 =====
    app_name: str = Field(default="Fenq Memory Sync Task", description="应用名称")
    app_version: str = Field(default="0.2.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    log_level: str = Field(default="INFO", description="日志级别")

    # ===== PostgreSQL 配置 =====
    postgres_host: str = Field(default="localhost", description="PostgreSQL 主机")
    postgres_port: int = Field(default=5432, description="PostgreSQL 端口")
    postgres_user: str = Field(default="suagent", description="PostgreSQL 用户名")
    postgres_password: str = Field(default="postgres", description="PostgreSQL 密码")
    postgres_db: str = Field(default="super_agent_db", description="PostgreSQL 数据库名")

    @property
    def postgres_connection_string(self) -> str:
        """生成 PostgreSQL 连接字符串"""
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ===== 调度配置 =====
    scheduler_timezone: str = Field(default="UTC", description="调度器时区")
    scheduler_job_store_url: Optional[str] = Field(
        default=None, description="调度任务持久化存储（默认复用 Postgres）"
    )
    scheduler_misfire_grace_seconds: int = Field(
        default=300, description="调度器错过执行的容忍窗口（秒）"
    )
    memory_sync_interval_minutes: int = Field(
        default=120, description="定时同步周期（分钟）"
    )

    # ===== RabbitMQ 配置 =====
    rabbitmq_host: str = Field(default="localhost", description="RabbitMQ 主机")
    rabbitmq_port: int = Field(default=5672, description="RabbitMQ 端口")
    rabbitmq_username: str = Field(default="guest", description="RabbitMQ 用户名")
    rabbitmq_password: str = Field(default="guest", description="RabbitMQ 密码")
    rabbitmq_virtual_host: str = Field(default="/", description="RabbitMQ vhost")

    # 队列拓扑 & 参数
    mq_exchange: str = Field(default="memory.sync", description="主交换机")
    mq_routing_key: str = Field(default="memory.sync", description="路由键")
    mq_queue: str = Field(default="memory.sync.queue", description="主队列")
    mq_dead_letter_exchange: str = Field(default="memory.sync.dlx", description="死信交换机")
    mq_dead_letter_routing_key: str = Field(default="memory.sync.dlx", description="死信路由键")
    mq_dead_letter_queue: str = Field(default="memory.sync.dlx.queue", description="死信队列")
    mq_message_ttl_ms: int = Field(default=30 * 60 * 1000, description="消息TTL（毫秒）")
    mq_prefetch_count: int = Field(default=10, description="消费者预取数量")
    mq_publish_delay_ms: int = Field(default=50, description="生产者发送间隔（毫秒）")
    mq_consumer_max_concurrency: int = Field(default=5, description="消费者同步并发上限")

    @property
    def rabbitmq_url(self) -> str:
        """构建 AMQP 连接串"""
        vhost = quote(self.rabbitmq_virtual_host, safe="")
        return (
            f"amqp://{self.rabbitmq_username}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/{vhost}"
        )

    @property
    def scheduler_store_url(self) -> str:
        """调度器使用的 job store 连接串"""
        return self.scheduler_job_store_url or self.postgres_connection_string

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
