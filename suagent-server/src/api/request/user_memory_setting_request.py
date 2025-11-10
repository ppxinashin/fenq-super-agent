"""
用户长期记忆设置相关请求模型
"""

from typing import Optional
from pydantic import BaseModel, Field


class UserMemorySettingAddRequest(BaseModel):
    """用户长期记忆设置新增请求模型"""
    
    username: str = Field(..., description="用户名", min_length=1, max_length=50)
    enabled: bool = Field(default=True, description="长期记忆开关(true=开启, false=关闭)")
    created_by: str = Field(..., description="创建人")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "zhangsan",
                "enabled": True,
                "created_by": "system"
            }
        }


class UserMemorySettingEditRequest(BaseModel):
    """用户长期记忆设置编辑请求模型"""
    
    id: int = Field(..., description="设置ID", gt=0)
    username: Optional[str] = Field(None, description="用户名", min_length=1, max_length=50)
    enabled: Optional[bool] = Field(None, description="长期记忆开关(true=开启, false=关闭)")
    updated_by: str = Field(..., description="更新人")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 4000000000001,
                "username": "zhangsan",
                "enabled": False,
                "updated_by": "admin"
            }
        }

