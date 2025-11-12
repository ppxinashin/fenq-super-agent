"""
用户管理相关请求模型
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from src.consts.user_consts import UserConsts
import re


class UserUpdateRequest(BaseModel):
    """用户信息修改请求模型"""

    user_id: int = Field(..., description="用户ID", gt=0)
    password: Optional[str] = Field(default=None, description="新密码（可选）")
    role: str = Field(..., description="用户角色", pattern=f"^{UserConsts.USER_ROLE_ADMIN}|{UserConsts.USER_ROLE_USER}$")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """密码格式校验"""
        if v is None:
            return v

        if len(v) < UserConsts.PASSWORD_MIN_LENGTH:
            raise ValueError(f"密码长度不能少于{UserConsts.PASSWORD_MIN_LENGTH}位")

        if len(v) > UserConsts.PASSWORD_MAX_LENGTH:
            raise ValueError(f"密码长度不能超过{UserConsts.PASSWORD_MAX_LENGTH}位")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1000000000001,
                "password": "new_password123",
                "role": "user"
            }
        }


class UserCreateRequest(BaseModel):
    """用户新增请求模型"""

    username: str = Field(..., description="用户名", min_length=UserConsts.USERNAME_MIN_LENGTH, max_length=UserConsts.USERNAME_DISPLAY_MAX_LENGTH)
    password: str = Field(..., description="密码", min_length=UserConsts.PASSWORD_MIN_LENGTH, max_length=UserConsts.PASSWORD_MAX_LENGTH)
    role: str = Field(..., description="用户角色", pattern=f"^{UserConsts.USER_ROLE_ADMIN}|{UserConsts.USER_ROLE_USER}$")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """用户名格式校验"""
        if not re.match(UserConsts.USERNAME_PATTERN, v):
            raise ValueError(UserConsts.USERNAME_RULE_DESC)
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "new_user",
                "password": "password123",
                "role": "user"
            }
        }


class UserListRequest(BaseModel):
    """用户列表查询请求模型"""

    page: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=20, description="每页数量", ge=1, le=100)
    keyword: Optional[str] = Field(default=None, description="用户名关键词（可选）")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "keyword": "admin"
            }
        }