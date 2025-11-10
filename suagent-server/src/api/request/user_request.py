"""
用户相关请求模型
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class UserAddRequest(BaseModel):
    """用户新增请求模型"""
    
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    password: str = Field(..., description="密码", min_length=6, max_length=100)
    role: str = Field(default="user", description="用户角色(admin/user)")
    created_by: str = Field(..., description="创建人")
    
    @validator('role')
    def validate_role(cls, v):
        """验证角色"""
        if v not in ['admin', 'user']:
            raise ValueError('角色必须是 admin 或 user')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "zhangsan",
                "password": "123456",
                "role": "user",
                "created_by": "admin"
            }
        }


class UserEditRequest(BaseModel):
    """用户编辑请求模型"""
    
    id: int = Field(..., description="用户ID", gt=0)
    username: Optional[str] = Field(None, description="用户名", min_length=3, max_length=50)
    password: Optional[str] = Field(None, description="密码（不修改则不传）", min_length=6, max_length=100)
    role: Optional[str] = Field(None, description="用户角色(admin/user)")
    updated_by: str = Field(..., description="更新人")
    
    @validator('role')
    def validate_role(cls, v):
        """验证角色"""
        if v is not None and v not in ['admin', 'user']:
            raise ValueError('角色必须是 admin 或 user')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1000000000001,
                "username": "zhangsan",
                "password": "newpassword123",
                "role": "admin",
                "updated_by": "admin"
            }
        }

