"""
用户认证相关的响应模型
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UserInfo(BaseModel):
    """用户信息模型"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "role": "admin",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z"
            }
        }


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌过期时间（秒）")
    user_info: UserInfo = Field(..., description="用户信息")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 86400,
                "user_info": {
                    "id": 1,
                    "username": "admin",
                    "role": "admin",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z"
                }
            }
        }


class RegisterResponse(BaseModel):
    """注册响应模型"""
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")
    message: str = Field(default="注册成功", description="注册消息")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 2,
                "username": "new_user",
                "role": "user",
                "message": "注册成功"
            }
        }


class LogoutResponse(BaseModel):
    """退出登录响应模型"""
    message: str = Field(default="退出登录成功", description="退出消息")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "退出登录成功"
            }
        }


class ChangePasswordResponse(BaseModel):
    """修改密码响应模型"""
    message: str = Field(default="密码修改成功", description="修改消息")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "密码修改成功"
            }
        }


class TokenValidationResponse(BaseModel):
    """Token验证响应模型"""
    valid: bool = Field(..., description="Token是否有效")
    user_info: Optional[UserInfo] = Field(None, description="用户信息（Token有效时）")
    expires_at: Optional[datetime] = Field(None, description="Token过期时间")

    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "user_info": {
                    "id": 1,
                    "username": "admin",
                    "role": "admin",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z"
                },
                "expires_at": "2024-01-02T00:00:00Z"
            }
        }