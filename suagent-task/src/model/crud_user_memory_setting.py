"""UserMemorySetting 模型 CRUD 操作"""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.model.crud_base import CRUDBase
from src.model.user_memory_setting import UserMemorySetting


class CRUDUserMemorySetting(CRUDBase[UserMemorySetting]):
    """UserMemorySetting CRUD 操作类"""

    def get_by_username(self, db: Session, username: str) -> Optional[UserMemorySetting]:
        """根据用户名获取设置"""
        return db.query(UserMemorySetting).filter(
            UserMemorySetting.username == username,
            UserMemorySetting.is_deleted == False
        ).first()

    def is_enabled(self, db: Session, username: str) -> bool:
        """检查用户是否开启长期记忆"""
        setting = self.get_by_username(db=db, username=username)
        if not setting:
            return False  # 默认关闭
        return setting.enabled

    def list_enabled_usernames(self, db: Session) -> List[str]:
        """获取所有已开启长期记忆的用户名列表"""
        rows = db.query(UserMemorySetting.username).filter(
            UserMemorySetting.enabled == True,
            UserMemorySetting.is_deleted == False
        ).all()
        return [row[0] for row in rows]

    def set_enabled(
        self,
        db: Session,
        username: str,
        enabled: bool,
        updated_by: str = "system"
    ) -> UserMemorySetting:
        """设置用户长期记忆开关"""
        setting = self.get_by_username(db=db, username=username)

        if setting:
            update_data = {"enabled": enabled}
            return self.update(db=db, db_obj=setting, obj_in=update_data, updated_by=updated_by)

        setting_data = {
            "username": username,
            "enabled": enabled
        }
        return self.create(db=db, obj_in=setting_data, created_by=updated_by)


# 创建全局 CRUD 实例
crud_user_memory_setting = CRUDUserMemorySetting(UserMemorySetting)
