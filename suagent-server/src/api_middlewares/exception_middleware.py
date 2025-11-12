"""
统一异常处理中间件
"""

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
import traceback
import logging

from src.response.base_response import ApiResponse

logger = logging.getLogger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    统一异常处理中间件

    捕获所有异常，转换为标准JSON响应格式
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并捕获异常

        Args:
            request: HTTP请求
            call_next: 下一个中间件或路由处理器

        Returns:
            HTTP响应
        """
        try:
            response = await call_next(request)
            return response

        except HTTPException as e:
            # 处理HTTPException（通常来自FastAPI的依赖注入等）
            logger.warning(f"HTTP异常: {e.status_code} - {e.detail}")

            return JSONResponse(
                status_code=e.status_code,
                content=ApiResponse.error(
                    message=e.detail,
                    code=e.status_code
                ).model_dump()
            )

        except (ValueError, BusinessException, ValidationError) as e:
            # 处理业务异常（通常是参数验证失败等）
            logger.warning(f"业务异常: {str(e)}")

            # 获取错误码
            error_code = 400
            if hasattr(e, 'code'):
                error_code = e.code

            return JSONResponse(
                status_code=error_code,
                content=ApiResponse.error(
                    message=str(e),
                    code=error_code
                ).model_dump()
            )

        except (AuthenticationError, AuthorizationError) as e:
            # 处理认证/授权异常
            logger.warning(f"认证/授权异常: {str(e)}")

            return JSONResponse(
                status_code=403,
                content=ApiResponse.error(
                    message=str(e),
                    code=403
                ).model_dump()
            )

        except NotFoundError as e:
            # 处理资源未找到异常
            logger.warning(f"资源未找到: {str(e)}")

            return JSONResponse(
                status_code=404,
                content=ApiResponse.error(
                    message=str(e),
                    code=404
                ).model_dump()
            )

        except ConflictError as e:
            # 处理资源冲突异常
            logger.warning(f"资源冲突: {str(e)}")

            return JSONResponse(
                status_code=409,
                content=ApiResponse.error(
                    message=str(e),
                    code=409
                ).model_dump()
            )

        except ConnectionError as e:
            # 处理连接异常（数据库、Redis等）
            logger.error(f"连接异常: {str(e)}")

            return JSONResponse(
                status_code=503,
                content=ApiResponse.error(
                    message="服务暂时不可用，请稍后重试",
                    code=503
                ).model_dump()
            )

        except TimeoutError as e:
            # 处理超时异常
            logger.error(f"超时异常: {str(e)}")

            return JSONResponse(
                status_code=504,
                content=ApiResponse.error(
                    message="请求超时，请稍后重试",
                    code=504
                ).model_dump()
            )

        except Exception as e:
            # 处理所有其他未捕获的异常
            logger.error(f"未捕获异常: {str(e)}", exc_info=True)

            # 在生产环境中，返回通用错误信息
            # 在开发环境中，可以返回详细错误信息
            import os
            is_dev = os.getenv("DEBUG", "false").lower() == "true"

            error_message = "服务器内部错误" if not is_dev else str(e)

            return JSONResponse(
                status_code=500,
                content=ApiResponse.error(
                    message=error_message,
                    code=500
                ).model_dump()
            )


class BusinessException(Exception):
    """
    业务异常类

    用于抛出需要返回给客户端的业务错误
    """

    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AuthenticationError(Exception):
    """
    认证异常类

    用于抛出认证相关的错误
    """

    def __init__(self, message: str = "认证失败"):
        self.message = message
        super().__init__(self.message)


class AuthorizationError(Exception):
    """
    授权异常类

    用于抛出权限相关的错误
    """

    def __init__(self, message: str = "权限不足"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    """
    验证异常类

    用于抛出参数验证相关的错误
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """
    资源未找到异常类

    用于抛出资源未找到的错误
    """

    def __init__(self, message: str = "资源未找到"):
        self.message = message
        super().__init__(self.message)


class ConflictError(Exception):
    """
    冲突异常类

    用于抛出资源冲突的错误
    """

    def __init__(self, message: str = "资源冲突"):
        self.message = message
        super().__init__(self.message)