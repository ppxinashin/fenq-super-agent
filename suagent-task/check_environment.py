#!/usr/bin/env python3
"""
环境检查脚本 - 针对定时任务/消息队列/存储三件套
"""

import os
import sys
from importlib import import_module
from pathlib import Path


REQUIRED_PACKAGES = {
    "pydantic": "Pydantic",
    "pydantic_settings": "pydantic-settings",
    "sqlalchemy": "SQLAlchemy",
    "psycopg": "psycopg",
    "apscheduler": "APScheduler",
    "aio_pika": "aio-pika",
    "minio": "MinIO",
    "loguru": "Loguru",
}


def _status_line(ok: bool, message: str) -> None:
    icon = "✅" if ok else "❌"
    print(f"{icon} {message}")


def check_basic_runtime() -> bool:
    print("🔍 环境检查")
    print("=" * 40)
    print(f"🐍 Python路径: {sys.executable}")
    print(f"🐍 Python版本: {sys.version.split()[0]}")
    print(f"📁 当前工作目录: {os.getcwd()}")
    return True


def ensure_repo_root() -> bool:
    repo_root = Path(__file__).resolve().parent
    cwd = Path.cwd().resolve()
    ok = cwd == repo_root
    _status_line(ok, f"工作目录在仓库根目录 ({repo_root})")
    return ok


def check_required_packages() -> bool:
    print("\n📦 依赖检查")
    ok = True
    for module_name, label in REQUIRED_PACKAGES.items():
        try:
            import_module(module_name)
            _status_line(True, label)
        except Exception as exc:
            ok = False
            _status_line(False, f"{label} 未安装: {exc}")
    return ok


def show_runtime_settings() -> None:
    from src.config.settings import settings

    print("\n⚙️  关键配置")
    print(f"- APP_NAME={settings.app_name} v{settings.app_version}")
    print(f"- Postgres={settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    print(f"- RabbitMQ={settings.rabbitmq_host}:{settings.rabbitmq_port} vhost={settings.rabbitmq_virtual_host}")
    print(f"- Scheduler timezone={settings.scheduler_timezone} interval(min)={settings.memory_sync_interval_minutes}")
    print(f"- MinIO endpoint={settings.minio_endpoint} bucket={settings.minio_bucket}")


def main() -> None:
    ok = check_basic_runtime()
    ok = ensure_repo_root() and ok
    ok = check_required_packages() and ok

    if ok:
        show_runtime_settings()
        print("\n🎉 环境检查完成 - 可以运行定时任务调度器")
        sys.exit(0)
    else:
        print("\n❌ 环境缺少依赖或目录不正确，请先修复")
        sys.exit(1)


if __name__ == "__main__":
    main()
