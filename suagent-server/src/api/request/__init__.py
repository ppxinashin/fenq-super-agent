"""
API请求模型模块
"""

# 基础请求模型
from .base_request import (
    BaseIDRequest,
    BasePageKeywordRequest
)

# 用户请求模型
from .user_request import (
    UserAddRequest,
    UserEditRequest
)

# 智能体请求模型
from .agent_request import (
    AgentAddRequest,
    AgentEditRequest
)
# 智能体管理请求模型
from .agent_manage_request import (
    AgentManageCreateRequest,
    AgentManageUpdateRequest
)

# 会话日志请求模型
from .session_log_request import (
    SessionLogAddRequest,
    SessionLogEditRequest,
    SessionLogListRequest
)

# 用户长期记忆设置请求模型
from .user_memory_setting_request import (
    UserMemorySettingAddRequest,
    UserMemorySettingEditRequest
)

# 文件上传请求模型
from .file_request import FileRequest

# 聊天请求模型
from .chat_request import ChatRequest


__all__ = [
    # 基础请求模型
    "BaseIDRequest",
    "BasePageKeywordRequest",
    
    # 用户请求模型
    "UserAddRequest",
    "UserEditRequest",
    
    # 智能体请求模型
    "AgentAddRequest",
    "AgentEditRequest",
    
    # 智能体管理请求模型
    "AgentManageCreateRequest",
    "AgentManageUpdateRequest",
    
    # 会话日志请求模型
    "SessionLogAddRequest",
    "SessionLogEditRequest",
    "SessionLogListRequest",
    
    # 用户长期记忆设置请求模型
    "UserMemorySettingAddRequest",
    "UserMemorySettingEditRequest",
    
    # 文件上传请求模型
    "FileRequest",
    
    # 聊天请求模型
    "ChatRequest",
]
