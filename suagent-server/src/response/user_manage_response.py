"""
用户管理相关响应模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_serializer


class UserInfo(BaseModel):
    """用户信息响应模型"""

    user_id: int = Field(..., description="用户ID", alias="id")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")
    is_deleted: bool = Field(..., description="是否已删除")
    created_at: datetime = Field(..., description="创建时间")
    created_by: Optional[str] = Field(default=None, description="创建人用户名")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    updated_by: Optional[str] = Field(default=None, description="更新人用户名")

    @field_serializer('created_at', 'updated_at')
    def format_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": 1000000000001,
                "username": "admin",
                "role": "admin",
                "is_deleted": False,
                "created_at": "2024-01-01 00:00:00",
                "updated_at": "2024-01-01 12:00:00"
            }
        }


class UserListItem(BaseModel):
    """用户列表项响应模型"""

    user_id: int = Field(..., description="用户ID", alias="id")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")
    is_deleted: bool = Field(..., description="是否已删除")
    created_at: datetime = Field(..., description="创建时间")
    created_by: Optional[str] = Field(default=None, description="创建人用户名")

    @field_serializer('created_at')
    def format_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": 1000000000001,
                "username": "admin",
                "role": "admin",
                "is_deleted": False,
                "created_at": "2024-01-01 00:00:00"
            }
        }