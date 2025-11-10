"""
用户长期记忆设置相关响应模型
"""

from datetime import datetime
from pydantic import BaseModel, Field


class UserMemorySettingResponse(BaseModel):
    """用户长期记忆设置响应模型"""
    
    id: int = Field(..., description="设置ID")
    username: str = Field(..., description="用户名")
    enabled: bool = Field(..., description="长期记忆开关(true=开启, false=关闭)")
    created_at: datetime = Field(..., description="创建时间")
    created_by: str = Field(..., description="创建人")
    updated_at: datetime = Field(..., description="更新时间")
    updated_by: str = Field(..., description="更新人")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 4000000000001,
                "username": "zhangsan",
                "enabled": True,
                "created_at": "2025-01-10T10:30:00",
                "created_by": "system",
                "updated_at": "2025-01-10T10:30:00",
                "updated_by": "system"
            }
        }


class UserMemorySettingSimpleResponse(BaseModel):
    """用户长期记忆设置简要响应模型"""
    
    username: str = Field(..., description="用户名")
    enabled: bool = Field(..., description="长期记忆开关")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "username": "zhangsan",
                "enabled": True
            }
        }


class UserMemoryStatusResponse(BaseModel):
    """用户长期记忆状态响应模型"""
    
    enabled: bool = Field(..., description="长期记忆开关状态")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True
            }
        }

