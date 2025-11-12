"""
用户认证相关的请求模型
"""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from src.consts.user_consts import UserConsts


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., min_length=1, max_length=UserConsts.USERNAME_DISPLAY_MAX_LENGTH, description="用户名")
    password: str = Field(..., min_length=1, max_length=UserConsts.PASSWORD_MAX_LENGTH, description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "password123"
            }
        }


class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str = Field(..., min_length=UserConsts.USERNAME_MIN_LENGTH, max_length=UserConsts.USERNAME_DISPLAY_MAX_LENGTH, description="用户名")
    password: str = Field(..., min_length=UserConsts.PASSWORD_MIN_LENGTH, max_length=UserConsts.PASSWORD_MAX_LENGTH, description="密码")
    confirm_password: str = Field(..., description="确认密码")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """用户名验证：只允许大小写字母、数字和下划线"""
        if not re.match(UserConsts.USERNAME_PATTERN, v):
            raise ValueError(UserConsts.USERNAME_RULE_DESC)
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """密码验证：至少8位，ASCII可见字符"""
        if len(v) < UserConsts.PASSWORD_MIN_LENGTH:
            raise ValueError(f'密码长度至少{UserConsts.PASSWORD_MIN_LENGTH}位')

        # 检查是否为ASCII可见字符
        for char in v:
            if not (32 <= ord(char) <= 126):
                raise ValueError('密码只能包含ASCII可见字符')

        return v

    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, v, info):
        """确认密码验证"""
        password = info.data.get('password')
        if password and v != password:
            raise ValueError('两次输入的密码不一致')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "test_user",
                "password": "password123",
                "confirm_password": "password123"
            }
        }


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=UserConsts.PASSWORD_MIN_LENGTH, max_length=UserConsts.PASSWORD_MAX_LENGTH, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """新密码验证：至少8位，ASCII可见字符"""
        if len(v) < UserConsts.PASSWORD_MIN_LENGTH:
            raise ValueError(f'密码长度至少{UserConsts.PASSWORD_MIN_LENGTH}位')

        # 检查是否为ASCII可见字符
        for char in v:
            if not (32 <= ord(char) <= 126):
                raise ValueError('密码只能包含ASCII可见字符')

        return v

    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, v, info):
        """确认新密码验证"""
        new_password = info.data.get('new_password')
        if new_password and v != new_password:
            raise ValueError('两次输入的新密码不一致')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "old_password123",
                "new_password": "new_password456",
                "confirm_password": "new_password456"
            }
        }


class LogoutRequest(BaseModel):
    """退出登录请求模型"""
    token: Optional[str] = Field(None, description="要退出的token（可选）")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }