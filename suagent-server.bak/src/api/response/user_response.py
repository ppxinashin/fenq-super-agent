"""
用户相关响应模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """
    用户响应模型
    注意：不包含敏感信息（密码、盐值）
    """
    
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色(admin/user)")
    created_at: datetime = Field(..., description="创建时间")
    created_by: str = Field(..., description="创建人")
    updated_at: datetime = Field(..., description="更新时间")
    updated_by: str = Field(..., description="更新人")
    
    class Config:
        from_attributes = True  # Pydantic v2
        json_schema_extra = {
            "example": {
                "id": 1000000000001,
                "username": "zhangsan",
                "role": "user",
                "created_at": "2025-01-10T10:30:00",
                "created_by": "admin",
                "updated_at": "2025-01-10T10:30:00",
                "updated_by": "admin"
            }
        }


class UserDetailResponse(UserResponse):
    """
    用户详细信息响应模型（包含更多字段）
    """
    pass


class UserSimpleResponse(BaseModel):
    """
    用户简要信息响应模型（仅基本信息）
    """
    
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")
    
    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """
    用户登录响应模型
    """
    
    token: str = Field(..., description="JWT Token")
    user: UserResponse = Field(..., description="用户信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "id": 1000000000001,
                    "username": "zhangsan",
                    "role": "user",
                    "created_at": "2025-01-10T10:30:00",
                    "created_by": "admin",
                    "updated_at": "2025-01-10T10:30:00",
                    "updated_by": "admin"
                }
            }
        }


class UserRegisterResponse(BaseModel):
    """
    用户注册响应模型
    """
    
    user: UserResponse = Field(..., description="用户信息")
    message: str = Field(default="注册成功", description="提示信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 1000000000001,
                    "username": "zhangsan",
                    "role": "user",
                    "created_at": "2025-01-10T10:30:00",
                    "created_by": "system",
                    "updated_at": "2025-01-10T10:30:00",
                    "updated_by": "system"
                },
                "message": "注册成功"
            }
        }

