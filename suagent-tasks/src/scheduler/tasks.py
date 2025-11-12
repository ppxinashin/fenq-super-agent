"""
Celery Tasks - Celery 任务定义
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from celery import Task

from src.scheduler.celery_app import celery_app
from src.scheduler.memory_sync_service import MemorySyncService
from src.scheduler.minio_client import MinIOClient
from src.scheduler.utils.formatter import MemoryFormatter
from src.scheduler.config import (
    MEMORY_SYNC_MAX_RETRIES,
    MEMORY_SYNC_RETRY_DELAY,
    ALERT_EMAIL_ENABLED,
    ALERT_EMAIL_TO
)

logger = logging.getLogger(__name__)

class BaseTaskWithRetry(Task):
    """带有重试机制的基础任务类"""

    autoretry_for = (Exception,)
    max_retries = MEMORY_SYNC_MAX_RETRIES
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = False

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(
            f"Task {self.name} failed: {exc}. "
            f"Attempt {self.request.retries + 1}/{self.max_retries}"
        )

        # 发送告警（如果配置了邮件通知）
        if self.request.retries >= self.max_retries - 1 and ALERT_EMAIL_ENABLED:
            self._send_alert_email(exc, task_id, args, kwargs)

    def _send_alert_email(self, exc, task_id, args, kwargs):
        """发送告警邮件"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            if not ALERT_EMAIL_TO:
                return

            subject = f"[ALERT] Memory Sync Task Failed: {self.name}"
            body = f"""
            Task: {self.name}
            Task ID: {task_id}
            Error: {exc}
            Attempt: {self.request.retries + 1}/{self.max_retries}
            Args: {args}
            Kwargs: {kwargs}
            Time: {datetime.now().isoformat()}
            """

            msg = MIMEMultipart()
            msg['From'] = "scheduler@suagent.com"
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # 这里需要根据实际的邮件配置进行发送
            logger.error(f"Alert: {subject}\n{body}")

        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")

@celery_app.task(bind=True, base=BaseTaskWithRetry)
def sync_daily_user_memory(self, target_date: str = None):
    """
    每日用户记忆同步主任务

    Args:
        target_date: 目标日期 (YYYY-MM-DD)，默认为昨天
    """
    try:
        logger.info("Starting daily user memory sync task")

        # 解析目标日期
        if target_date:
            sync_date = datetime.strptime(target_date, "%Y-%m-%d")
        else:
            sync_date = datetime.now() - timedelta(days=1)

        logger.info(f"Syncing memory for date: {sync_date.strftime('%Y-%m-%d')}")

        # 获取同步服务
        sync_service = MemorySyncService()
        start_date, end_date = sync_service.get_sync_date_range(sync_date)

        # 获取需要同步的用户列表
        users = sync_service.get_long_memory_users()
        logger.info(f"Found {len(users)} users with long memory enabled")

        if not users:
            logger.info("No users with long memory enabled. Task completed.")
            return {"status": "completed", "users_count": 0, "message": "No users found"}

        # 为每个用户创建子任务
        task_results = []
        for user_id in users:
            try:
                # 异步执行用户记忆同步
                result = sync_user_memories.delay(
                    user_id=user_id,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat()
                )
                task_results.append({
                    "user_id": user_id,
                    "task_id": result.id,
                    "status": "submitted"
                })

            except Exception as e:
                logger.error(f"Failed to submit task for user {user_id}: {e}")
                task_results.append({
                    "user_id": user_id,
                    "task_id": None,
                    "status": "failed",
                    "error": str(e)
                })

        summary = {
            "status": "submitted",
            "sync_date": sync_date.strftime("%Y-%m-%d"),
            "total_users": len(users),
            "submitted_tasks": len([r for r in task_results if r["status"] == "submitted"]),
            "failed_tasks": len([r for r in task_results if r["status"] == "failed"]),
            "task_results": task_results
        }

        logger.info(f"Daily memory sync tasks submitted: {summary}")
        return summary

    except Exception as exc:
        logger.error(f"Daily memory sync task failed: {exc}")
        raise self.retry(countdown=MEMORY_SYNC_RETRY_DELAY, exc=exc)

@celery_app.task(bind=True, base=BaseTaskWithRetry)
def sync_user_memories(self, user_id: str, start_date: str, end_date: str):
    """
    同步单个用户的记忆数据

    Args:
        user_id: 用户ID
        start_date: 开始日期 (ISO format)
        end_date: 结束日期 (ISO format)
    """
    try:
        logger.info(f"Starting memory sync for user: {user_id}")

        # 转换日期格式
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # 初始化服务
        sync_service = MemorySyncService()
        minio_client = MinIOClient()
        formatter = MemoryFormatter()

        # 获取用户会话数据
        sessions = sync_service.get_user_sessions_batch(user_id, start_dt, end_dt)
        logger.info(f"Found {len(sessions)} sessions for user {user_id}")

        if not sessions:
            logger.info(f"No sessions found for user {user_id} in the specified date range")
            return {
                "status": "completed",
                "user_id": user_id,
                "sessions_count": 0,
                "files_uploaded": 0,
                "message": "No sessions found"
            }

        # 处理每个会话
        upload_results = []
        total_uploaded = 0

        for session_data in sessions:
            try:
                # 验证会话数据
                if not sync_service.validate_session_data(session_data):
                    logger.warning(f"Invalid session data for session {session_data.get('session_id')}")
                    continue

                # 格式化内容为 Markdown
                markdown_content = formatter.format_session_to_markdown(
                    session_data['logs'],
                    session_data['title']
                )

                # 验证格式化后的内容
                if not formatter.validate_content(markdown_content):
                    logger.warning(f"Invalid formatted content for session {session_data['session_id']}")
                    continue

                # 生成文件名
                session_date = session_data['created_at']
                filename = formatter.generate_filename(session_data['title'], session_date)

                # 上传到 MinIO
                upload_result = minio_client.upload_file(
                    user_id=user_id,
                    filename=filename,
                    content=markdown_content,
                    content_type="text/markdown"
                )

                upload_results.append({
                    "session_id": session_data['session_id'],
                    "filename": filename,
                    "upload_result": upload_result,
                    "log_count": len(session_data['logs']),
                    "content_size": formatter.calculate_size(markdown_content)
                })

                total_uploaded += 1
                logger.info(f"Uploaded memory file: {filename} for user {user_id}")

            except Exception as e:
                logger.error(f"Failed to process session {session_data.get('session_id')}: {e}")
                upload_results.append({
                    "session_id": session_data.get('session_id'),
                    "error": str(e)
                })

        # 获取用户存储统计
        storage_stats = minio_client.get_user_storage_stats(user_id)

        result = {
            "status": "completed",
            "user_id": user_id,
            "sync_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "sessions_found": len(sessions),
            "files_uploaded": total_uploaded,
            "failed_uploads": len(sessions) - total_uploaded,
            "upload_results": upload_results,
            "storage_stats": storage_stats
        }

        logger.info(f"Memory sync completed for user {user_id}: {result}")
        return result

    except Exception as exc:
        logger.error(f"User memory sync failed for {user_id}: {exc}")
        raise self.retry(countdown=MEMORY_SYNC_RETRY_DELAY, exc=exc)

@celery_app.task(bind=True, base=BaseTaskWithRetry)
def upload_session_memory(
    self,
    user_id: str,
    session_title: str,
    session_logs: List[Dict[str, Any]],
    filename: str = None
):
    """
    上传单个会话记忆数据

    Args:
        user_id: 用户ID
        session_title: 会话标题
        session_logs: 会话日志列表
        filename: 自定义文件名
    """
    try:
        logger.info(f"Uploading session memory for user: {user_id}")

        # 初始化服务
        minio_client = MinIOClient()
        formatter = MemoryFormatter()

        # 格式化内容
        markdown_content = formatter.format_session_to_markdown(session_logs, session_title)

        # 验证内容
        if not formatter.validate_content(markdown_content):
            raise ValueError("Invalid session content after formatting")

        # 生成文件名
        if filename is None:
            # 从日志中获取最新时间作为文件日期
            latest_time = max(log['created_at'] for log in session_logs)
            filename = formatter.generate_filename(session_title, latest_time)

        # 上传文件
        upload_result = minio_client.upload_file(
            user_id=user_id,
            filename=filename,
            content=markdown_content,
            content_type="text/markdown"
        )

        result = {
            "status": "completed",
            "user_id": user_id,
            "session_title": session_title,
            "filename": filename,
            "log_count": len(session_logs),
            "content_size": formatter.calculate_size(markdown_content),
            "upload_result": upload_result
        }

        logger.info(f"Session memory uploaded successfully: {result}")
        return result

    except Exception as exc:
        logger.error(f"Session memory upload failed: {exc}")
        raise self.retry(countdown=MEMORY_SYNC_RETRY_DELAY, exc=exc)

@celery_app.task(bind=True, base=BaseTaskWithRetry)
def cleanup_old_logs(self, days_to_keep: int = 30):
    """
    清理旧的日志记录

    Args:
        days_to_keep: 保留天数
    """
    try:
        logger.info(f"Starting cleanup of logs older than {days_to_keep} days")

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        # 这里可以添加清理逻辑
        # 例如：删除数据库中的旧记录、清理临时文件等

        result = {
            "status": "completed",
            "cutoff_date": cutoff_date.isoformat(),
            "days_to_keep": days_to_keep,
            "message": "Cleanup task completed"
        }

        logger.info(f"Cleanup task completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"Cleanup task failed: {exc}")
        raise self.retry(countdown=MEMORY_SYNC_RETRY_DELAY, exc=exc)

@celery_app.task(bind=True)
def monitor_storage_usage(self):
    """
    监控存储使用情况
    """
    try:
        logger.info("Starting storage usage monitoring")

        # 获取所有开启长期记忆的用户
        sync_service = MemorySyncService()
        users = sync_service.get_long_memory_users()

        minio_client = MinIOClient()
        usage_stats = []

        total_users = len(users)
        total_files = 0
        total_size = 0

        for user_id in users:
            try:
                stats = minio_client.get_user_storage_stats(user_id)
                usage_stats.append(stats)

                total_files += stats.get("total_files", 0)
                total_size += stats.get("total_size", 0)

            except Exception as e:
                logger.error(f"Failed to get stats for user {user_id}: {e}")
                usage_stats.append({
                    "user_id": user_id,
                    "error": str(e)
                })

        result = {
            "status": "completed",
            "total_users": total_users,
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "usage_stats": usage_stats,
            "monitoring_time": datetime.now().isoformat()
        }

        logger.info(f"Storage monitoring completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"Storage monitoring failed: {exc}")
        raise