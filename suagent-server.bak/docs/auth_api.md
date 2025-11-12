# 用户认证 API 文档

## API 接口

### 1. 用户注册

**接口地址**: `POST /api/user/register`

**请求参数**:
```json
{
  "username": "zhangsan",
  "password": "Password123!",
  "password_confirm": "Password123!"
}
```

**参数说明**:
- `username`: 用户名，最多20个字符，只支持大小写字母和下划线
- `password`: 密码，至少8位，只允许ASCII范围内的可见字符（ASCII码33-126）
- `password_confirm`: 确认密码，必须与密码一致

### 2. 用户登录

**接口地址**: `POST /api/user/login`

**请求参数**:
```json
{
  "username": "zhangsan",
  "password": "Password123!"
}
```

**Token 存储**: JWT Token 存储在 Redis 中，默认 24 小时过期

### 3. 用户登出

**接口地址**: `POST /api/user/logout`

**请求参数**:
```json
{
  "token": "your_jwt_token"
}
```

### 4. 获取当前用户信息

**接口地址**: `GET /api/user/info`

**请求参数**: 通过查询参数传递 `token`

## 配置说明

### JWT 配置

在 `.env` 文件中配置：

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
REDIS_PASSWORD=
```
