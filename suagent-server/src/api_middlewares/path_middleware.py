"""
路径规范化中间件
处理双斜杠等路径问题
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
import re


class PathNormalizeMiddleware(BaseHTTPMiddleware):
    """
    路径规范化中间件
    
    处理路径中的双斜杠等问题，确保路由能正确匹配
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        """
        规范化请求路径
        
        Args:
            request: HTTP请求
            call_next: 下一个中间件或路由处理器
            
        Returns:
            HTTP响应
        """
        # 获取原始路径
        path = request.url.path
        
        # 规范化路径：将多个连续斜杠替换为单个斜杠
        normalized_path = re.sub(r'/+', '/', path)
        
        # 如果路径被修改，更新request的scope
        if normalized_path != path:
            request.scope["path"] = normalized_path
            request.scope["raw_path"] = normalized_path.encode()
            
        response = await call_next(request)
        return response

