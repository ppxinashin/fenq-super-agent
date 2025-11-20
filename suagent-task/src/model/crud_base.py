"""
CRUD操作基类
提供通用的增删改查操作
"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from src.model.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """CRUD操作基类"""
    
    def __init__(self, model: Type[ModelType]):
        """
        初始化CRUD基类
        
        Args:
            model: SQLAlchemy模型类
        """
        self.model = model
    
    def create(self, db: Session, obj_in: Dict[str, Any], created_by: str = "admin") -> ModelType:
        """
        创建记录
        
        Args:
            db: 数据库会话
            obj_in: 输入数据字典
            created_by: 创建人
            
        Returns:
            创建的对象
        """
        obj_in["created_by"] = created_by
        obj_in["updated_by"] = created_by
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        根据ID获取记录（排除已删除）
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            查询到的对象，未找到返回None
        """
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.is_deleted == False
        ).first()
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        order_by: str = "id",
        order_desc: bool = True
    ) -> List[ModelType]:
        """
        获取多条记录（列表查询）
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 限制返回记录数
            order_by: 排序字段
            order_desc: 是否降序
            
        Returns:
            对象列表
        """
        query = db.query(self.model).filter(self.model.is_deleted == False)
        
        # 排序
        if hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            query = query.order_by(desc(order_column) if order_desc else asc(order_column))
        
        return query.offset(skip).limit(limit).all()
    
    def get_paginated(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "id",
        order_desc: bool = True
    ) -> Dict[str, Any]:
        """
        分页查询
        
        Args:
            db: 数据库会话
            page: 页码（从1开始）
            page_size: 每页记录数
            order_by: 排序字段
            order_desc: 是否降序
            
        Returns:
            包含分页信息和数据的字典
        """
        # 计算总数
        total = db.query(self.model).filter(self.model.is_deleted == False).count()
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        # 确保页码在有效范围内
        page = max(1, min(page, total_pages))
        
        # 计算跳过记录数
        skip = (page - 1) * page_size
        
        # 查询数据
        items = self.get_multi(
            db=db,
            skip=skip,
            limit=page_size,
            order_by=order_by,
            order_desc=order_desc
        )
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
    
    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        obj_in: Dict[str, Any],
        updated_by: str = "admin"
    ) -> ModelType:
        """
        更新记录
        
        Args:
            db: 数据库会话
            db_obj: 数据库对象
            obj_in: 更新数据字典
            updated_by: 更新人
            
        Returns:
            更新后的对象
        """
        obj_in["updated_by"] = updated_by
        
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int, deleted_by: str = "admin") -> bool:
        """
        软删除记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            deleted_by: 删除人
            
        Returns:
            是否删除成功
        """
        obj = self.get(db=db, id=id)
        if obj:
            obj.is_deleted = True
            obj.updated_by = deleted_by
            db.add(obj)
            db.commit()
            return True
        return False
    
    def hard_delete(self, db: Session, id: int) -> bool:
        """
        物理删除记录（谨慎使用！）
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            是否删除成功
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

