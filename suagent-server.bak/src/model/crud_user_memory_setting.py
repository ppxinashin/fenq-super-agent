"""
UserMemorySetting模型CRUD操作
"""

from typing import Optional
from sqlalchemy.orm import Session
from src.model.crud_base import CRUDBase
from src.model.user_memory_setting import UserMemorySetting


class CRUDUserMemorySetting(CRUDBase[UserMemorySetting]):
    """UserMemorySetting CRUD操作类"""
    
    def get_by_username(self, db: Session, username: str) -> Optional[UserMemorySetting]:
        """
        根据用户名获取设置
        
        Args:
            db: 数据库会话
            username: 用户名
            
        Returns:
            设置对象，未找到返回None
        """
        return db.query(UserMemorySetting).filter(
            UserMemorySetting.username == username,
            UserMemorySetting.is_deleted == False
        ).first()
    
    def is_enabled(self, db: Session, username: str) -> bool:
        """
        检查用户是否开启长期记忆
        
        Args:
            db: 数据库会话
            username: 用户名
            
        Returns:
            是否开启长期记忆
        """
        setting = self.get_by_username(db=db, username=username)
        if not setting:
            return False  # 默认关闭
        return setting.enabled
    
    def set_enabled(
        self,
        db: Session,
        username: str,
        enabled: bool,
        updated_by: str = "system"
    ) -> UserMemorySetting:
        """
        设置用户长期记忆开关
        
        Args:
            db: 数据库会话
            username: 用户名
            enabled: 是否开启
            updated_by: 更新人
            
        Returns:
            设置对象
        """
        setting = self.get_by_username(db=db, username=username)
        
        if setting:
            # 更新现有设置
            update_data = {"enabled": enabled}
            return self.update(db=db, db_obj=setting, obj_in=update_data, updated_by=updated_by)
        else:
            # 创建新设置
            setting_data = {
                "username": username,
                "enabled": enabled
            }
            return self.create(db=db, obj_in=setting_data, created_by=updated_by)


# 创建全局CRUD实例
crud_user_memory_setting = CRUDUserMemorySetting(UserMemorySetting)

