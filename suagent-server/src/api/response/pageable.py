"""
分页响应格式
"""

from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class Pageable(BaseModel, Generic[T]):
    """
    分页响应格式
    
    Attributes:
        page: 当前页码
        page_size: 每页最大数量
        total: 总记录数
        data: 数据列表
    """
    
    page: int = Field(..., description="当前页码（从1开始）", ge=1)
    page_size: int = Field(..., description="每页最大数量", ge=1)
    total: int = Field(..., description="总记录数", ge=0)
    data: List[T] = Field(default_factory=list, description="数据列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 10,
                "total": 100,
                "data": [
                    {"id": 1, "name": "item1"},
                    {"id": 2, "name": "item2"}
                ]
            }
        }
    
    @property
    def total_pages(self) -> int:
        """
        计算总页数
        
        Returns:
            总页数
        """
        if self.total == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size
    
    @property
    def has_prev(self) -> bool:
        """
        是否有上一页
        
        Returns:
            是否有上一页
        """
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        """
        是否有下一页
        
        Returns:
            是否有下一页
        """
        return self.page < self.total_pages
    
    @classmethod
    def from_dict(
        cls,
        page_data: dict,
        data_key: str = "items"
    ) -> "Pageable[T]":
        """
        从字典创建分页对象（适配数据库查询结果）
        
        Args:
            page_data: 包含分页信息的字典
                - page: 当前页
                - page_size: 每页大小
                - total: 总记录数
                - items/data: 数据列表（key由data_key指定）
            data_key: 数据列表的key（默认"items"）
            
        Returns:
            Pageable对象
        """
        return cls(
            page=page_data.get("page", 1),
            page_size=page_data.get("page_size", 10),
            total=page_data.get("total", 0),
            data=page_data.get(data_key, [])
        )
    
    def to_dict(self) -> dict:
        """
        转换为字典（包含计算属性）
        
        Returns:
            包含所有信息的字典
        """
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_prev": self.has_prev,
            "has_next": self.has_next,
            "data": self.data
        }


def create_pageable(
    page: int,
    page_size: int,
    total: int,
    data: List[T]
) -> Pageable[T]:
    """
    创建分页对象（便捷方法）
    
    Args:
        page: 当前页码
        page_size: 每页大小
        total: 总记录数
        data: 数据列表
        
    Returns:
        Pageable对象
    """
    return Pageable(
        page=page,
        page_size=page_size,
        total=total,
        data=data
    )


class PageableResponse(BaseModel, Generic[T]):
    """
    分页响应格式（标准版）
    
    Attributes:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页数量
        total_pages: 总页数
        has_prev: 是否有上一页
        has_next: 是否有下一页
    """
    
    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(..., description="总记录数", ge=0)
    page: int = Field(..., description="当前页码（从1开始）", ge=1)
    page_size: int = Field(..., description="每页数量", ge=1)
    total_pages: int = Field(..., description="总页数", ge=0)
    has_prev: bool = Field(..., description="是否有上一页")
    has_next: bool = Field(..., description="是否有下一页")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {"id": 1, "name": "item1"},
                    {"id": 2, "name": "item2"}
                ],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "total_pages": 10,
                "has_prev": False,
                "has_next": True
            }
        }

