# 用户管理功能使用指南

## 概述

用户管理功能提供了完整的用户增删改查能力，**所有接口都需要管理员权限**才能访问。

## API 接口

所有用户管理接口都需要在 Header 中提供管理员的 Token：
```
Authorization: Bearer {admin_token}
```

### 1. 新增用户

**接口地址**: `POST /api/admin/users/`

**请求参数**:
```json
{
  "username": "new_user",
  "password": "Password123!",
  "role": "user",
  "created_by": "admin"
}
```

### 2. 分页查询用户列表

**接口地址**: `GET /api/admin/users/`

**查询参数**:
- `page`: 页码（默认 1）
- `page_size`: 每页记录数（默认 10，范围 1-100）
- `keyword`: 搜索关键词（搜索用户名）

### 3. 查询用户详情

**接口地址**: `GET /api/admin/users/{user_id}`

### 4. 编辑用户信息

**接口地址**: `PUT /api/admin/users/{user_id}`

**注意**: 只能修改密码和角色，不能修改用户名

**请求参数**:
```json
{
  "password": "NewPassword123!",
  "role": "admin"
}
```

### 5. 删除用户

**接口地址**: `DELETE /api/admin/users/{user_id}`

**注意**: 软删除，不能删除自己

## 权限控制

所有用户管理接口都通过拦截器自动验证管理员权限：

```python
router = APIRouter(
    prefix="/api/admin/users",
    dependencies=[Depends(verify_admin_interceptor)]
)
```

## 搜索功能

支持通过 `keyword` 参数搜索用户名：

```
GET /api/admin/users/?keyword=test
```

## 安全建议

### 密码策略

- 密码至少 8 位
- 只允许 ASCII 可见字符
- 使用 MD5 + 盐值加密

### 权限控制

- 所有接口需要管理员权限
- 不能删除自己
- 详细的操作日志
