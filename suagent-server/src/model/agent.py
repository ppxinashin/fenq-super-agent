from sqlalchemy import Column, String, Text, Boolean, JSON, Index
from src.model.base import Base


class Agent(Base):
    """智能体表"""
    __tablename__ = "agents"

    agent_id = Column(String(100), unique=True, nullable=False, comment="智能体英文名(唯一标识)")
    agent_name = Column(String(100), nullable=False, comment="智能体中文名")
    description = Column(Text, comment="智能体介绍")
    system_prompt = Column(Text, nullable=False, comment="系统提示词")
    tools = Column(JSON, default=list, comment="绑定工具清单(JSON列表)")
    mcp_enabled = Column(Boolean, default=False, comment="MCP开关")
    mcp_servers = Column(JSON, default=dict, comment="MCP服务器列表(JSON对象)")

    # 创建索引
    __table_args__ = (
        Index('idx_agent_id', 'agent_id'),
        Index('idx_agent_name', 'agent_name'),
    )
    
    def __repr__(self):
        return f"<Agent(id={self.id}, agent_id={self.agent_id}, agent_name={self.agent_name})>"

