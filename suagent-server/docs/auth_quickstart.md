# 认证功能快速入门指南

## 快速开始

### 1. 安装依赖

```bash
cd /home/ubuntu/fenq-super-agent/suagent-server
pip install -r requirements.txt
```

### 2. 启动必要的服务

#### 启动 PostgreSQL

```bash
docker run -d --name postgres \
  -e POSTGRES_USER=suagent \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=super_agent_db \
  -p 5432:5432 postgres:latest
```

#### 启动 Redis

```bash
docker run -d --name redis \
  -p 6379:6379 redis:latest
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# JWT 配置
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# PostgreSQL 配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=suagent
POSTGRES_PASSWORD=postgres
POSTGRES_DB=super_agent_db
```

### 4. 初始化数据库

```bash
python -m src.model.init_db
```

### 5. 启动认证服务

```bash
python examples/auth_example.py
```

服务将在 `http://localhost:8000` 启动

### 6. 访问 API 文档

在浏览器中打开：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 在你的 FastAPI 应用中集成

### 方法 1: 直接导入路由

```python
from fastapi import FastAPI
from src.api.controller import user_router

app = FastAPI()
app.include_router(user_router)
```

### 方法 2: 自定义路由前缀

```python
from fastapi import FastAPI
from src.api.controller.user_controller import router

app = FastAPI()
app.include_router(router, prefix="/auth", tags=["认证"])
```

## 验证规则

### 用户名

- 最多 20 个字符
- 只支持大小写字母和下划线
- 正则表达式: `^[a-zA-Z_]+$`

### 密码

- 至少 8 位
- 只允许 ASCII 可见字符（ASCII 码 33-126）

## 安全建议

### 生产环境配置

1. **修改 JWT 密钥**

```env
JWT_SECRET_KEY=使用一个强随机字符串
```

可以使用 Python 生成：

```python
import secrets
print(secrets.token_urlsafe(32))
```

2. **使用 HTTPS**

确保在生产环境中使用 HTTPS 传输 Token。

3. **设置 Redis 密码**

```env
REDIS_PASSWORD=your-redis-password
```
