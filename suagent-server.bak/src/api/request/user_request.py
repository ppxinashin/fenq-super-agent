"""
用户相关请求模型
"""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class UserAddRequest(BaseModel):
    """用户新增请求模型"""
    
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    password: str = Field(..., description="密码", min_length=6, max_length=100)
    role: str = Field(default="user", description="用户角色(admin/user)")
    created_by: str = Field(..., description="创建人")
    
    @field_validator('role')
    @classmethod
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
    """用户编辑请求模型（只能修改密码和角色）"""
    
    password: Optional[str] = Field(None, description="新密码（不修改则不传）", min_length=8)
    role: Optional[str] = Field(None, description="用户角色(admin/user)")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """验证密码：至少8位，只允许ASCII范围内的可见字符"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('密码至少8位')
        # ASCII可见字符范围：33-126
        for char in v:
            if not (33 <= ord(char) <= 126):
                raise ValueError('密码只允许ASCII范围内的可见字符')
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        """验证角色"""
        if v is not None and v not in ['admin', 'user']:
            raise ValueError('角色必须是 admin 或 user')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "NewPassword123!",
                "role": "admin"
            }
        }


class UserRegisterRequest(BaseModel):
    """用户注册请求模型"""
    
    username: str = Field(..., description="用户名", min_length=1, max_length=20)
    password: str = Field(..., description="密码", min_length=8)
    password_confirm: str = Field(..., description="确认密码", min_length=8)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """验证用户名：只能包含大小写字母和下划线"""
        if not re.match(r'^[a-zA-Z_]+$', v):
            raise ValueError('用户名只能包含大小写字母和下划线')
        if len(v) > 20:
            raise ValueError('用户名最多20个字符')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """验证密码：至少8位，只允许ASCII范围内的可见字符"""
        if len(v) < 8:
            raise ValueError('密码至少8位')
        # ASCII可见字符范围：33-126
        for char in v:
            if not (33 <= ord(char) <= 126):
                raise ValueError('密码只允许ASCII范围内的可见字符')
        return v
    
    def validate_password_match(self):
        """验证密码是否匹配"""
        if self.password != self.password_confirm:
            raise ValueError('两次输入的密码不一致')
        return True
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "zhangsan",
                "password": "Password123!",
                "password_confirm": "Password123!"
            }
        }


class UserLoginRequest(BaseModel):
    """用户登录请求模型"""
    
    username: str = Field(..., description="用户名", min_length=1, max_length=50)
    password: str = Field(..., description="密码", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "zhangsan",
                "password": "Password123!"
            }
        }

