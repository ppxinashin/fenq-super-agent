# 用户登录注册功能实现总结

## 功能概述

已完成用户登录注册和用户管理功能的实现。

## 实现的功能

- ✅ 用户注册功能
- ✅ 用户登录功能
- ✅ 用户登出功能
- ✅ 获取用户信息功能
- ✅ JWT Token 生成和验证
- ✅ Redis 缓存用户信息

## 实现的文件

### 核心代码文件

| 文件 | 说明 |
|------|------|
| `src/config/settings.py` | JWT配置（密钥、算法、过期时间） |
| `src/api/request/user_request.py` | 用户请求模型（注册、登录） |
| `src/api/response/user_response.py` | 用户响应模型 |
| `src/utils/jwt_util.py` | JWT工具类 |
| `src/utils/redis_util.py` | Redis工具类 |
| `src/api/controller/user_controller.py` | 用户控制器 |

## 核心功能说明

### 1. 注册功能

**验证规则**：
- 用户名：最多20个字符，只支持大小写字母和下划线
- 密码：至少8位，只允许ASCII可见字符
- 密码确认：两次输入的密码必须一致

### 2. 登录功能

**流程**：
1. 验证用户名和密码
2. 生成 JWT Token
3. 将 Token 和用户信息存储到 Redis
4. 返回 Token 和用户信息

### 3. Token 验证

**流程**：
1. 解码 JWT Token
2. 检查 Token 是否过期
3. 从 Redis 获取用户信息

### 4. 登出功能

**流程**：
1. 验证 Token 有效性
2. 从 Redis 删除 Token

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. 初始化数据库

```bash
python -m src.model.init_db
```

### 4. 启动服务

```bash
python examples/auth_example.py
```

## 技术特点

### 1. 安全性

- 密码使用 MD5 + 随机盐值加密
- JWT Token 包含过期时间
- 严格的密码格式验证

### 2. 性能

- Redis 缓存用户信息
- Token 自动过期机制
- 单例模式的 Redis 客户端
