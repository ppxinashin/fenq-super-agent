# Fenq Super Agent - 多智能体交互系统

<div align="center">

![Fenq Super Agent](https://img.shields.io/badge/AUTHOR-JEHOL%20FENQ-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.120.3-green?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-1.0.3-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

[API文档](http://localhost:8000/docs) • [在线演示](#) • [更新日志](CHANGELOG.md)

</div>

## 🌟 项目简介

Fenq Super Agent 是一个功能完整的多智能体交互系统，旨在为用户提供高度自定义的AI智能体体验。项目最初专用于足球智能体，现已扩展为通用的智能体平台，鼓励用户创建、分享和定制自己的智能体。

### 🎯 核心价值

- **高度自定义**：不同于市面同类产品专注于特定类型（海龟汤、恋爱大师），我们提供完全自定义的智能体创建能力
- **知识库隔离**：不同智能体、不同用户的知识库完全隔离，确保回复的纯洁性和准确性
- **工具生态丰富**：集成多种工具和MCP协议，支持个性化工具选择
- **管理完善**：提供完整的用户管理、智能体管理、会话管理功能

## ✨ 主要功能

### 🤖 智能体管理
- **创建智能体**：支持自定义系统提示词、工具选择、MCP配置
- **编辑智能体**：实时更新智能体配置，优化回复效果
- **删除智能体**：灵活管理智能体生命周期
- **智能体市场**：浏览和发现其他用户分享的智能体

### 💬 聊天交互
- **流式对话**：实时流畅的对话体验
- **会话管理**：支持多会话并行，自动生成会话标题
- **历史记录**：完整的聊天记录保存和查询
- **上下文理解**：基于对话历史的智能回复

### 🧠 记忆系统
- **短期记忆**：基于Redis的会话级记忆
- **长期记忆**：基于PGVector的持久化语义记忆
- **记忆同步**：手动/自动记忆同步机制
- **记忆开关**：用户可控的记忆功能开关

### 📁 文件处理
- **文件上传**：支持多种格式文件上传
- **RAG集成**：自动文件分块、向量化、检索
- **文件管理**：文件列表、预览、批量删除
- **实时监听**：文件上传/删除的实时RAG处理

### 🔧 工具集成
- **内置工具**：网页抓取、文件操作、终端执行、网络搜索、计算器等
- **MCP协议**：支持Model Context Protocol，可扩展第三方工具
- **工具配置**：按智能体个性化配置可用工具
- **自定义工具**：支持用户开发自定义工具

### 👥 用户管理
- **角色权限**：管理员和普通用户角色分离
- **用户认证**：JWT令牌认证，支持刷新机制
- **用户操作**：注册、登录、密码修改、信息管理
- **管理员功能**：用户管理、智能体管理、系统配置

## 🏗️ 技术架构

### 后端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| **Web框架** | FastAPI 0.120.3 | 高性能异步Web框架 |
| **ASGI服务器** | Uvicorn 0.38.0 | 异步服务器 |
| **数据验证** | Pydantic 2.12.3 | 数据建模和验证 |
| **AI框架** | LangChain 1.0.3 | AI应用开发框架 |
| **工作流编排** | LangGraph 1.0.2 | 复杂工作流编排 |
| **数据库** | PostgreSQL | 主数据库 |
| **缓存** | Redis | 缓存和短期记忆 |
| **向量存储** | PGVector | 长期记忆和RAG |
| **对象存储** | MinIO | 文件存储 |
| **认证** | JWT | 无状态认证 |
| **日志** | Loguru | 结构化日志 |

### AI模型支持

- **OpenAI API**：GPT-3.5、GPT-4系列
- **阿里云通义千问**：qwen系列模型
- **本地模型**：支持OpenAI兼容的本地部署
- **自定义模型**：易于扩展的模型适配器

### 核心特性

- **异步架构**：基于FastAPI的高并发异步处理
- **模块化设计**：清晰的分层架构，易于扩展和维护
- **流式响应**：Server-Sent Events实现实时对话
- **健康检查**：完整的系统和组件健康监控
- **错误处理**：统一的异常处理和错误响应
- **日志追踪**：详细的操作日志和错误追踪

## 📦 项目结构

```
suagent-server/
├── src/                          # 核心源代码
│   ├── agents/                   # Agent构建和管理
│   │   └── my_agent.py          # 主Agent构建类
│   ├── api_middlewares/          # API中间件
│   │   └── exception_middleware.py  # 异常处理中间件
│   ├── config/                   # 配置管理
│   │   └── settings.py          # 应用配置
│   ├── controller/               # 控制器层
│   │   ├── auth_controller.py   # 认证控制器
│   │   ├── agent_manage_controller.py  # Agent管理
│   │   ├── chat_controller.py   # 聊天控制器
│   │   ├── file_manage_controller.py   # 文件管理
│   │   └── user_manage_controller.py   # 用户管理
│   ├── memory/                   # 记忆管理
│   │   ├── redis_short_memory.py  # 短期记忆
│   │   └── pg_vector_memory.py   # 长期记忆
│   ├── model/                    # 数据模型
│   │   ├── database.py          # 数据库连接
│   │   ├── init_db.py           # 数据库初始化
│   │   ├── User.py              # 用户模型
│   │   ├── Agent.py             # Agent模型
│   │   └── Session.py           # 会话模型
│   ├── service/                  # 业务逻辑服务
│   │   ├── auth_service.py      # 认证服务
│   │   ├── chat_service.py      # 聊天服务
│   │   ├── agent_manage_service.py  # Agent管理服务
│   │   ├── file_manage_service.py   # 文件管理服务
│   │   └── user_manage_service.py   # 用户管理服务
│   ├── tools/                    # 工具集
│   │   ├── web_scraper.py       # 网页抓取
│   │   ├── file_opt.py          # 文件操作
│   │   ├── terminal_opt.py      # 终端操作
│   │   ├── web_search.py        # 网络搜索
│   │   └── rag.py               # RAG工具
│   ├── workflow/                 # 工作流程
│   │   └── rag/                 # RAG工作流
│   │       ├── rag_workflow.py  # RAG主工作流
│   │       ├── generate_answer.py  # 答案生成
│   │       └── grade_documents.py   # 文档评分
│   ├── mcp_client/               # MCP客户端
│   ├── utils/                    # 工具类
│   └── main.py                   # 应用入口
├── demo/                         # 演示脚本
├── scripts/                      # 脚本文件
├── logs/                         # 日志目录
├── main.py                       # 应用入口（根目录）
├── start_server.py              # 启动脚本
├── check_environment.py         # 环境检查
├── requirements.txt             # 依赖包
├── .env.example                 # 环境变量模板
├── .env                         # 环境变量配置
└── mcp-servers.json             # MCP服务器配置
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.13
- **PostgreSQL**: 17
- **Redis**: 8.2
- **MinIO**: 20250422（最后一个支持完整管理端的版本）

### 安装部署

1. **克隆项目**
```bash
git clone https://github.com/jeholppx/fenq-super-agent.git
cd fenq-super-agent/suagent-server
```

2. **创建虚拟环境**
```bash
# 使用conda
conda create -n suagent-server python=3.13
conda activate suagent-server

```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis、AI模型等参数
```

5. **初始化数据库**
```bash
python check_environment.py
```

6. **启动服务**
```bash
# 开发模式
python start_server.py

# 或使用uvicorn直接启动
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

7. **验证部署**
- 访问 http://localhost:8000 查看服务状态
- 访问 http://localhost:8000/docs 查看API文档
- 访问 http://localhost:8000/health 查看健康检查

### Docker部署

```bash
# 构建镜像
docker build -t fenq-super-agent .

# 运行容器
docker run -d \
  --name suagent-server \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e REDIS_URL="redis://..." \
  fenq-super-agent
```

## 📚 API文档

### 基础信息

- **基础URL**: `http://localhost:8000`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON (ApiResponse统一格式)
- **API版本**: v1

### 认证方式

所有需要认证的接口都需要在请求头中提供：
```http
Authorization: Bearer <JWT_TOKEN>
```

### 主要接口模块

#### 1. 认证模块 (`/api/v1/auth`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/register` | POST | 用户注册 |
| `/login` | POST | 用户登录 |
| `/logout` | POST | 用户退出 |
| `/change-password` | POST | 修改密码 |
| `/me` | GET | 获取当前用户信息 |
| `/validate-token` | POST | 验证Token有效性 |
| `/refresh-token` | POST | 刷新Token |

**登录示例**：
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

#### 2. 智能体管理 (`/api/v1/agents`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/agents` | GET | 智能体列表 |
| `/agents` | POST | 创建智能体 |
| `/agents` | PUT | 修改智能体 |
| `/agents/{agent_id}` | GET | 智能体详情 |
| `/agents/{agent_id}` | DELETE | 删除智能体 |
| `/agents/cards` | GET | 智能体卡片展示 |
| `/agents/tools` | PUT | 更新智能体工具 |
| `/agents/mcp` | PUT | 更新MCP配置 |

**创建智能体示例**：
```bash
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_agent",
    "agent_name": "我的智能体",
    "description": "这是一个自定义智能体",
    "system_prompt": "你是一个有帮助的AI助手",
    "available_tools": ["web_search", "file_read"],
    "mcp_status": false
  }'
```

#### 3. 聊天交互 (`/api/v1/chat`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/chat` | GET | 智能体对话（流式） |
| `/sessions` | GET | 会话列表 |
| `/sessions` | POST | 创建会话 |
| `/sessions/{session_id}` | DELETE | 删除会话 |
| `/sessions/{session_id}/title` | PUT | 更新会话标题 |
| `/sessions/{session_id}/messages` | GET | 聊天记录 |

**聊天示例（流式）**：
```bash
curl -X GET "http://localhost:8000/api/v1/chat?agent_id=my_agent&session_id=123&message=你好" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Accept: text/event-stream"
```

#### 4. 文件管理 (`/api/v1/files`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/files/upload` | POST | 上传文件 |
| `/files` | GET | 文件列表 |
| `/files/chunks` | GET | 文件分块查看 |
| `/files` | DELETE | 删除文件 |
| `/files/batch-delete` | POST | 批量删除文件 |

**文件上传示例**：
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload?agent_id=my_agent" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/path/to/your/file.txt"
```

#### 5. 用户管理 (`/api/v1/users`)

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/users` | GET | 用户列表 | 管理员 |
| `/users` | POST | 创建用户 | 管理员 |
| `/users` | PUT | 修改用户 | 管理员 |
| `/users/{user_id}` | GET | 用户详情 | 管理员 |
| `/users/{user_id}` | DELETE | 删除用户 | 管理员 |

#### 6. 记忆管理 (`/api/v1/memory`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/memory-setting` | GET | 查询记忆状态 |
| `/memory-setting` | POST | 设置记忆开关 |
| `/memory-sync` | POST | 手动同步记忆 |

### 统一响应格式

所有接口都遵循统一的响应格式：

```json
{
  "code": 200,              // 状态码 (200成功, 299业务错误, 500系统错误)
  "message": "响应消息",     // 响应说明
  "result": {}              // 响应数据 (可为空)
}
```

### 错误码说明

- **200**: 成功
- **299**: 业务错误（参数错误、权限不足等）
- **400**: 请求参数错误
- **401**: 未认证
- **403**: 权限不足
- **404**: 资源不存在
- **500**: 系统错误

## 🔧 配置说明

### 环境变量配置

主要环境变量说明：

```bash
# 应用配置
APP_NAME="Fenq Super Agent"
APP_VERSION="1.0.0"
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# 数据库配置
DATABASE_URL="postgresql://username:password@localhost:5432/suagent"

# Redis配置
REDIS_URL="redis://localhost:6379/0"

# AI模型配置
OPENAI_API_KEY="your-openai-api-key"
OPENAI_BASE_URL="https://api.openai.com/v1"
DASHSCOPE_API_KEY="your-dashscope-api-key"

# JWT配置
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 文件存储配置
MINIO_ENDPOINT="localhost:9000"
MINIO_ACCESS_KEY="your-minio-access-key"
MINIO_SECRET_KEY="your-minio-secret-key"
MINIO_BUCKET_NAME="suagent-files"
```

### MCP服务器配置

在 `mcp-servers.json` 中配置可用的MCP服务器：

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["weather_server.py"],
      "env": {
        "API_KEY": "weather-api-key"
      }
    }
  }
}
```

## 🎯 使用场景

### 1. 个人智能助手
创建专属的个人AI助手，集成日历、邮件、文件管理等工具。

### 2. 客服机器人
构建企业的智能客服系统，集成知识库查询、工单管理等业务功能。

### 3. 教育辅导
开发个性化的教育辅导智能体，支持学科问答、学习进度跟踪。

### 4. 内容创作
打造内容创作助手，集成网络搜索、文档分析、创意生成工具。

### 5. 技术支持
构建技术支持智能体，集成代码分析、文档查询、问题诊断工具。

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 开发流程

1. **Fork项目**
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **提交Pull Request**

### 开发规范

- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 确保所有测试通过
- 更新相关文档

### 代码提交规范

```
type(scope): description

[optional body]

[optional footer]
```

类型说明：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目的支持：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [LangChain](https://python.langchain.com/) - AI应用开发框架
- [PostgreSQL](https://www.postgresql.org/) - 强大的开源数据库
- [Redis](https://redis.io/) - 内存数据结构存储
- [MinIO](https://min.io/) - 高性能对象存储

## 📞 联系我们

- **项目主页**: https://github.com/your-username/fenq-super-agent
- **问题反馈**: https://github.com/your-username/fenq-super-agent/issues
- **邮箱**: your-email@example.com
- **文档**: https://docs.fenq-super-agent.com

## 🗺️ 路线图

### v1.1 (计划中)
- [ ] 智能体市场功能
- [ ] 更多内置工具集成
- [ ] 性能优化和监控
- [ ] 多语言支持

### v1.2 (规划中)
- [ ] 图形化配置界面
- [ ] 插件系统
- [ ] 分布式部署支持
- [ ] 高级分析功能

### v2.0 (长期规划)
- [ ] 多模态支持（图像、语音）
- [ ] 移动端支持
- [ ] 企业级功能
- [ ] 云服务集成

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐️**

Made with ❤️ by Jehol FENQ

</div>