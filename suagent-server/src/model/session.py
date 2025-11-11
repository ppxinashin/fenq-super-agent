from sqlalchemy import Column, String, BigInteger, Index
from src.model.base import Base


class Session(Base):
    """会话表"""
    __tablename__ = "sessions"
    
    agent_id = Column(String(100), nullable=False, comment="智能体英文名")
    session_id = Column(BigInteger, nullable=False, unique=True, comment="会话ID")
    title = Column(String(200), nullable=True, comment="会话标题")
    
    # 创建索引
    __table_args__ = (
        Index('idx_session_agent_id', 'agent_id'),
        Index('idx_session_session_id', 'session_id'),
        Index('idx_session_agent_id_session_id', 'agent_id', 'session_id'),
    )
    
    def __repr__(self):
        return f"<Session(id={self.id}, session_id={self.session_id}, agent_id={self.agent_id}, title={self.title})>"
