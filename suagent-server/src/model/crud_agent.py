"""
Agent模型CRUD操作
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from src.model.crud_base import CRUDBase
from src.model.agent import Agent


class CRUDAgent(CRUDBase[Agent]):
    """Agent CRUD操作类"""
    
    def create_agent(
        self,
        db: Session,
        agent_id: str,
        agent_name: str,
        system_prompt: str,
        description: Optional[str] = None,
        tools: Optional[List[str]] = None,
        mcp_enabled: bool = False,
        mcp_servers: Optional[Dict[str, Any]] = None,
        created_by: str = "system"
    ) -> Agent:
        """
        创建智能体
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名(唯一标识)
            agent_name: 智能体中文名
            system_prompt: 系统提示词
            description: 智能体介绍
            tools: 绑定工具清单
            mcp_enabled: MCP开关
            mcp_servers: MCP服务器列表
            created_by: 创建人
            
        Returns:
            创建的智能体对象
        """
        agent_data = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "system_prompt": system_prompt,
            "description": description,
            "tools": tools or [],
            "mcp_enabled": mcp_enabled,
            "mcp_servers": mcp_servers or {}
        }
        
        return self.create(db=db, obj_in=agent_data, created_by=created_by)
    
    def get_by_agent_id(self, db: Session, agent_id: str) -> Optional[Agent]:
        """
        根据agent_id获取智能体
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名
            
        Returns:
            智能体对象，未找到返回None
        """
        return db.query(Agent).filter(
            Agent.agent_id == agent_id,
            Agent.is_deleted == False
        ).first()
    
    def get_by_name(self, db: Session, agent_name: str) -> Optional[Agent]:
        """
        根据智能体中文名获取智能体
        
        Args:
            db: 数据库会话
            agent_name: 智能体中文名
            
        Returns:
            智能体对象，未找到返回None
        """
        return db.query(Agent).filter(
            Agent.agent_name == agent_name,
            Agent.is_deleted == False
        ).first()
    
    def search_by_name(self, db: Session, keyword: str, limit: int = 10) -> List[Agent]:
        """
        按名称搜索智能体（模糊查询）
        
        Args:
            db: 数据库会话
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            智能体列表
        """
        return db.query(Agent).filter(
            Agent.agent_name.like(f"%{keyword}%"),
            Agent.is_deleted == False
        ).limit(limit).all()
    
    def update_tools(
        self,
        db: Session,
        agent_id: str,
        tools: List[str],
        updated_by: str = "system"
    ) -> Optional[Agent]:
        """
        更新智能体工具列表
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名
            tools: 工具列表
            updated_by: 更新人
            
        Returns:
            更新后的智能体对象，未找到返回None
        """
        agent = self.get_by_agent_id(db=db, agent_id=agent_id)
        if not agent:
            return None
        
        update_data = {"tools": tools}
        return self.update(db=db, db_obj=agent, obj_in=update_data, updated_by=updated_by)
    
    def update_mcp_config(
        self,
        db: Session,
        agent_id: str,
        mcp_enabled: bool,
        mcp_servers: Optional[Dict[str, Any]] = None,
        updated_by: str = "system"
    ) -> Optional[Agent]:
        """
        更新智能体MCP配置
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名
            mcp_enabled: MCP开关
            mcp_servers: MCP服务器列表
            updated_by: 更新人
            
        Returns:
            更新后的智能体对象，未找到返回None
        """
        agent = self.get_by_agent_id(db=db, agent_id=agent_id)
        if not agent:
            return None
        
        update_data = {
            "mcp_enabled": mcp_enabled
        }
        if mcp_servers is not None:
            update_data["mcp_servers"] = mcp_servers
        
        return self.update(db=db, db_obj=agent, obj_in=update_data, updated_by=updated_by)


# 创建全局CRUD实例
crud_agent = CRUDAgent(Agent)

