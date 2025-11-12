"""
HTTP状态码常量定义
"""

from enum import IntEnum


class StatusCode(IntEnum):
    """HTTP状态码枚举"""
    
    # 2xx 成功
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # 2xx 业务错误（自定义）
    BUSINESS_ERROR = 299
    
    # 4xx 客户端错误
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    
    # 5xx 服务器错误
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


# 状态码对应的默认消息
STATUS_CODE_MESSAGES = {
    # 2xx 成功
    StatusCode.OK: "OK",
    StatusCode.CREATED: "Created",
    StatusCode.ACCEPTED: "Accepted",
    StatusCode.NO_CONTENT: "No Content",
    StatusCode.BUSINESS_ERROR: "Business Error",
    
    # 4xx 客户端错误
    StatusCode.BAD_REQUEST: "Bad Request",
    StatusCode.UNAUTHORIZED: "Unauthorized",
    StatusCode.FORBIDDEN: "Forbidden",
    StatusCode.NOT_FOUND: "Not Found",
    StatusCode.METHOD_NOT_ALLOWED: "Method Not Allowed",
    StatusCode.CONFLICT: "Conflict",
    StatusCode.UNPROCESSABLE_ENTITY: "Unprocessable Entity",
    StatusCode.TOO_MANY_REQUESTS: "Too Many Requests",
    
    # 5xx 服务器错误
    StatusCode.INTERNAL_SERVER_ERROR: "Internal Server Error",
    StatusCode.NOT_IMPLEMENTED: "Not Implemented",
    StatusCode.BAD_GATEWAY: "Bad Gateway",
    StatusCode.SERVICE_UNAVAILABLE: "Service Unavailable",
    StatusCode.GATEWAY_TIMEOUT: "Gateway Timeout",
}


def get_status_message(code: int) -> str:
    """
    获取状态码对应的默认消息
    
    Args:
        code: 状态码
        
    Returns:
        状态消息
    """
    return STATUS_CODE_MESSAGES.get(code, "Unknown Status")

