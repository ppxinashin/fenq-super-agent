"""
User模型CRUD操作
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from src.model.crud_base import CRUDBase
from src.model.user import User, UserRole


class CRUDUser(CRUDBase[User]):
    """User CRUD操作类"""
    
    def create_user(
        self, 
        db: Session, 
        username: str, 
        plain_password: str,
        role: UserRole = UserRole.USER,
        created_by: str = "system"
    ) -> User:
        """
        创建用户（自动生成盐和加密密码）
        
        Args:
            db: 数据库会话
            username: 用户名
            plain_password: 明文密码
            role: 用户角色（默认为普通用户）
            created_by: 创建人
            
        Returns:
            创建的用户对象
        """
        salt = User.generate_salt()
        password = User.hash_password(plain_password, salt)
        
        user_data = {
            "username": username,
            "password": password,
            "salt": salt,
            "role": role
        }
        
        return self.create(db=db, obj_in=user_data, created_by=created_by)
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            db: 数据库会话
            username: 用户名
            
        Returns:
            用户对象，未找到返回None
        """
        return db.query(User).filter(
            User.username == username,
            User.is_deleted == False
        ).first()
    
    def authenticate(self, db: Session, username: str, plain_password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            db: 数据库会话
            username: 用户名
            plain_password: 明文密码
            
        Returns:
            认证成功返回用户对象，否则返回None
        """
        user = self.get_by_username(db=db, username=username)
        if not user:
            return None
        if not user.verify_password(plain_password):
            return None
        return user
    
    def update_password(
        self,
        db: Session,
        user_id: int,
        new_password: str,
        updated_by: str = "system"
    ) -> Optional[User]:
        """
        更新用户密码
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            new_password: 新密码（明文）
            updated_by: 更新人
            
        Returns:
            更新后的用户对象，未找到返回None
        """
        user = self.get(db=db, id=user_id)
        if not user:
            return None
        
        # 生成新的盐和密码
        salt = User.generate_salt()
        password = User.hash_password(new_password, salt)
        
        update_data = {
            "password": password,
            "salt": salt
        }
        
        return self.update(db=db, db_obj=user, obj_in=update_data, updated_by=updated_by)
    
    def get_by_role(self, db: Session, role: UserRole, limit: int = 100) -> List[User]:
        """
        根据角色查询用户
        
        Args:
            db: 数据库会话
            role: 用户角色
            limit: 返回结果数量限制
            
        Returns:
            用户列表
        """
        return db.query(User).filter(
            User.role == role,
            User.is_deleted == False
        ).limit(limit).all()
    
    def update_role(
        self,
        db: Session,
        user_id: int,
        new_role: UserRole,
        updated_by: str = "system"
    ) -> Optional[User]:
        """
        更新用户角色
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            new_role: 新角色
            updated_by: 更新人
            
        Returns:
            更新后的用户对象，未找到返回None
        """
        user = self.get(db=db, id=user_id)
        if not user:
            return None
        
        update_data = {"role": new_role}
        return self.update(db=db, db_obj=user, obj_in=update_data, updated_by=updated_by)
    
    def is_admin(self, db: Session, user_id: int) -> bool:
        """
        检查用户是否为管理员
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            是否为管理员
        """
        user = self.get(db=db, id=user_id)
        if not user:
            return False
        return user.role == UserRole.ADMIN


# 创建全局CRUD实例
crud_user = CRUDUser(User)

