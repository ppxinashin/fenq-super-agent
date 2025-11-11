"""
SessionLog模型CRUD操作
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.model.crud_base import CRUDBase
from src.model.session_log import SessionLog


class CRUDSessionLog(CRUDBase[SessionLog]):
    """SessionLog CRUD操作类"""
    
    def get_session_agent(self, db: Session, session_id: int) -> Optional[str]:
        """
        获取会话所属的智能体ID
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            
        Returns:
            智能体ID，如果会话不存在返回None
        """
        log = db.query(SessionLog).filter(
            SessionLog.session_id == session_id,
            SessionLog.is_deleted == False
        ).first()
        return log.agent_id if log else None
    
    def create_log(
        self,
        db: Session,
        session_id: int,
        agent_id: str,
        role: str,
        content: str,
        created_by: str = "system"
    ) -> SessionLog:
        """
        创建会话日志
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            agent_id: 智能体英文名
            role: 角色(user/assistant/system)
            content: 消息内容
            created_by: 创建人
            
        Returns:
            创建的会话日志对象
            
        Raises:
            ValueError: 如果会话ID已绑定到其他智能体
        """
        # 检查会话是否已存在，如果存在则验证agent_id
        existing_agent_id = self.get_session_agent(db=db, session_id=session_id)
        if existing_agent_id and existing_agent_id != agent_id:
            raise ValueError(
                f"会话ID {session_id} 已绑定到智能体 {existing_agent_id}，"
                f"不能使用智能体 {agent_id} 创建日志"
            )
        
        log_data = {
            "session_id": session_id,
            "agent_id": agent_id,
            "role": role,
            "content": content
        }
        
        return self.create(db=db, obj_in=log_data, created_by=created_by)
    
    def get_by_session_id(
        self, 
        db: Session, 
        session_id: int,
        limit: Optional[int] = None
    ) -> List[SessionLog]:
        """
        根据会话ID获取所有日志（按时间升序）
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            limit: 限制返回数量（可选）
            
        Returns:
            会话日志列表
        """
        query = db.query(SessionLog).filter(
            SessionLog.session_id == session_id,
            SessionLog.is_deleted == False
        ).order_by(SessionLog.created_at)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_latest_by_session_id(
        self,
        db: Session,
        session_id: int,
        limit: int = 10
    ) -> List[SessionLog]:
        """
        获取会话最新的N条日志（按时间降序）
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            limit: 返回数量
            
        Returns:
            会话日志列表（最新的在前）
        """
        return db.query(SessionLog).filter(
            SessionLog.session_id == session_id,
            SessionLog.is_deleted == False
        ).order_by(desc(SessionLog.created_at)).limit(limit).all()
    
    def get_paginated_by_session(
        self,
        db: Session,
        session_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        分页查询会话日志
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            page: 页码（从1开始）
            page_size: 每页记录数
            
        Returns:
            包含分页信息和数据的字典
        """
        # 计算总数
        total = db.query(SessionLog).filter(
            SessionLog.session_id == session_id,
            SessionLog.is_deleted == False
        ).count()
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        # 确保页码在有效范围内
        page = max(1, min(page, total_pages))
        
        # 计算跳过记录数
        skip = (page - 1) * page_size
        
        # 查询数据（按时间升序）
        items = db.query(SessionLog).filter(
            SessionLog.session_id == session_id,
            SessionLog.is_deleted == False
        ).order_by(SessionLog.created_at).offset(skip).limit(page_size).all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
    
    def get_recent_paginated_by_session(
        self,
        db: Session,
        session_id: int,
        days: int = 7,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        分页查询指定时间范围内的会话日志
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            days: 查询的天数范围（默认7天）
            page: 页码（从1开始）
            page_size: 每页记录数
        
        Returns:
            包含分页信息和数据的字典
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        query = db.query(SessionLog).filter(
            SessionLog.session_id == session_id,
            SessionLog.is_deleted == False,
            SessionLog.created_at >= cutoff_time
        )
        
        total = query.count()
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        page = max(1, min(page, total_pages))
        skip = (page - 1) * page_size
        
        items = query.order_by(SessionLog.created_at).offset(skip).limit(page_size).all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
    
    def delete_by_session_id(
        self,
        db: Session,
        session_id: int,
        deleted_by: str = "system"
    ) -> int:
        """
        软删除某个会话的所有日志
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            deleted_by: 删除人
            
        Returns:
            删除的记录数
        """
        # 使用批量更新，提高性能
        count = db.query(SessionLog).filter(
            SessionLog.session_id == session_id,
            SessionLog.is_deleted == False
        ).update(
            {
                "is_deleted": True,
                "updated_by": deleted_by
            },
            synchronize_session=False
        )
        
        db.commit()
        return count
    
    def count_by_session_id(self, db: Session, session_id: int) -> int:
        """
        统计会话日志数量
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            
        Returns:
            日志数量
        """
        return db.query(SessionLog).filter(
            SessionLog.session_id == session_id,
            SessionLog.is_deleted == False
        ).count()
    
    def get_by_agent_id(
        self,
        db: Session,
        agent_id: str,
        limit: int = 100
    ) -> List[SessionLog]:
        """
        根据智能体ID获取会话日志
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名
            limit: 返回结果数量限制
            
        Returns:
            会话日志列表
        """
        return db.query(SessionLog).filter(
            SessionLog.agent_id == agent_id,
            SessionLog.is_deleted == False
        ).order_by(desc(SessionLog.created_at)).limit(limit).all()
    
    def get_by_session_and_agent(
        self,
        db: Session,
        session_id: int,
        agent_id: str,
        limit: Optional[int] = None
    ) -> List[SessionLog]:
        """
        根据会话ID和智能体ID获取日志
        
        Args:
            db: 数据库会话
            session_id: 会话ID
            agent_id: 智能体英文名
            limit: 限制返回数量（可选）
            
        Returns:
            会话日志列表
        """
        query = db.query(SessionLog).filter(
            SessionLog.session_id == session_id,
            SessionLog.agent_id == agent_id,
            SessionLog.is_deleted == False
        ).order_by(SessionLog.created_at)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_sessions_by_agent(
        self,
        db: Session,
        agent_id: str,
        limit: int = 100
    ) -> List[int]:
        """
        获取智能体的所有会话ID列表
        
        Args:
            db: 数据库会话
            agent_id: 智能体英文名
            limit: 返回结果数量限制
            
        Returns:
            会话ID列表（去重）
        """
        results = db.query(SessionLog.session_id).filter(
            SessionLog.agent_id == agent_id,
            SessionLog.is_deleted == False
        ).distinct().limit(limit).all()
        
        return [r[0] for r in results]

    def count_sessions_by_agent(self, db: Session, agent_id: str) -> int:
        """统计指定智能体的会话数量（按 session_id 去重）"""
        return db.query(SessionLog.session_id).filter(
            SessionLog.agent_id == agent_id,
            SessionLog.is_deleted == False
        ).distinct().count()


# 创建全局CRUD实例
crud_session_log = CRUDSessionLog(SessionLog)
