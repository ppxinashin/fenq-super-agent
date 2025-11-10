"""
通用基础请求模型
"""

from typing import Optional
from pydantic import BaseModel, Field


class BaseIDRequest(BaseModel):
    """基础ID请求模型（用于删除、查询等操作）"""
    
    id: int = Field(..., description="记录ID", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1000000000001
            }
        }


class BasePageKeywordRequest(BaseModel):
    """基础分页关键词查询请求模型"""
    
    page: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=10, description="每页数量", ge=1, le=100)
    keyword: Optional[str] = Field(default=None, description="关键词（可选）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 10,
                "keyword": "查询关键词"
            }
        }

