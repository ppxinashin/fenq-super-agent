"""
通用API响应格式
"""

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field
from src.consts.status_code import StatusCode, get_status_message

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    通用API响应格式
    
    Attributes:
        code: 状态码（遵循HTTP状态码 + 299业务错误）
        message: 响应消息
        result: 响应数据
    """
    
    code: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    result: Optional[T] = Field(default=None, description="响应数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "OK",
                "result": {"id": 1, "name": "example"}
            }
        }
    
    @classmethod
    def success(
        cls,
        result: Optional[T] = None,
        message: str = "OK",
        code: int = StatusCode.OK
    ) -> "ApiResponse[T]":
        """
        成功响应
        
        Args:
            result: 响应数据
            message: 响应消息（默认"OK"）
            code: 状态码（默认200）
            
        Returns:
            ApiResponse对象
        """
        return cls(
            code=code,
            message=message,
            result=result
        )
    
    @classmethod
    def error(
        cls,
        message: str,
        code: int = StatusCode.BUSINESS_ERROR,
        result: Optional[T] = None
    ) -> "ApiResponse[T]":
        """
        错误响应
        
        Args:
            message: 错误消息
            code: 状态码（默认299业务错误）
            result: 响应数据（可选）
            
        Returns:
            ApiResponse对象
        """
        return cls(
            code=code,
            message=message,
            result=result
        )
    
    @classmethod
    def from_status_code(
        cls,
        code: int,
        result: Optional[T] = None,
        message: Optional[str] = None
    ) -> "ApiResponse[T]":
        """
        根据状态码创建响应
        
        Args:
            code: 状态码
            result: 响应数据（可选）
            message: 自定义消息（可选，不提供则使用默认消息）
            
        Returns:
            ApiResponse对象
        """
        # 200使用"OK"，299使用自定义消息，其他使用默认消息
        if message is None:
            if code == StatusCode.OK:
                message = "OK"
            else:
                message = get_status_message(code)
        
        return cls(
            code=code,
            message=message,
            result=result
        )


# 便捷方法
def success_response(
    result: Optional[Any] = None,
    message: str = "OK"
) -> ApiResponse:
    """
    创建成功响应（便捷方法）
    
    Args:
        result: 响应数据
        message: 响应消息
        
    Returns:
        ApiResponse对象
    """
    return ApiResponse.success(result=result, message=message)


def error_response(
    message: str,
    code: int = StatusCode.BUSINESS_ERROR
) -> ApiResponse:
    """
    创建错误响应（便捷方法）
    
    Args:
        message: 错误消息
        code: 状态码
        
    Returns:
        ApiResponse对象
    """
    return ApiResponse.error(message=message, code=code)


def business_error_response(message: str) -> ApiResponse:
    """
    创建业务错误响应（便捷方法）
    
    Args:
        message: 错误消息
        
    Returns:
        ApiResponse对象，code=299
    """
    return ApiResponse.error(message=message, code=StatusCode.BUSINESS_ERROR)

