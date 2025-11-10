"""
API响应格式模块
"""

from .base_response import (
    ApiResponse,
    success_response,
    error_response,
    business_error_response
)
from .pageable import Pageable, create_pageable

# 用户响应模型
from .user_response import (
    UserResponse,
    UserDetailResponse,
    UserSimpleResponse
)

# 智能体响应模型
from .agent_response import (
    AgentResponse,
    AgentSimpleResponse,
    AgentListResponse,
    AgentConfigResponse
)

# 会话日志响应模型
from .session_log_response import (
    SessionLogResponse,
    SessionLogSimpleResponse,
    SessionMessageResponse,
    SessionSummaryResponse
)

# 用户长期记忆设置响应模型
from .user_memory_setting_response import (
    UserMemorySettingResponse,
    UserMemorySettingSimpleResponse,
    UserMemoryStatusResponse
)

# RAG文件查询响应模型
from .rag_file_response import (
    RAGFileListResponse,
    RAGFileChunkResponse,
    RAGFileSummaryResponse,
    RAGFileChunkSimpleResponse
)

__all__ = [
    # 通用响应
    "ApiResponse",
    "success_response",
    "error_response",
    "business_error_response",
    
    # 分页响应
    "Pageable",
    "create_pageable",
    
    # 用户响应模型
    "UserResponse",
    "UserDetailResponse",
    "UserSimpleResponse",
    
    # 智能体响应模型
    "AgentResponse",
    "AgentSimpleResponse",
    "AgentListResponse",
    "AgentConfigResponse",
    
    # 会话日志响应模型
    "SessionLogResponse",
    "SessionLogSimpleResponse",
    "SessionMessageResponse",
    "SessionSummaryResponse",
    
    # 用户长期记忆设置响应模型
    "UserMemorySettingResponse",
    "UserMemorySettingSimpleResponse",
    "UserMemoryStatusResponse",
    
    # RAG文件查询响应模型
    "RAGFileListResponse",
    "RAGFileChunkResponse",
    "RAGFileSummaryResponse",
    "RAGFileChunkSimpleResponse",
]

