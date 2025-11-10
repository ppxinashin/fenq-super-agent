from sqlalchemy import Column, String, Text, Index, BigInteger
from src.model.base import Base


class SessionLog(Base):
    """会话日志表"""
    __tablename__ = "session_logs"
    
    session_id = Column(BigInteger, nullable=False, comment="会话ID")
    agent_id = Column(String(100), nullable=False, comment="智能体英文名")
    role = Column(String(20), nullable=False, comment="角色(user/assistant/system)")
    content = Column(Text, nullable=False, comment="消息内容")
    
    # 创建索引和约束
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_session_id_agent_id', 'session_id', 'agent_id'),
        Index('idx_session_id_created_at', 'session_id', 'created_at'),
        Index('idx_agent_id', 'agent_id'),
    )
    
    def __repr__(self):
        return f"<SessionLog(id={self.id}, session_id={self.session_id}, agent_id={self.agent_id}, role={self.role})>"

