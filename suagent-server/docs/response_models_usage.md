# 响应模型使用说明

## 概述

本项目为每个数据库模型创建了对应的Pydantic响应模型，用于API接口的JSON序列化。

## 响应模型列表

### 1. 用户响应模型

| 模型名 | 文件 | 用途 |
|--------|------|------|
| `UserResponse` | `user_response.py` | 完整用户信息（不含密码） |
| `UserDetailResponse` | `user_response.py` | 用户详细信息 |
| `UserSimpleResponse` | `user_response.py` | 用户简要信息 |

### 2. 智能体响应模型

| 模型名 | 文件 | 用途 |
|--------|------|------|
| `AgentResponse` | `agent_response.py` | 完整智能体信息 |
| `AgentSimpleResponse` | `agent_response.py` | 智能体简要信息 |
| `AgentListResponse` | `agent_response.py` | 智能体列表项 |
| `AgentConfigResponse` | `agent_response.py` | 智能体配置信息 |

### 3. 会话日志响应模型

| 模型名 | 文件 | 用途 |
|--------|------|------|
| `SessionLogResponse` | `session_log_response.py` | 完整会话日志 |
| `SessionLogSimpleResponse` | `session_log_response.py` | 简要会话日志 |
| `SessionMessageResponse` | `session_log_response.py` | 会话消息（对话展示） |
| `SessionSummaryResponse` | `session_log_response.py` | 会话摘要 |

### 4. 用户长期记忆设置响应模型

| 模型名 | 文件 | 用途 |
|--------|------|------|
| `UserMemorySettingResponse` | `user_memory_setting_response.py` | 完整设置信息 |
| `UserMemorySettingSimpleResponse` | `user_memory_setting_response.py` | 简要设置信息 |
| `UserMemoryStatusResponse` | `user_memory_setting_response.py` | 仅开关状态 |

## 使用示例

### 1. 用户接口

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.model import get_db, crud_user
from src.api.response import (
    ApiResponse,
    success_response,
    UserResponse,
    UserSimpleResponse,
    Pageable
)

router = APIRouter()

# 获取用户详情
@router.get("/users/{user_id}", response_model=ApiResponse[UserResponse])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户详情"""
    user = crud_user.get(db, user_id)
    if not user:
        return error_response("用户不存在", code=StatusCode.NOT_FOUND)
    
    # 自动从ORM模型转换为响应模型
    return success_response(result=UserResponse.from_orm(user))

# 获取用户列表（分页）
@router.get("/users", response_model=ApiResponse[Pageable[UserSimpleResponse]])
async def list_users(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """分页查询用户列表"""
    page_data = crud_user.get_paginated(db, page=page, page_size=page_size)
    
    # 转换ORM模型列表为响应模型列表
    user_responses = [
        UserSimpleResponse.from_orm(user) 
        for user in page_data["items"]
    ]
    
    # 创建分页响应
    pageable = Pageable(
        page=page_data["page"],
        page_size=page_data["page_size"],
        total=page_data["total"],
        data=user_responses
    )
    
    return success_response(result=pageable)
```

**响应示例**：

```json
{
    "code": 200,
    "message": "OK",
    "result": {
        "id": 1000000000001,
        "username": "zhangsan",
        "role": "user",
        "created_at": "2025-01-10T10:30:00",
        "created_by": "admin",
        "updated_at": "2025-01-10T10:30:00",
        "updated_by": "admin"
    }
}
```

### 2. 智能体接口

```python
from src.api.response import (
    AgentResponse,
    AgentSimpleResponse,
    AgentListResponse,
    AgentConfigResponse
)

# 获取智能体详情
@router.get("/agents/{agent_id}", response_model=ApiResponse[AgentResponse])
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """获取智能体详情"""
    agent = crud_agent.get_by_agent_id(db, agent_id)
    if not agent:
        return error_response("智能体不存在", code=StatusCode.NOT_FOUND)
    
    return success_response(result=AgentResponse.from_orm(agent))

# 获取智能体列表
@router.get("/agents", response_model=ApiResponse[Pageable[AgentListResponse]])
async def list_agents(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """分页查询智能体列表"""
    page_data = crud_agent.get_paginated(db, page=page, page_size=page_size)
    
    # 转换为列表响应模型（可以添加计算字段）
    agent_responses = []
    for agent in page_data["items"]:
        response = AgentListResponse.from_orm(agent)
        # 添加工具数量（计算字段）
        response.tools_count = len(agent.tools) if agent.tools else 0
        agent_responses.append(response)
    
    pageable = Pageable(
        page=page_data["page"],
        page_size=page_data["page_size"],
        total=page_data["total"],
        data=agent_responses
    )
    
    return success_response(result=pageable)

# 获取智能体配置
@router.get("/agents/{agent_id}/config", response_model=ApiResponse[AgentConfigResponse])
async def get_agent_config(agent_id: str, db: Session = Depends(get_db)):
    """获取智能体配置"""
    agent = crud_agent.get_by_agent_id(db, agent_id)
    if not agent:
        return error_response("智能体不存在", code=StatusCode.NOT_FOUND)
    
    return success_response(result=AgentConfigResponse.from_orm(agent))
```

**响应示例**：

```json
{
    "code": 200,
    "message": "OK",
    "result": {
        "id": 2000000000001,
        "agent_id": "demo_agent",
        "agent_name": "演示智能体",
        "description": "这是一个演示智能体",
        "system_prompt": "你是一个友好的AI助手",
        "tools": ["now_time", "web_search"],
        "mcp_enabled": true,
        "mcp_servers": {
            "amap-maps": {
                "type": "sse",
                "url": "https://mcp.api-inference.modelscope.net/xxx/sse"
            }
        },
        "created_at": "2025-01-10T10:30:00",
        "created_by": "system",
        "updated_at": "2025-01-10T10:30:00",
        "updated_by": "system"
    }
}
```

### 3. 会话日志接口

```python
from src.api.response import (
    SessionLogResponse,
    SessionMessageResponse,
    SessionSummaryResponse
)

# 获取会话历史
@router.get("/sessions/{session_id}/logs", response_model=ApiResponse[Pageable[SessionMessageResponse]])
async def get_session_logs(
    session_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取会话历史消息"""
    page_data = crud_session_log.get_paginated_by_session(
        db, session_id=session_id, page=page, page_size=page_size
    )
    
    # 转换为消息响应模型
    messages = []
    for log in page_data["items"]:
        message = SessionMessageResponse(
            role=log.role,
            content=log.content,
            timestamp=log.created_at
        )
        messages.append(message)
    
    pageable = Pageable(
        page=page_data["page"],
        page_size=page_data["page_size"],
        total=page_data["total"],
        data=messages
    )
    
    return success_response(result=pageable)

# 获取会话摘要
@router.get("/sessions/{session_id}/summary", response_model=ApiResponse[SessionSummaryResponse])
async def get_session_summary(session_id: int, db: Session = Depends(get_db)):
    """获取会话摘要"""
    logs = crud_session_log.get_by_session_id(db, session_id)
    if not logs:
        return error_response("会话不存在", code=StatusCode.NOT_FOUND)
    
    # 构建摘要
    summary = SessionSummaryResponse(
        session_id=session_id,
        agent_id=logs[0].agent_id,
        message_count=len(logs),
        first_message_time=logs[0].created_at,
        last_message_time=logs[-1].created_at
    )
    
    return success_response(result=summary)
```

**响应示例**：

```json
{
    "code": 200,
    "message": "OK",
    "result": {
        "page": 1,
        "page_size": 20,
        "total": 10,
        "data": [
            {
                "role": "user",
                "content": "你好",
                "timestamp": "2025-01-10T10:30:00"
            },
            {
                "role": "assistant",
                "content": "你好！有什么可以帮您？",
                "timestamp": "2025-01-10T10:30:05"
            }
        ]
    }
}
```

### 4. 用户长期记忆设置接口

```python
from src.api.response import (
    UserMemorySettingResponse,
    UserMemoryStatusResponse
)

# 获取用户记忆设置
@router.get("/users/{username}/memory", response_model=ApiResponse[UserMemorySettingResponse])
async def get_memory_setting(username: str, db: Session = Depends(get_db)):
    """获取用户长期记忆设置"""
    setting = crud_user_memory_setting.get_by_username(db, username)
    if not setting:
        return error_response("设置不存在", code=StatusCode.NOT_FOUND)
    
    return success_response(result=UserMemorySettingResponse.from_orm(setting))

# 获取记忆开关状态
@router.get("/users/{username}/memory/status", response_model=ApiResponse[UserMemoryStatusResponse])
async def get_memory_status(username: str, db: Session = Depends(get_db)):
    """获取用户长期记忆开关状态"""
    enabled = crud_user_memory_setting.is_enabled(db, username)
    
    return success_response(result=UserMemoryStatusResponse(enabled=enabled))

# 设置记忆开关
@router.put("/users/{username}/memory", response_model=ApiResponse[UserMemorySettingResponse])
async def set_memory_status(
    username: str,
    enabled: bool,
    db: Session = Depends(get_db)
):
    """设置用户长期记忆开关"""
    setting = crud_user_memory_setting.set_enabled(db, username, enabled)
    
    return success_response(
        result=UserMemorySettingResponse.from_orm(setting),
        message="设置成功"
    )
```

**响应示例**：

```json
{
    "code": 200,
    "message": "OK",
    "result": {
        "enabled": true
    }
}
```

## 模型转换方法

### 1. 自动转换（推荐）

使用 `from_orm()` 方法自动从ORM模型转换：

```python
user = crud_user.get(db, user_id)
response = UserResponse.from_orm(user)
```

### 2. 手动构造

适用于需要计算字段或组合多个来源的数据：

```python
response = AgentListResponse(
    id=agent.id,
    agent_id=agent.agent_id,
    agent_name=agent.agent_name,
    description=agent.description,
    tools_count=len(agent.tools),  # 计算字段
    mcp_enabled=agent.mcp_enabled,
    created_at=agent.created_at
)
```

### 3. 批量转换

列表转换：

```python
users = crud_user.get_multi(db, limit=100)
user_responses = [UserSimpleResponse.from_orm(user) for user in users]
```

## 安全性说明

### 排除敏感字段

用户响应模型自动排除了敏感信息：

- ❌ `password` - 密码（不返回）
- ❌ `salt` - 盐值（不返回）
- ✅ 其他字段正常返回

如需添加更多敏感字段保护，在响应模型中不定义对应字段即可。

## 响应模型特点

### 1. 类型安全

使用Pydantic提供完整的类型检查和验证：

```python
class UserResponse(BaseModel):
    id: int  # 必须是整数
    username: str  # 必须是字符串
    role: str  # 必须是字符串
```

### 2. 自动文档

FastAPI会自动生成OpenAPI文档：

```python
@router.get("/users/{user_id}", response_model=ApiResponse[UserResponse])
```

在Swagger UI中会显示完整的响应结构。

### 3. JSON序列化

Pydantic自动处理复杂类型的序列化：

- `datetime` → ISO 8601字符串
- `List` → JSON数组
- `Dict` → JSON对象

### 4. 示例数据

每个模型都包含示例数据，显示在API文档中：

```python
class Config:
    json_schema_extra = {
        "example": {...}
    }
```

## 最佳实践

### 1. 选择合适的响应模型

- 列表接口：使用 `SimpleResponse` 或 `ListResponse`
- 详情接口：使用完整的 `Response`
- 配置接口：使用 `ConfigResponse`

### 2. 分页统一使用Pageable

```python
# 正确
response_model=ApiResponse[Pageable[UserSimpleResponse]]

# 不推荐
response_model=ApiResponse[List[UserSimpleResponse]]
```

### 3. 添加计算字段

在转换时添加计算字段：

```python
agent_response = AgentListResponse.from_orm(agent)
agent_response.tools_count = len(agent.tools)
```

### 4. 使用类型提示

始终使用明确的类型提示：

```python
# 正确
response_model=ApiResponse[UserResponse]

# 不正确
response_model=ApiResponse  # 缺少泛型参数
```

## 相关文件

- 响应模型目录: `src/api/response/`
- 通用响应格式: `src/api/response/base_response.py`
- 分页响应: `src/api/response/pageable.py`
- API响应使用说明: `docs/api_response_usage.md`

