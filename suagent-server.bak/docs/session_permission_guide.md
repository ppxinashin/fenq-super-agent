# 会话权限控制说明

## 概述

会话管理系统已实现完整的权限控制，确保用户只能操作自己创建的会话。

## 权限控制功能

### 1. 登录认证

**所有接口都需要登录**
- `agent_controller.py` - 智能体聊天接口
- `session_controller.py` - 会话管理接口

所有接口都使用 `Depends(get_current_user)` 进行身份验证，必须在请求头中携带有效的JWT Token：

```
Authorization: Bearer <your_token>
```

### 2. 会话创建权限

**接口**: `POST /api/session/create`

- 任何登录用户都可以创建会话
- 会话会自动关联到当前登录用户（`created_by` 字段）

### 3. 会话列表查询权限

**接口**: `POST /api/session/list`

**权限规则**：
- ✅ 只显示当前智能体（`agent_id`）下的会话
- ✅ 只显示当前登录用户（`created_by`）创建的会话
- ❌ 无法查看其他用户创建的会话

**实现方式**：
```python
# 使用双重过滤条件
sessions = crud_session.get_by_agent_and_user(
    db=db,
    agent_id=request.agent_id,
    created_by=str(current_user.id),  # 当前用户ID
    skip=skip,
    limit=page_size
)
```

### 4. 会话修改权限

**接口**: `PUT /api/session/update`

**权限规则**：
- ✅ 只能修改自己创建的会话
- ❌ 尝试修改他人会话返回 403 错误

**权限检查**：
```python
# 检查权限：只能修改自己创建的会话
if str(session.created_by) != str(current_user.id):
    return error_response(
        message="无权修改该会话，只能修改自己创建的会话",
        code=status.HTTP_403_FORBIDDEN
    )
```

### 5. 会话删除权限

**接口**: `DELETE /api/session/delete`

**权限规则**：
- ✅ 只能删除自己创建的会话
- ✅ 删除会话时同时删除相关的所有对话日志
- ❌ 尝试删除他人会话返回 403 错误

**权限检查**：
```python
# 检查权限：只能删除自己创建的会话
if str(session.created_by) != str(current_user.id):
    return error_response(
        message="无权删除该会话，只能删除自己创建的会话",
        code=status.HTTP_403_FORBIDDEN
    )
```

### 6. 标题生成权限

**接口**: `POST /api/session/generate-title`

**权限规则**：
- ✅ 只能为自己创建的会话生成标题
- ❌ 尝试为他人会话生成标题返回 403 错误

**权限检查**：
```python
# 检查权限：只能为自己创建的会话生成标题
if str(session.created_by) != str(current_user.id):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="无权操作该会话，只能为自己创建的会话生成标题"
    )
```

## 数据库层面支持

### 新增CRUD方法

在 `src/model/crud_session.py` 中新增：

#### 1. 按智能体和用户查询会话
```python
def get_by_agent_and_user(
    self,
    db: DBSession,
    agent_id: str,
    created_by: str,
    skip: int = 0,
    limit: int = 100
) -> List[Session]
```

#### 2. 统计智能体和用户的会话数量
```python
def count_by_agent_and_user(
    self, 
    db: DBSession, 
    agent_id: str, 
    created_by: str
) -> int
```

## HTTP状态码

### 成功响应
- `200 OK` - 操作成功
- `200 OK (SSE)` - 流式响应

### 错误响应
- `401 Unauthorized` - 未登录或Token无效
- `403 Forbidden` - 无权操作该资源
- `404 Not Found` - 会话不存在
- `500 Internal Server Error` - 服务器错误

## 权限验证流程

### 查询会话列表流程
```
1. 验证用户登录 (JWT Token)
   ↓
2. 获取 agent_id 和 current_user.id
   ↓
3. 查询数据库 WHERE agent_id = ? AND created_by = ?
   ↓
4. 返回结果（只包含用户自己的会话）
```

### 修改/删除会话流程
```
1. 验证用户登录 (JWT Token)
   ↓
2. 根据 session_id 查询会话
   ↓
3. 检查会话是否存在
   ↓
4. 检查 session.created_by == current_user.id
   ↓
5. 权限验证通过 → 执行操作
   权限验证失败 → 返回 403 错误
```

## 使用示例

### 示例1：查询会话列表

**请求**：
```bash
curl -X POST "http://localhost:8000/api/session/list" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "demo_agent",
    "page": 1,
    "page_size": 20
  }'
```

**响应**：
```json
{
  "code": 200,
  "message": "查询成功",
  "result": {
    "items": [
      {
        "id": 1,
        "session_id": 1000000001,
        "agent_id": "demo_agent",
        "title": "关于天气的讨论",
        "created_at": "2025-01-10T10:00:00",
        "updated_at": "2025-01-10T11:00:00"
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "has_prev": false,
    "has_next": false
  }
}
```
> 注意：只会返回当前用户在该智能体下创建的会话

### 示例2：尝试修改他人会话（失败）

**请求**：
```bash
curl -X PUT "http://localhost:8000/api/session/update" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 9999999999,
    "title": "新标题"
  }'
```

**响应**：
```json
{
  "code": 403,
  "message": "无权修改该会话，只能修改自己创建的会话",
  "result": null
}
```

## 安全建议

1. **Token 安全**
   - 使用 HTTPS 传输
   - 定期刷新 Token
   - Token 过期时间不宜过长

2. **数据隔离**
   - 每个用户只能看到自己的数据
   - 使用 `created_by` 字段进行强制过滤

3. **日志记录**
   - 所有操作都会记录用户ID
   - 便于审计和追踪

4. **前端配合**
   - 前端也应该只显示用户自己的会话
   - 隐藏不必要的操作按钮
   - 但后端权限是最终防线

## 总结

✅ **已实现的权限控制**：
1. 所有接口需要登录才能访问
2. 会话列表只显示当前用户创建的会话（agent_id + created_by 双重过滤）
3. 修改会话需要验证创建者权限
4. 删除会话需要验证创建者权限
5. 生成标题需要验证创建者权限

✅ **数据安全**：
- 用户之间数据完全隔离
- 无法跨用户查看或操作会话
- 所有操作都有日志记录

