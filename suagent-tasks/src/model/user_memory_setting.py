from sqlalchemy import Column, String, Boolean, Index
from src.model.base import Base


class UserMemorySetting(Base):
    """用户长期记忆设置表"""
    __tablename__ = "user_memory_settings"
    
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    enabled = Column(Boolean, default=False, nullable=False, comment="长期记忆开关(true=开启, false=关闭)")
    
    # 创建索引
    __table_args__ = (
        Index('idx_user_memory_settings_username', 'username'),
    )
    
    def __repr__(self):
        return f"<UserMemorySetting(id={self.id}, username={self.username}, enabled={self.enabled})>"

