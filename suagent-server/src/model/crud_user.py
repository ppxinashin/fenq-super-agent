"""
User模型CRUD操作
"""

from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
            "role": role.value if isinstance(role, UserRole) else role  # 传递字符串值
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
        
        update_data = {"role": new_role.value if isinstance(new_role, UserRole) else new_role}  # 传递字符串值
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
    
    def delete_by_user_id(
        self,
        db: Session,
        user_id: int,
        deleted_by: str = "system"
    ) -> bool:
        """
        根据user_id删除用户（软删除）

        Args:
            db: 数据库会话
            user_id: 用户ID
            deleted_by: 删除人

        Returns:
            是否删除成功
        """
        return self.delete(db=db, id=user_id, deleted_by=deleted_by)

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """
        根据用户ID获取用户

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户对象，未找到返回None
        """
        return db.query(User).filter(
            User.id == user_id
        ).first()

    def create(self, db: Session, obj_in: dict, created_by: str = "system") -> Optional[User]:
        """
        创建用户（适配用户管理服务的接口）

        Args:
            db: 数据库会话
            obj_in: 用户数据字典
            created_by: 创建人

        Returns:
            创建的用户对象
        """
        # 如果传入的数据中没有password_hash但有password，则进行哈希处理
        if "password" in obj_in and "password_hash" not in obj_in:
            salt = User.generate_salt()
            password = User.hash_password(obj_in["password"], salt)
            obj_in["password"] = password
            obj_in["salt"] = salt

        # 移除password_hash字段，如果存在
        if "password_hash" in obj_in:
            obj_in.pop("password_hash")

        return super().create(db=db, obj_in=obj_in, created_by=created_by)

    def update_user_info(self, db: Session, user_id: int, obj_in: dict, updated_by: str = "system") -> Optional[User]:
        """
        更新用户（适配用户管理服务的接口）

        Args:
            db: 数据库会话
            user_id: 用户ID
            obj_in: 更新数据字典
            updated_by: 更新人

        Returns:
            更新后的用户对象
        """
        user = self.get(db=db, id=user_id)
        if not user:
            return None

        update_data = obj_in.copy()

        # 如果有password_hash字段，需要转换为password和salt
        if "password_hash" in update_data:
            password_hash = update_data.pop("password_hash")
            salt = User.generate_salt()
            password = password_hash  # 这里假设传入的已经是最终的哈希值
            update_data["password"] = password
            update_data["salt"] = salt

        return super().update(db=db, db_obj=user, obj_in=update_data, updated_by=updated_by)

    def soft_delete(self, db: Session, user_id: int, deleted_by: str = "system") -> bool:
        """
        逻辑删除用户

        Args:
            db: 数据库会话
            user_id: 用户ID
            deleted_by: 删除人

        Returns:
            是否删除成功
        """
        return self.delete(db=db, id=user_id, deleted_by=deleted_by)

    def get_user_list(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """
        分页查询用户列表

        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            keyword: 关键词搜索

        Returns:
            (用户列表, 总数)
        """
        query = db.query(User).filter(User.is_deleted == False)

        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{keyword}%"),
                    User.role.ilike(f"%{keyword}%")
                )
            )

        # 计算总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        users = query.offset(offset).limit(page_size).all()

        return users, total


# 创建全局CRUD实例
crud_user = CRUDUser(User)

