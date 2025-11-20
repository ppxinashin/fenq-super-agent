"""用户记忆设置服务层"""

import asyncio
import time

from src.model.crud_user_memory_setting import crud_user_memory_setting
from src.model.crud_session_log import CRUDSessionLog
from src.model.database import get_db_session
from src.model.session_log import SessionLog
from src.minio_client.my_minio import MyMinio
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MemorySettingService:
    """用户记忆设置服务类"""

    def __init__(self):
        self.minio_client = MyMinio()
        self.session_log_crud = CRUDSessionLog(SessionLog)

    def get_memory_status(self, username: str) -> bool:
        """获取用户记忆开关状态"""
        try:
            with get_db_session() as db:
                return crud_user_memory_setting.is_enabled(db=db, username=username)
        except Exception as e:
            logger.error(f"获取用户记忆状态失败: {e}")
            return False

    def set_memory_setting(self, username: str, enabled: bool) -> bool:
        """设置用户记忆开关"""
        try:
            with get_db_session() as db:
                crud_user_memory_setting.set_enabled(
                    db=db,
                    username=username,
                    enabled=enabled,
                    updated_by=username
                )

            if enabled:
                # 如果开启记忆，异步执行记忆文档上传
                asyncio.create_task(self.sync_user_memory(username))

            logger.info(f"用户 {username} 记忆开关设置成功: {enabled}")
            return True

        except Exception as e:
            logger.error(f"设置用户记忆开关失败: {e}")
            return False

    def sync_memory(self, username: str) -> str:
        """手动同步长期记忆（用于外部触发，立即异步调度）"""
        try:
            asyncio.create_task(self.sync_user_memory(username))
            logger.info(f"用户 {username} 记忆同步已启动")
            return "记忆同步已启动，正在后台处理"
        except Exception as e:
            logger.error(f"同步用户记忆失败: {e}")
            return "同步记忆失败，请稍后重试"

    async def sync_user_memory(self, username: str) -> None:
        """对外暴露的同步接口，供消费者/调度任务调用"""
        await asyncio.to_thread(self._upload_memory_document, username)

    def _upload_memory_document(self, username: str):
        """上传记忆文档到 MinIO，幂等：先清空后重建"""
        try:
            logger.info(f"开始为用户 {username} 上传记忆文档")

            with get_db_session() as db:
                # 先删除现有的记忆文件，保证幂等
                self._delete_existing_memory_files(username)

                # 获取该用户的所有会话日志
                session_logs = self.session_log_crud.get_by_username(
                    db=db,
                    username=username
                )

                if not session_logs:
                    logger.info(f"用户 {username} 没有聊天记录，跳过记忆文档上传")
                    return

                # 格式化聊天记录为 Markdown
                memory_content = '\n\n'.join([
                    f'**{session.role}**\n\n{session.content}'
                    for session in session_logs
                ])

                timestamp = int(time.time())
                object_name = f"memory/{username}/{timestamp}.md"

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
            logger.error(f"上传记忆文档异常: {e}")

    def _delete_existing_memory_files(self, username: str):
        """删除用户现有的所有记忆文件"""
        try:
            memory_prefix = f"memory/{username}/"
            delete_count = 0

            for obj in self.minio_client.list_objects(prefix=memory_prefix, recursive=True):
                self.minio_client.remove_object(obj.object_name)
                delete_count += 1

            logger.info(f"用户 {username} 删除了 {delete_count} 个记忆文件")

        except Exception as e:
            logger.error(f"删除用户 {username} 记忆文件失败: {e}")


# 创建服务实例
memory_setting_service = MemorySettingService()
