# 响应模型使用说明

## 概述

本项目为每个数据库模型创建了对应的Pydantic响应模型，用于API接口的JSON序列化。

## 响应模型列表

### 1. 用户响应模型

| 模型名 | 用途 |
|--------|------|
| `UserResponse` | 完整用户信息（不含密码） |
| `UserDetailResponse` | 用户详细信息 |
| `UserSimpleResponse` | 用户简要信息 |

### 2. 智能体响应模型

| 模型名 | 用途 |
|--------|------|
| `AgentResponse` | 完整智能体信息 |
| `AgentSimpleResponse` | 智能体简要信息 |
| `AgentListResponse` | 智能体列表项 |
| `AgentConfigResponse` | 智能体配置信息 |

### 3. 会话日志响应模型

| 模型名 | 用途 |
|--------|------|
| `SessionLogResponse` | 完整会话日志 |
| `SessionLogSimpleResponse` | 简要会话日志 |
| `SessionMessageResponse` | 会话消息 |
| `SessionSummaryResponse` | 会话摘要 |

## 使用方法

### 1. 自动转换

```python
user = crud_user.get(db, user_id)
response = UserResponse.from_orm(user)
```

### 2. 手动构造

```python
response = AgentListResponse(
    id=agent.id,
    agent_id=agent.agent_id,
    agent_name=agent.agent_name,
    description=agent.description,
    tools_count=len(agent.tools)
)
```

### 3. 批量转换

```python
users = crud_user.get_multi(db, limit=100)
user_responses = [UserSimpleResponse.from_orm(user) for user in users]
```

### 4. FastAPI集成

```python
@router.get("/users/{user_id}", response_model=ApiResponse[UserResponse])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get(db, user_id)
    return success_response(result=UserResponse.from_orm(user))
```

## 安全性说明

### 排除敏感字段

用户响应模型自动排除了敏感信息：
- ❌ `password` - 密码（不返回）
- ❌ `salt` - 盐值（不返回）

## 相关文件

- 响应模型目录: `src/api/response/`
- 通用响应格式: `src/api/response/base_response.py`
- 分页响应: `src/api/response/pageable.py`
