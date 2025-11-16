"""
用户记忆设置服务层
"""

import asyncio
import time
from typing import Optional
from sqlalchemy.orm import Session
from src.model.crud_user_memory_setting import crud_user_memory_setting
from src.model.crud_session_log import CRUDSessionLog
from src.model.database import get_db
from src.model.session_log import SessionLog
from src.minio_client.my_minio import MyMinio
from src.utils.logger import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


class MemorySettingService:
    """用户记忆设置服务类"""

    def __init__(self):
        self.minio_client = MyMinio()
        self.session_log_crud = CRUDSessionLog(SessionLog)

    def get_memory_status(self, username: str) -> bool:
        """
        获取用户记忆开关状态

        Args:
            username: 用户名

        Returns:
            bool: 记忆开关状态，默认关闭
        """
        db = next(get_db())
        try:
            return crud_user_memory_setting.is_enabled(db=db, username=username)
        except Exception as e:
            logger.error(f"获取用户记忆状态失败: {e}")
            return False
        finally:
            db.close()

    def set_memory_setting(self, username: str, enabled: bool) -> bool:
        """
        设置用户记忆开关

        Args:
            username: 用户名
            enabled: 开关状态

        Returns:
            bool: 设置是否成功
        """
        db = next(get_db())
        try:
            # 设置记忆开关
            setting = crud_user_memory_setting.set_enabled(
                db=db,
                username=username,
                enabled=enabled,
                updated_by=username
            )

            if enabled:
                # 如果开启记忆，异步执行记忆文档上传
                asyncio.create_task(self._upload_memory_document(username))

            logger.info(f"用户 {username} 记忆开关设置成功: {enabled}")
            return True

        except Exception as e:
            logger.error(f"设置用户记忆开关失败: {e}")
            return False
        finally:
            db.close()

    async def _upload_memory_document(self, username: str):
        """
        异步上传记忆文档到MinIO

        Args:
            username: 用户名
        """
        try:
            logger.info(f"开始为用户 {username} 上传记忆文档")

            # 查询用户的聊天记录
            db = next(get_db())
            try:
                # 获取该用户的所有会话日志
                session_logs = self.session_log_crud.get_by_username(
                    db=db,
                    username=username
                )

                if not session_logs:
                    logger.info(f"用户 {username} 没有聊天记录，跳过记忆文档上传")
                    return

                # 格式化聊天记录为Markdown格式
                memory_content = '\n\n'.join([
                    f'**{session.role}**\n\n{session.content}'
                    for session in session_logs
                ])

                # 生成文档路径：memory/user_id/unix时间戳.md
                timestamp = int(time.time())
                object_name = f"memory/{username}/{timestamp}.md"

                # 上传到MinIO
                from io import BytesIO
                data_stream = BytesIO(memory_content.encode('utf-8'))
                self.minio_client.put_object(
                    object_name=object_name,
                    data=data_stream,
                    length=len(memory_content.encode('utf-8')),
                    content_type='text/markdown'
                )

                logger.info(f"用户 {username} 记忆文档上传成功: {object_name}")

            except Exception as e:
                logger.error(f"用户 {username} 记忆文档上传失败: {e}")
            finally:
                db.close()

        except Exception as e:
            logger.error(f"异步上传记忆文档异常: {e}")


# 创建服务实例
memory_setting_service = MemorySettingService()