"""
用户记忆设置相关的请求模型
"""

from pydantic import BaseModel, Field


class MemorySettingRequest(BaseModel):
    """记忆开关设置请求"""
    enabled: bool = Field(..., description="记忆开关状态")

    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True
            }
        }


class MemorySettingResponse(BaseModel):
    """记忆开关设置响应"""
    username: str = Field(..., description="用户名")
    enabled: bool = Field(..., description="记忆开关状态")
    message: str = Field(default="设置成功", description="操作结果消息")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "test_user",
                "enabled": True,
                "message": "记忆开关已开启"
            }
        }