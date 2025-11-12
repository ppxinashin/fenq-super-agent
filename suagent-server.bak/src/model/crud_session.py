"""
Session模型CRUD操作
"""

from typing import Optional, List
from sqlalchemy.orm import Session as DBSession
from src.model.crud_base import CRUDBase
from src.model.session import Session


class CRUDSession(CRUDBase[Session]):
    """Session CRUD操作类"""
    
    def create_session(
        self,
        db: DBSession,
        agent_id: str,
        session_id: int,
        title: Optional[str] = None,
        created_by: str = "system"
    ) -> Session:
        """
        创建会话
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名
            session_id: 会话ID
            title: 会话标题
            created_by: 创建人
            
        Returns:
            创建的会话对象
        """
        session_data = {
            "agent_id": agent_id,
            "session_id": session_id,
            "title": title
        }
        
        return self.create(db=db, obj_in=session_data, created_by=created_by)
    
    def get_by_session_id(self, db: DBSession, session_id: int) -> Optional[Session]:
        """
        根据session_id获取会话
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            
        Returns:
            会话对象，未找到返回None
        """
        return db.query(Session).filter(
            Session.session_id == session_id,
            Session.is_deleted == False
        ).first()
    
    def get_by_agent_id(
        self, 
        db: DBSession, 
        agent_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Session]:
        """
        根据智能体ID获取所有会话
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名
            skip: 跳过记录数
            limit: 返回记录数限制
            
        Returns:
            会话列表
        """
        return db.query(Session).filter(
            Session.agent_id == agent_id,
            Session.is_deleted == False
        ).order_by(Session.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_agent_and_user(
        self,
        db: DBSession,
        agent_id: str,
        created_by: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Session]:
        """
        根据智能体ID和创建用户获取会话
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名
            created_by: 创建用户ID
            skip: 跳过记录数
            limit: 返回记录数限制
            
        Returns:
            会话列表
        """
        return db.query(Session).filter(
            Session.agent_id == agent_id,
            Session.created_by == created_by,
            Session.is_deleted == False
        ).order_by(Session.created_at.desc()).offset(skip).limit(limit).all()
    
    def count_by_agent_and_user(self, db: DBSession, agent_id: str, created_by: str) -> int:
        """
        统计指定智能体和用户的会话数量
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名
            created_by: 创建用户ID
            
        Returns:
            会话数量
        """
        return db.query(Session).filter(
            Session.agent_id == agent_id,
            Session.created_by == created_by,
            Session.is_deleted == False
        ).count()
    
    def update_title(
        self,
        db: DBSession,
        session_id: int,
        title: str,
        updated_by: str = "system"
    ) -> Optional[Session]:
        """
        更新会话标题
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            title: 新的会话标题
            updated_by: 更新人
            
        Returns:
            更新后的会话对象，未找到返回None
        """
        session = self.get_by_session_id(db=db, session_id=session_id)
        if not session:
            return None
        
        update_data = {"title": title}
        return self.update(db=db, db_obj=session, obj_in=update_data, updated_by=updated_by)
    
    def delete_by_session_id(
        self,
        db: DBSession,
        session_id: int,
        deleted_by: str = "system"
    ) -> bool:
        """
        根据session_id删除会话（软删除）
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            deleted_by: 删除人
            
        Returns:
            是否删除成功
        """
        session = self.get_by_session_id(db=db, session_id=session_id)
        if not session:
            return False
        
        return self.delete(db=db, id=session.id, deleted_by=deleted_by)
    
    def count_by_agent_id(self, db: DBSession, agent_id: str) -> int:
        """
        统计某个智能体的会话数量
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名
            
        Returns:
            会话数量
        """
        return db.query(Session).filter(
            Session.agent_id == agent_id,
            Session.is_deleted == False
        ).count()
    
    def count_all(self, db: DBSession) -> int:
        """
        统计全部会话数量
        
        Args:
            db: 数据库会话
            
        Returns:
            会话总数量
        """
        return db.query(Session).filter(
            Session.is_deleted == False
        ).count()
    
    def search_by_title(
        self, 
        db: DBSession, 
        keyword: str, 
        agent_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Session]:
        """
        按标题搜索会话（模糊查询）
        
        Args:
            db: 数据库会话
            keyword: 搜索关键词
            agent_id: 智能体英文名（可选，用于限定智能体）
            limit: 返回结果数量限制
            
        Returns:
            会话列表
        """
        query = db.query(Session).filter(
            Session.title.like(f"%{keyword}%"),
            Session.is_deleted == False
        )
        
        if agent_id:
            query = query.filter(Session.agent_id == agent_id)
        
        return query.order_by(Session.created_at.desc()).limit(limit).all()


# 创建全局CRUD实例
crud_session = CRUDSession(Session)
