# 用户认证与授权 API 文档

## 概述

本文档描述了 Fenq Super Agent 系统的用户认证与授权功能，包括注册、登录、退出登录等功能。

## 技术特性

- **JWT Token**: 使用 JSON Web Token 进行身份验证
- **Redis 存储**: Token 和用户信息存储在 Redis 中，支持快速查询和撤销
- **密码加密**: MD5(明文密码 + salt) 方式加密存储
- **角色权限**: 支持 admin 和 user 两种角色
- **中间件保护**: 提供 JWT 认证中间件保护需要授权的 API

## API 端点

### 基础路径
```
http://localhost:8000/api/v1/auth
```

### 1. 用户注册

**POST** `/register`

注册一个新用户账户。

#### 请求参数
```json
{
  "username": "new_user",
  "password": "password123",
  "confirm_password": "password123"
}
```

**参数说明:**
- `username`: 用户名，3-50个字符，只允许大小写字母、数字和下划线
- `password`: 密码，至少8位ASCII可见字符
- `confirm_password`: 确认密码，必须与密码一致

#### 响应示例
```json
{
  "code": 200,
  "message": "注册成功",
  "result": {
    "user_id": 2,
    "username": "new_user",
    "role": "user",
    "message": "注册成功"
  }
}
```

### 2. 用户登录

**POST** `/login`

使用用户名和密码登录系统。

#### 请求参数
```json
{
  "username": "admin",
  "password": "password123"
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "登录成功",
  "result": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user_info": {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-02T00:00:00Z"
    }
  }
}
```

### 3. 退出登录

**POST** `/logout`

用户退出登录系统，需要提供有效的 JWT token。

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应示例
```json
{
  "code": 200,
  "message": "退出登录成功",
  "result": {
    "message": "退出登录成功"
  }
}
```

### 4. 修改密码

**POST** `/change-password`

修改当前用户的密码。

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数
```json
{
  "old_password": "old_password123",
  "new_password": "new_password456",
  "confirm_password": "new_password456"
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "密码修改成功",
  "result": {
    "message": "密码修改成功"
  }
}
```

### 5. 获取当前用户信息

**GET** `/me`

获取当前登录用户的详细信息。

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应示例
```json
{
  "code": 200,
  "message": "获取用户信息成功",
  "result": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-02T00:00:00Z"
  }
}
```

### 6. Token 验证

**POST** `/validate-token`

验证提供的 JWT token 是否有效。

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应示例
```json
{
  "code": 200,
  "message": "Token有效",
  "result": {
    "valid": true,
    "user_info": {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-02T00:00:00Z"
    },
    "expires_at": "2024-01-02T00:00:00Z"
  }
}
```

### 7. 刷新 Token

**POST** `/refresh-token`

刷新当前的 JWT token，返回新的访问令牌。

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应示例
```json
{
  "code": 200,
  "message": "Token刷新成功",
  "result": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

### 8. 健康检查

**GET** `/health`

检查认证服务的健康状态。

#### 响应示例
```json
{
  "code": 200,
  "message": "认证服务运行正常",
  "result": {
    "status": "healthy",
    "redis_status": "connected",
    "jwt_config": {
      "algorithm": "HS256",
      "expire_minutes": 1440
    }
  }
}
```

## 错误响应

所有 API 错误都遵循统一的响应格式：

```json
{
  "code": 299,
  "message": "错误描述",
  "result": null
}
```

### 常见错误码

- `200`: 成功
- `299`: 业务错误
- `401`: 未认证
- `403`: 权限不足
- `500`: 服务器内部错误

### 常见错误消息

- `"用户名已存在"`: 注册时用户名重复
- `"用户名或密码错误"`: 登录凭据错误
- `"缺少有效的Authorization header"`: 未提供认证token
- `"token无效或已过期，请重新登录"`: JWT token无效或过期
- `"需要 admin 权限"`: 权限不足

## 使用示例

### Python 客户端示例

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 1. 用户注册
register_data = {
    "username": "test_user",
    "password": "password123",
    "confirm_password": "password123"
}

response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print("注册结果:", response.json())

# 2. 用户登录
login_data = {
    "username": "test_user",
    "password": "password123"
}

response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
login_result = response.json()
access_token = login_result["result"]["access_token"]
print("登录结果:", login_result)

# 3. 获取用户信息
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print("用户信息:", response.json())

# 4. 退出登录
response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
print("退出登录:", response.json())
```

### cURL 示例

```bash
# 注册用户
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "password123",
    "confirm_password": "password123"
  }'

# 用户登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "password123"
  }'

# 获取用户信息（替换 YOUR_ACCESS_TOKEN）
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 退出登录（替换 YOUR_ACCESS_TOKEN）
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 安全配置

### JWT 配置

在 `.env` 文件中配置 JWT 参数：

```env
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

### Redis 配置

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password
```

## 中间件使用

在需要认证的 API 端点中使用中间件：

```python
from fastapi import Depends
from src.api_middlewares.jwt_middleware import get_current_user_from_token, require_admin

@router.get("/protected-endpoint")
async def protected_endpoint(
    current_user: UserInfo = Depends(get_current_user_from_token)
):
    return {"message": f"Hello, {current_user.username}!"}

@router.get("/admin-only")
async def admin_only(
    current_user: UserInfo = Depends(require_admin)
):
    return {"message": "Admin access granted"}
```

## 测试

运行测试脚本验证认证功能：

```bash
# 启动服务器
python start_server.py

# 在另一个终端运行测试
python test_auth.py
```

## 部署注意事项

1. **生产环境配置**: 修改默认的 JWT 密钥和数据库密码
2. **HTTPS**: 生产环境必须使用 HTTPS 协议
3. **CORS**: 根据需要配置 CORS 策略
4. **日志监控**: 启用适当的日志记录和监控
5. **Redis 持久化**: 配置 Redis 持久化以防止 token 丢失