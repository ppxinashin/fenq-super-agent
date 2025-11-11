# 拦截器使用指南

## 拦截器类型

### 1. 登录验证拦截器 (`verify_token_interceptor`)

验证用户是否已登录（Header 中是否包含有效的 Token）。

**功能**：
- 检查 `Authorization` Header 是否存在
- 验证 Token 格式（支持 `Bearer {token}` 格式）
- 验证 Token 是否有效（未过期）
- 验证 Token 是否存在于 Redis（未登出）

### 2. 权限验证拦截器 (`verify_admin_interceptor`)

验证当前用户是否为管理员（角色为 admin）。

**功能**：
- 自动调用 `get_current_user` 获取当前用户
- 检查用户角色是否为 `admin`

### 3. 获取当前用户 (`get_current_user`)

从 Token 中获取当前登录的用户信息。

## 使用方法

### 1. 导入拦截器

```python
from fastapi import Depends
from src.api.interceptor import (
    verify_token_interceptor,
    verify_admin_interceptor,
    get_current_user
)
from src.model.user import User
```

### 2. 需要登录的接口

```python
@router.get("/protected")
async def protected_route(token: str = Depends(verify_token_interceptor)):
    return {"message": "这是一个受保护的接口"}
```

### 3. 获取用户信息

```python
@router.get("/user/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role.value
    }
```

### 4. 仅管理员可访问

```python
@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(verify_admin_interceptor)
):
    return {"message": f"用户 {user_id} 已被删除"}
```

### 5. 整个路由组添加拦截器

```python
# 所有接口都需要登录
router = APIRouter(
    prefix="/api/protected",
    dependencies=[Depends(verify_token_interceptor)]
)

# 所有接口都需要管理员权限
admin_router = APIRouter(
    prefix="/api/admin",
    dependencies=[Depends(verify_admin_interceptor)]
)
```

## 请求格式

### Authorization Header

```
Authorization: Bearer {your_token}
```

## 错误处理

### 未登录错误（401）

```json
{
  "detail": "未登录，请先登录"
}
```

### 无权限错误（403）

```json
{
  "detail": "无权限访问，仅管理员可操作"
}
```
