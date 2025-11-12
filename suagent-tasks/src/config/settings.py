"""
配置管理 - 使用 Pydantic Settings 管理环境变量
"""

from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""

    # ===== 基础配置 =====
    app_name: str = Field(default="Fenq Super Agent Scheduler", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    log_level: str = Field(default="INFO", description="日志级别")

    # ===== Celery 配置 =====
    celery_broker_url: str = Field(
        default="amqp://guest:guest@localhost:5672//",
        description="Celery Broker URL (RabbitMQ)"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        description="Celery Result Backend (Redis)"
    )

    # ===== 任务序列化配置 =====
    celery_task_serializer: str = Field(default="json", description="任务序列化格式")
    celery_result_serializer: str = Field(default="json", description="结果序列化格式")
    celery_accept_content: List[str] = Field(default=["json"], description="接受的内容类型")
    celery_timezone: str = Field(default="Asia/Shanghai", description="时区")
    celery_enable_utc: bool = Field(default=True, description="启用UTC")

    # ===== 任务执行配置 =====
    celery_task_track_started: bool = Field(default=True, description="跟踪任务开始")
    celery_task_time_limit: int = Field(default=3600, description="任务超时时间(秒)")
    celery_task_soft_time_limit: int = Field(default=3000, description="任务软超时时间(秒)")
    celery_worker_prefetch_multiplier: int = Field(default=1, description="Worker预取倍数")
    celery_worker_max_tasks_per_child: int = Field(default=50, description="每个Worker最大任务数")
    celery_worker_concurrency: int = Field(default=4, description="Worker并发数")

    # ===== 重试配置 =====
    celery_task_reject_on_worker_lost: bool = Field(default=True, description="Worker丢失时拒绝任务")
    celery_task_acks_late: bool = Field(default=True, description="延迟确认")

    # ===== MinIO 配置 =====
    minio_endpoint: str = Field(default="localhost:9000", description="MinIO 主机")
    minio_access_key: Optional[str] = Field(default=None, description="MinIO 访问密钥")
    minio_secret_key: Optional[str] = Field(default=None, description="MinIO 秘密密钥")
    minio_secure: bool = Field(default=False, description="MinIO SSL/TLS")
    minio_memory_bucket: str = Field(default="user-memories", description="MinIO 记忆存储桶")
    minio_ssl_cert_path: Optional[str] = Field(default=None, description="MinIO SSL证书路径")
    minio_ssl_key_path: Optional[str] = Field(default=None, description="MinIO SSL密钥路径")

    # ===== PostgreSQL 配置 =====
    postgres_host: str = Field(default="localhost", description="PostgreSQL 主机")
    postgres_port: int = Field(default=5432, description="PostgreSQL 端口")
    postgres_user: str = Field(default="postgres", description="PostgreSQL 用户名")
    postgres_password: str = Field(default="password", description="PostgreSQL 密码")
    postgres_db: str = Field(default="suagent", description="PostgreSQL 数据库名")

    @property
    def database_url(self) -> str:
        """生成 PostgreSQL 连接字符串"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ===== Redis 配置 =====
    redis_host: str = Field(default="localhost", description="Redis 主机")
    redis_port: int = Field(default=6379, description="Redis 端口")
    redis_db: int = Field(default=0, description="Redis 数据库编号")
    redis_password: Optional[str] = Field(default=None, description="Redis 密码")

    # ===== 调度器配置 =====
    max_concurrent_users: int = Field(default=10, description="最大并发用户数")
    batch_size: int = Field(default=100, description="批处理大小")
    memory_sync_retry_delay: int = Field(default=300, description="记忆同步重试延迟(秒)")
    memory_sync_max_retries: int = Field(default=3, description="记忆同步最大重试次数")
    memory_sync_schedule_hour: int = Field(default=2, description="记忆同步执行小时")
    memory_sync_schedule_minute: int = Field(default=0, description="记忆同步执行分钟")
    memory_sync_date_range_days: int = Field(default=1, description="同步前N天的数据")

    # ===== RabbitMQ 配置 =====
    rabbitmq_host: str = Field(default="localhost", description="RabbitMQ 主机")
    rabbitmq_port: int = Field(default=5672, description="RabbitMQ 端口")
    rabbitmq_user: str = Field(default="guest", description="RabbitMQ 用户名")
    rabbitmq_password: str = Field(default="guest", description="RabbitMQ 密码")
    rabbitmq_vhost: str = Field(default="/", description="RabbitMQ 虚拟主机")

    @property
    def celery_broker_url_rabbitmq(self) -> str:
        """生成 RabbitMQ 连接字符串"""
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}{self.rabbitmq_vhost}"
        )

    # ===== 告警配置 =====
    alert_email_enabled: bool = Field(default=False, description="启用邮件告警")
    alert_email_smtp_host: str = Field(default="localhost", description="SMTP 主机")
    alert_email_smtp_port: int = Field(default=587, description="SMTP 端口")
    alert_email_username: Optional[str] = Field(default=None, description="SMTP 用户名")
    alert_email_password: Optional[str] = Field(default=None, description="SMTP 密码")
    alert_email_to: List[str] = Field(default=[], description="告警邮件收件人列表")

    # ===== 记忆管理配置 =====
    memory_sync_enabled: bool = Field(default=True, description="启用记忆同步")
    memory_cleanup_enabled: bool = Field(default=True, description="启用记忆清理")
    memory_cleanup_days: int = Field(default=30, description="记忆清理天数阈值")

    # ===== Flower 监控配置 =====
    flower_enabled: bool = Field(default=True, description="启用 Flower 监控")
    flower_port: int = Field(default=5555, description="Flower 监控端口")
    flower_basic_auth: Optional[str] = Field(default=None, description="Flower 基础认证")

    # ===== 日志配置 =====
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    log_file_path: Optional[str] = Field(default=None, description="日志文件路径")
    log_rotation: str = Field(default="1 day", description="日志轮转")
    log_retention: str = Field(default="30 days", description="日志保留")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )


# 全局配置实例
settings = Settings()