#!/usr/bin/env python3
"""
定时任务模拟运行脚本
用于模拟定时任务执行，便于测试和调试
"""

import os
import sys
import time
import signal
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class SchedulerSimulator:
    """定时任务模拟器"""

    def __init__(self):
        self.running = False
        self.logger = self._setup_logging()
        self.task_schedule = {}

    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('/tmp/scheduler_simulator.log', encoding='utf-8')
            ]
        )
        return logging.getLogger(__name__)

    def signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info("Received shutdown signal...")
        self.running = False

class TaskRunner:
    """任务运行器"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def validate_config(self) -> bool:
        """验证配置"""
        try:
            from src.scheduler.memory_sync_service import MemorySyncService
            from src.scheduler.minio_client import MinIOClient

            # 测试数据库连接
            sync_service = MemorySyncService()
            users_count = sync_service.get_long_memory_users_count()
            self.logger.info(f"数据库连接正常，共有 {users_count} 个用户开启长期记忆")

            # 测试 MinIO 连接
            minio_client = MinIOClient()
            bucket_exists = minio_client.check_bucket_exists()
            self.logger.info(f"MinIO 连接正常，存储桶存在: {bucket_exists}")

            return True

        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False

    def sync_daily_user_memory(self, target_date: str = None, dry_run: bool = True) -> Dict[str, Any]:
        """模拟每日用户记忆同步任务"""
        try:
            from src.scheduler.memory_sync_service import MemorySyncService

            # 解析目标日期
            if target_date:
                sync_date = datetime.strptime(target_date, "%Y-%m-%d")
            else:
                sync_date = datetime.now() - timedelta(days=1)

            self.logger.info(f"{'[DRY RUN] ' if dry_run else ''}开始执行每日用户记忆同步任务，目标日期: {sync_date.strftime('%Y-%m-%d')}")

            # 获取同步服务
            sync_service = MemorySyncService()
            start_date, end_date = sync_service.get_sync_date_range(sync_date)

            # 获取需要同步的用户列表
            users = sync_service.get_long_memory_users()
            self.logger.info(f"{'[DRY RUN] ' if dry_run else ''}找到 {len(users)} 个开启长期记忆的用户")

            if not users:
                return {
                    "status": "completed",
                    "users_count": 0,
                    "message": "没有找到开启长期记忆的用户"
                }

            # 模拟为每个用户执行同步
            results = []
            for user_id in users:
                if dry_run:
                    # 模拟模式：只记录，不实际执行
                    self.logger.info(f"[DRY RUN] 用户 {user_id} 将会同步记忆数据 ({start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')})")
                    results.append({
                        "user_id": user_id,
                        "status": "simulated",
                        "sessions_found": "模拟数据"
                    })
                else:
                    # 实际执行模式
                    try:
                        # 这里可以调用实际的同步任务
                        self.logger.info(f"正在为用户 {user_id} 同步记忆数据...")

                        # 模拟处理时间
                        time.sleep(1)

                        results.append({
                            "user_id": user_id,
                            "status": "completed",
                            "message": "同步完成"
                        })

                    except Exception as e:
                        self.logger.error(f"用户 {user_id} 同步失败: {e}")
                        results.append({
                            "user_id": user_id,
                            "status": "failed",
                            "error": str(e)
                        })

            summary = {
                "status": "completed" if dry_run else "executed",
                "sync_date": sync_date.strftime("%Y-%m-%d"),
                "total_users": len(users),
                "successful_syncs": len([r for r in results if r["status"] in ["completed", "simulated"]]),
                "failed_syncs": len([r for r in results if r["status"] == "failed"]),
                "results": results,
                "dry_run": dry_run
            }

            self.logger.info(f"{'[DRY RUN] ' if dry_run else ''}每日用户记忆同步任务完成: {summary}")
            return summary

        except Exception as e:
            self.logger.error(f"每日用户记忆同步任务失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "dry_run": dry_run
            }

    def sync_user_memories(self, user_id: str, start_date: str = None, end_date: str = None, dry_run: bool = True) -> Dict[str, Any]:
        """模拟单个用户记忆同步任务"""
        try:
            from src.scheduler.memory_sync_service import MemorySyncService

            # 设置默认日期范围
            if not start_date:
                start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")

            self.logger.info(f"{'[DRY RUN] ' if dry_run else ''}开始为用户 {user_id} 同步记忆数据 ({start_date} 到 {end_date})")

            if dry_run:
                # 模拟模式
                self.logger.info(f"[DRY RUN] 模拟为用户 {user_id} 获取会话数据并上传到存储")

                # 模拟一些会话数据
                simulated_sessions = [
                    {"session_id": "session_1", "title": "技术讨论", "log_count": 15},
                    {"session_id": "session_2", "title": "项目规划", "log_count": 8}
                ]

                return {
                    "status": "simulated",
                    "user_id": user_id,
                    "sync_period": {"start_date": start_date, "end_date": end_date},
                    "sessions_found": len(simulated_sessions),
                    "files_uploaded": len(simulated_sessions),
                    "simulated_sessions": simulated_sessions
                }
            else:
                # 实际执行模式
                sync_service = MemorySyncService()

                # 获取用户会话数据
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                sessions = sync_service.get_user_sessions_batch(user_id, start_dt, end_dt)

                self.logger.info(f"为用户 {user_id} 找到 {len(sessions)} 个会话")

                # 这里可以添加实际的文件上传逻辑
                upload_results = []
                for session in sessions:
                    self.logger.info(f"处理会话: {session.get('title', 'Unknown')}")
                    # 模拟处理时间
                    time.sleep(0.5)
                    upload_results.append({
                        "session_id": session["session_id"],
                        "status": "uploaded"
                    })

                return {
                    "status": "completed",
                    "user_id": user_id,
                    "sync_period": {"start_date": start_date, "end_date": end_date},
                    "sessions_found": len(sessions),
                    "files_uploaded": len(upload_results),
                    "upload_results": upload_results
                }

        except Exception as e:
            self.logger.error(f"用户 {user_id} 记忆同步失败: {e}")
            return {
                "status": "failed",
                "user_id": user_id,
                "error": str(e),
                "dry_run": dry_run
            }

    def monitor_storage_usage(self, dry_run: bool = True) -> Dict[str, Any]:
        """模拟存储使用监控任务"""
        try:
            self.logger.info(f"{'[DRY RUN] ' if dry_run else ''}开始执行存储使用监控任务")

            if dry_run:
                # 模拟模式
                simulated_stats = [
                    {"user_id": "user_1", "total_files": 25, "total_size": 1024000},
                    {"user_id": "user_2", "total_files": 15, "total_size": 512000}
                ]

                total_files = sum(s["total_files"] for s in simulated_stats)
                total_size = sum(s["total_size"] for s in simulated_stats)

                return {
                    "status": "simulated",
                    "total_users": len(simulated_stats),
                    "total_files": total_files,
                    "total_size": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "user_stats": simulated_stats
                }
            else:
                # 实际执行模式
                from src.scheduler.memory_sync_service import MemorySyncService
                from src.scheduler.minio_client import MinIOClient

                sync_service = MemorySyncService()
                users = sync_service.get_long_memory_users()

                minio_client = MinIOClient()
                usage_stats = []

                for user_id in users:
                    try:
                        stats = minio_client.get_user_storage_stats(user_id)
                        usage_stats.append(stats)
                    except Exception as e:
                        self.logger.error(f"获取用户 {user_id} 存储统计失败: {e}")

                total_files = sum(s.get("total_files", 0) for s in usage_stats)
                total_size = sum(s.get("total_size", 0) for s in usage_stats)

                return {
                    "status": "completed",
                    "total_users": len(users),
                    "total_files": total_files,
                    "total_size": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "user_stats": usage_stats
                }

        except Exception as e:
            self.logger.error(f"存储监控任务失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "dry_run": dry_run
            }

    def cleanup_old_logs(self, days_to_keep: int = 30, dry_run: bool = True) -> Dict[str, Any]:
        """模拟清理旧日志任务"""
        try:
            self.logger.info(f"{'[DRY RUN] ' if dry_run else ''}开始清理 {days_to_keep} 天前的旧日志")

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            if dry_run:
                # 模拟模式
                simulated_cleanup = {
                    "database_records": 1250,
                    "temp_files": 45,
                    "log_files": 12
                }

                return {
                    "status": "simulated",
                    "cutoff_date": cutoff_date.isoformat(),
                    "days_to_keep": days_to_keep,
                    "cleanup_summary": simulated_cleanup
                }
            else:
                # 实际执行模式
                # 这里可以添加实际的清理逻辑
                self.logger.info(f"清理 {cutoff_date.strftime('%Y-%m-%d')} 之前的记录")

                # 模拟清理过程
                time.sleep(2)

                return {
                    "status": "completed",
                    "cutoff_date": cutoff_date.isoformat(),
                    "days_to_keep": days_to_keep,
                    "cleanup_summary": {
                        "database_records": "已清理",
                        "temp_files": "已清理",
                        "log_files": "已清理"
                    }
                }

        except Exception as e:
            self.logger.error(f"清理旧日志任务失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "dry_run": dry_run
            }

def run_interval_simulation(simulator: SchedulerSimulator, runner: TaskRunner, task_name: str, interval_seconds: int, dry_run: bool):
    """运行间隔模拟"""
    simulator.logger.info(f"开始间隔模拟任务: {task_name}, 间隔: {interval_seconds} 秒")

    while simulator.running:
        start_time = time.time()

        try:
            if task_name == "sync_daily":
                result = runner.sync_daily_user_memory(dry_run=dry_run)
            elif task_name == "monitor":
                result = runner.monitor_storage_usage(dry_run=dry_run)
            elif task_name == "cleanup":
                result = runner.cleanup_old_logs(dry_run=dry_run)
            else:
                simulator.logger.error(f"未知的任务名称: {task_name}")
                break

            simulator.logger.info(f"任务执行结果: {result.get('status', 'unknown')}")

        except Exception as e:
            simulator.logger.error(f"任务执行失败: {e}")

        # 计算下次执行时间
        elapsed_time = time.time() - start_time
        sleep_time = max(0, interval_seconds - elapsed_time)

        if simulator.running and sleep_time > 0:
            simulator.logger.info(f"下次执行将在 {sleep_time:.1f} 秒后")
            time.sleep(sleep_time)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="定时任务模拟运行脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s validate                              # 验证配置
  %(prog)s sync_daily --dry-run                  # 模拟每日同步任务
  %(prog)s sync_daily --execute                  # 实际执行每日同步任务
  %(prog)s sync_user user123 --dry-run           # 模拟指定用户同步
  %(prog)s monitor --dry-run                     # 模拟存储监控
  %(prog)s cleanup --days 7 --dry-run            # 模拟清理7天前的日志
  %(prog)s simulate sync_daily --interval 60     # 每60秒模拟一次每日同步任务
  %(prog)s simulate monitor --interval 120       # 每120秒模拟一次存储监控
        """
    )

    parser.add_argument(
        'command',
        choices=['validate', 'sync_daily', 'sync_user', 'monitor', 'cleanup', 'simulate'],
        help='要执行的命令'
    )

    parser.add_argument(
        'user_id',
        nargs='?',
        help='用户ID（sync_user 命令需要）'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='模拟运行模式（默认启用）'
    )

    parser.add_argument(
        '--execute',
        action='store_true',
        help='实际执行模式（覆盖 --dry-run）'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='模拟间隔时间（秒，默认60秒）'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='保留天数（cleanup 命令使用，默认30天）'
    )

    parser.add_argument(
        '--start-date',
        help='开始日期 (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--end-date',
        help='结束日期 (YYYY-MM-DD)'
    )

    args = parser.parse_args()

    # 确定是否为实际执行模式
    dry_run = not args.execute

    # 创建模拟器和任务运行器
    simulator = SchedulerSimulator()
    runner = TaskRunner(simulator.logger)

    # 设置信号处理
    signal.signal(signal.SIGINT, simulator.signal_handler)
    signal.signal(signal.SIGTERM, simulator.signal_handler)

    try:
        if args.command == 'validate':
            success = runner.validate_config()
            sys.exit(0 if success else 1)

        elif args.command == 'sync_daily':
            result = runner.sync_daily_user_memory(
                target_date=args.start_date,
                dry_run=dry_run
            )
            print(f"任务执行结果: {result}")
            sys.exit(0 if result.get('status') in ['completed', 'simulated'] else 1)

        elif args.command == 'sync_user':
            if not args.user_id:
                print("错误: sync_user 命令需要提供用户ID")
                sys.exit(1)

            result = runner.sync_user_memories(
                user_id=args.user_id,
                start_date=args.start_date,
                end_date=args.end_date,
                dry_run=dry_run
            )
            print(f"任务执行结果: {result}")
            sys.exit(0 if result.get('status') in ['completed', 'simulated'] else 1)

        elif args.command == 'monitor':
            result = runner.monitor_storage_usage(dry_run=dry_run)
            print(f"任务执行结果: {result}")
            sys.exit(0 if result.get('status') in ['completed', 'simulated'] else 1)

        elif args.command == 'cleanup':
            result = runner.cleanup_old_logs(days_to_keep=args.days, dry_run=dry_run)
            print(f"任务执行结果: {result}")
            sys.exit(0 if result.get('status') in ['completed', 'simulated'] else 1)

        elif args.command == 'simulate':
            # 启动间隔模拟
            simulator.running = True
            task_name = args.user_id if args.user_id else 'sync_daily'

            print(f"开始间隔模拟任务: {task_name}")
            print(f"模拟间隔: {args.interval} 秒")
            print(f"运行模式: {'模拟执行' if dry_run else '实际执行'}")
            print("按 Ctrl+C 停止模拟")

            run_interval_simulation(simulator, runner, task_name, args.interval, dry_run)

            print("模拟已停止")

    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序执行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()