import hashlib
import uuid
import enum
from sqlalchemy import Column, String, Index, Enum
from src.consts.user_consts import UserConsts
from src.model.base import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    username = Column(String(UserConsts.USERNAME_MAX_LENGTH), unique=True, nullable=False, comment="用户名")
    password = Column(String(32), nullable=False, comment="密码(MD5加密)")
    salt = Column(String(4), nullable=False, comment="盐(从uuid4中取最后四位)")
    role = Column(Enum(UserConsts.USER_ROLE_ADMIN, UserConsts.USER_ROLE_USER, name="user_role"), default=UserConsts.USER_ROLE_USER, nullable=False, comment="用户角色(admin/user)")
    
    # 创建索引
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_role', 'role'),
    )
    
    @staticmethod
    def generate_salt() -> str:
        """生成盐值：从uuid4中取最后四位字符"""
        return str(uuid.uuid4())[-4:]
    
    @staticmethod
    def hash_password(plain_password: str, salt: str) -> str:
        """
        密码加密：明文密码 + 盐 的MD5加密
        
        Args:
            plain_password: 明文密码
            salt: 盐值
            
        Returns:
            MD5加密后的密码
        """
        combined = plain_password + salt
        return hashlib.md5(combined.encode()).hexdigest()
    
    def verify_password(self, plain_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            
        Returns:
            密码是否正确
        """
        hashed = self.hash_password(plain_password, str(self.salt))
        return str(self.password) == hashed
    
    def __repr__(self):
        # 处理 role 可能是字符串或枚举对象的情况
        role_value = self.role.value if hasattr(self.role, 'value') else self.role
        return f"<User(id={self.id}, username={self.username}, role={role_value})>"

