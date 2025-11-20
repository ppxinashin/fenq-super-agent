"""
用户记忆设置服务层
"""

import asyncio

from src.model.crud_user_memory_setting import crud_user_memory_setting
from src.model.database import get_db
from src.minio_client.my_minio import MyMinio
from src.mq import RabbitMQClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MemorySettingService:
    """用户记忆设置服务类"""

    def __init__(self):
        self.minio_client = MyMinio()
        self.mq_client = RabbitMQClient()

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

        - 开启：仅更新状态，由定时任务消费队列统一同步
        - 关闭：将 MinIO 中该用户的记忆文件异步清理
        """
        db = next(get_db())
        try:
            crud_user_memory_setting.set_enabled(
                db=db,
                username=username,
                enabled=enabled,
                updated_by=username
            )

            if not enabled:
                self._schedule_delete_memory(username)

            logger.info(f"用户 {username} 记忆开关设置成功: {enabled}")
            return True

        except Exception as e:
            logger.error(f"设置用户记忆开关失败: {e}")
            return False
        finally:
            db.close()

    async def sync_memory(self, username: str) -> str:
        """
        手动同步长期记忆：改为将任务投递到消息队列，由定时任务统一消费。
        """
        try:
            await self.mq_client.publish_memory_task(username)
            logger.info(f"用户 {username} 记忆同步任务已投递到消息队列")
            return "已提交同步申请"
        except Exception as e:
            logger.error(f"投递记忆同步任务失败: {e}")
            return "提交同步申请失败，请稍后重试"

    def _schedule_delete_memory(self, username: str) -> None:
        """关闭长期记忆时删除 MinIO 记录，优先放入事件循环线程池避免阻塞。"""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(asyncio.to_thread(self._delete_existing_memory_files, username))
        except RuntimeError:
            # 未在事件循环中，退化为同步执行
            self._delete_existing_memory_files(username)

    def _delete_existing_memory_files(self, username: str) -> None:
        """
        删除用户现有的所有记忆文件

        Args:
            username: 用户名
        """
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
