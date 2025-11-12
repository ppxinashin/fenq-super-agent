#!/usr/bin/env python3
"""
Memory Sync Scheduler Main Entry Point
定时记忆同步系统主入口文件
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """设置日志配置"""
    from src.config.settings import settings

    log_level = settings.log_level.upper()
    log_format = settings.log_format

    handlers = [logging.StreamHandler(sys.stdout)]

    # 如果配置了日志文件路径，添加文件处理器
    if settings.log_file_path:
        handlers.append(
            logging.FileHandler(settings.log_file_path, encoding='utf-8')
        )
    else:
        # 默认日志文件路径
        handlers.append(
            logging.FileHandler('/var/log/celery/scheduler.log', encoding='utf-8')
        )

    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=handlers
    )

def start_worker():
    """启动 Celery Worker"""
    from src.scheduler.celery_app import celery_app
    from src.config.settings import settings

    # 启动参数
    worker_args = [
        'worker',
        '--loglevel=' + settings.log_level,
        '--queues=memory_sync,storage,maintenance',
        '--concurrency=' + str(settings.celery_worker_concurrency),
        '--max-tasks-per-child=' + str(settings.celery_worker_max_tasks_per_child),
        '--pidfile=/var/run/celery/worker.pid',
        '--logfile=/var/log/celery/worker.log',
        '--statedb=/var/run/celery/worker.state'
    ]

    celery_app.worker_main(worker_args)

def start_beat():
    """启动 Celery Beat"""
    from src.scheduler.celery_app import celery_app
    from src.config.settings import settings

    # 启动参数
    beat_args = [
        'beat',
        '--loglevel=' + settings.log_level,
        '--schedule=/tmp/celery/celerybeat-schedule',
        '--pidfile=/var/run/celery/beat.pid',
        '--logfile=/var/log/celery/beat.log'
    ]

    celery_app.start(beat_args)

def start_flower():
    """启动 Celery Flower 监控"""
    from src.scheduler.celery_app import celery_app
    from src.config.settings import settings

    if not settings.flower_enabled:
        print("Flower monitoring is disabled")
        return

    # 启动参数
    flower_args = [
        'flower',
        '--port=' + str(settings.flower_port),
        '--pidfile=/var/run/celery/flower.pid'
    ]

    if settings.flower_basic_auth:
        flower_args.append('--basic_auth=' + settings.flower_basic_auth)

    celery_app.start(flower_args)

def validate_config():
    """验证配置"""
    try:
        from src.scheduler.celery_app import startup_validation

        print("Validating scheduler configuration...")
        result = startup_validation.delay()
        print("Configuration validation completed successfully!")
        return True

    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False

def run_task(task_name: str, *args, **kwargs):
    """运行指定任务"""
    from src.scheduler.tasks import sync_daily_user_memory, sync_user_memories, monitor_storage_usage

    task_map = {
        'sync_daily': sync_daily_user_memory,
        'sync_user': sync_user_memories,
        'monitor': monitor_storage_usage
    }

    if task_name not in task_map:
        print(f"Unknown task: {task_name}")
        print(f"Available tasks: {list(task_map.keys())}")
        return False

    try:
        task = task_map[task_name]
        if args or kwargs:
            result = task.delay(*args, **kwargs)
        else:
            result = task.delay()

        print(f"Task '{task_name}' submitted with ID: {result.id}")
        return True

    except Exception as e:
        print(f"Failed to submit task '{task_name}': {e}")
        return False

def show_status():
    """显示系统状态"""
    try:
        from src.scheduler.memory_sync_service import MemorySyncService
        from src.scheduler.minio_client import MinIOClient
        from src.config.settings import settings

        print("=== Memory Sync Scheduler Status ===\n")

        # 检查数据库连接
        sync_service = MemorySyncService()
        users_count = sync_service.get_long_memory_users_count()
        print(f"✓ Database connection: OK")
        print(f"✓ Users with long memory enabled: {users_count}")

        # 检查 MinIO 连接
        minio_client = MinIOClient()
        bucket_exists = minio_client.check_bucket_exists()
        print(f"✓ MinIO connection: OK")
        print(f"✓ MinIO bucket exists: {bucket_exists}")

        print(f"\n=== Configuration Summary ===")
        print(f"App Name: {settings.app_name}")
        print(f"Version: {settings.app_version}")
        print(f"Debug Mode: {settings.debug}")
        print(f"Broker URL: {settings.celery_broker_url}")
        print(f"Result Backend: {settings.celery_result_backend}")
        print(f"Database URL: {settings.database_url}")
        print(f"MinIO Endpoint: {settings.minio_endpoint}")
        print(f"Memory Bucket: {settings.minio_memory_bucket}")
        print(f"Memory Sync Enabled: {settings.memory_sync_enabled}")
        print(f"Flower Enabled: {settings.flower_enabled}")

        return True

    except Exception as e:
        print(f"Status check failed: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Memory Sync Scheduler - 定时记忆同步系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s worker                    # 启动 Celery Worker
  %(prog)s beat                      # 启动 Celery Beat
  %(prog)s flower                    # 启动 Flower 监控
  %(prog)s validate                  # 验证配置
  %(prog)s status                    # 显示状态
  %(prog)s task sync_daily           # 运行每日同步任务
  %(prog)s task sync_user user123    # 同步指定用户
  %(prog)s task monitor              # 运行监控任务
        """
    )

    parser.add_argument(
        'command',
        choices=['worker', 'beat', 'flower', 'validate', 'status', 'task'],
        help='要执行的命令'
    )

    parser.add_argument(
        'task_name',
        nargs='?',
        choices=['sync_daily', 'sync_user', 'monitor'],
        help='任务名称（当命令为 task 时使用）'
    )

    parser.add_argument(
        'task_args',
        nargs='*',
        help='任务参数'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别'
    )

    args = parser.parse_args()

    # 设置日志
    os.environ["LOG_LEVEL"] = args.log_level
    setup_logging()

    # 确保必要的目录存在
    os.makedirs("/tmp/celery", exist_ok=True)
    os.makedirs("/var/log/celery", exist_ok=True)
    os.makedirs("/var/run/celery", exist_ok=True)

    # 执行命令
    try:
        if args.command == 'worker':
            print("Starting Celery Worker...")
            start_worker()

        elif args.command == 'beat':
            print("Starting Celery Beat...")
            start_beat()

        elif args.command == 'flower':
            print("Starting Celery Flower...")
            start_flower()

        elif args.command == 'validate':
            success = validate_config()
            sys.exit(0 if success else 1)

        elif args.command == 'status':
            success = show_status()
            sys.exit(0 if success else 1)

        elif args.command == 'task':
            if not args.task_name:
                print("Error: Task name is required when using 'task' command")
                parser.print_help()
                sys.exit(1)

            if args.task_name == 'sync_daily':
                success = run_task('sync_daily')
            elif args.task_name == 'sync_user':
                if not args.task_args:
                    print("Error: User ID is required for sync_user task")
                    sys.exit(1)
                success = run_task('sync_user', args.task_args[0])
            elif args.task_name == 'monitor':
                success = run_task('monitor')
            else:
                print(f"Unknown task: {args.task_name}")
                sys.exit(1)

            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()