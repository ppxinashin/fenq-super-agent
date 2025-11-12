# SuAgent Server

智能体服务器，提供完整的RESTful API接口，支持文件管理、会话管理、Agent管理等功能。

## 🔧 环境设置

### Conda 环境

本项目使用专门的 conda 环境：`suagent-server`

```bash
# 检查环境
python check_environment.py

# 确认在正确环境中
which python  # 应该指向: /home/ubuntu/miniconda3/envs/suagent-server/bin/python
```

### 环境要求

- ✅ Python 3.13.9 (conda suagent-server环境)
- PostgreSQL
- Redis
- MinIO

## 🚀 快速开始

### 1. 环境检查

```bash
# 验证环境配置
python check_environment.py
```

### 2. 安装依赖

```bash
# 在suagent-server conda环境中
pip install -r requirements.txt
```

### 3. 启动服务器

```bash
# 启动API服务器
python start_server.py
```

### 4. 测试认证功能

```bash
# 运行完整认证测试
python test_auth.py
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件配置数据库和其他服务
```

### 4. 启动服务

```bash
# 默认启动（开发模式）
python main.py

# 自定义配置
python main.py --host 0.0.0.0 --port 8080

# 生产模式
python main.py --workers 4 --log-level warning

# 调试模式
python main.py --reload --debug
```

### 5. 访问API文档

启动成功后，可以通过以下地址访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 📋 主要功能

### 🔐 用户管理
- 用户注册、登录、登出
- JWT身份验证
- 用户信息管理
- 管理员权限控制

### 🤖 Agent管理
- Agent创建、更新、删除
- Agent配置管理
- 工具绑定和MCP服务器配置
- Agent使用统计

### 💬 会话管理
- 会话创建、删除
- 会话历史记录
- 会话标题管理
- 多Agent支持

### 📁 文件管理
- 文件上传、下载
- 文件夹创建和管理
- RAG分块浏览
- 文件删除和权限控制

## 🛠️ 启动参数

```bash
python main.py --help
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--host` | 0.0.0.0 | 服务器监听地址 |
| `--port` | 8000 | 服务器端口 |
| `--reload` | False | 开启热重载（开发模式） |
| `--debug` | False | 开启调试模式 |
| `--workers` | 1 | 工作进程数 |
| `--log-level` | info | 日志级别 |

## 📁 项目结构

```
suagent-server/
├── main.py                     # 主入口文件
├── src/                        # 源代码目录
│   ├── api/                    # API接口层
│   │   ├── controller/         # 控制器
│   │   └── services/           # 服务层
│   ├── model/                  # 数据模型
│   ├── config/                 # 配置
│   ├── utils/                  # 工具类
│   └── app.py                  # FastAPI应用
├── docs/                       # 文档
├── scripts/                    # SQL脚本
├── demo/                       # 示例代码
└── requirements.txt            # 依赖包列表
```

## 📖 API文档

### 核心接口

#### 用户相关
- `POST /api/user/register` - 用户注册
- `POST /api/user/login` - 用户登录
- `GET /api/user/info` - 获取用户信息

#### Agent相关
- `GET /api/agent/list` - 获取Agent列表
- `POST /api/agent/select` - 选择Agent
- `POST /api/agent/chat` - Agent对话

#### 文件管理
- `POST /api/file-management/upload` - 文件上传
- `GET /api/file-management/list` - 文件列表
- `DELETE /api/file-management/delete` - 文件删除

详细API文档请访问：http://localhost:8000/docs

## 🔧 配置说明

主要环境变量：

```bash
# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=suagent
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# MinIO配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_BUCKET=suagent

# JWT配置
JWT_SECRET_KEY=your_secret_key
JWT_EXPIRE_MINUTES=1440

# 调试模式
DEBUG=true
```

## 📄 许可证

本项目采用 MIT 许可证。