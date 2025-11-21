# Fenq Super Agent

<div align="center">

![Fenq Super Agent](https://img.shields.io/badge/AUTHOR-JEHOL%20FENQ-blue?style=for-the-badge)
![Multi-Agent](https://img.shields.io/badge/Architecture-Micro--Service-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-Apache-yellow?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.1.0-orange?style=for-the-badge)

[快速开始(后发)](#-快速开始) • [项目文档(后发)](#-详细文档) • [在线演示](http://suagent.jehol-ppx.com/) • [API文档](https://fenq-suagent.apifox.cn/)

</div>

## 📊 项目功能一览
![智能体市场](pics/1.png)
![会话](pics/2.png)
![知识库](pics/6.png)
![创建](pics/3.png)
![智能体管理](pics/4.png)
![用户管理](pics/5.png)


## 🌟 项目简介

Fenq Super Agent 是一个企业级的多智能体交互系统，采用现代化的微服务架构。项目基于 **LangChain 1.0.3 + LangGraph 1.0.2** 构建，集成先进的大语言模型技术、向量检索、消息队列和容器化部署，支持高度可扩展的智能体生态。

### 🎯 核心特性

- **🏗️ 微服务架构**：5个独立服务，支持水平扩展和高可用部署
- **🧠 双层记忆系统**：Redis 短期记忆 + PGVector 长期记忆
- **🔧 MCP 协议支持**：Model Context Protocol，可扩展工具生态
- **📁 智能RAG系统**：支持多格式文档，混合检索（向量+BM25）
- **🔒 企业级安全**：JWT 认证 + RBAC 权限控制
- **⚡ 高性能异步**：FastAPI + RabbitMQ + SSE 流式响应

## 🏗️ 系统架构

### 微服务架构图

```mermaid
graph TB
    subgraph "前端服务"
        A[🎨 suagent-app<br/>Next.js 16.0.3 + TypeScript<br/>Material-UI v7.3.5<br/>:11451]
    end

    subgraph "核心服务"
        B[🚀 suagent-server<br/>FastAPI 0.120.3<br/>LangChain 1.0.3 + LangGraph 1.0.2<br/>:8000]
        C[📄 suagent-rag<br/>RAG + 文档处理<br/>事件驱动]
        D[⚡ suagent-task<br/>任务调度 + MQ<br/>APScheduler + RabbitMQ]
        E[🎥 suagent-youtube-mcp<br/>YouTube 数据服务<br/>MCP Protocol<br/>:10086]
    end

    subgraph "基础设施"
        F[🗄️ PostgreSQL + PGVector<br/>主数据库 + 向量检索]
        G[💾 Redis<br/>缓存 + 短期记忆]
        H[📬 RabbitMQ<br/>消息队列]
        I[📦 MinIO<br/>对象存储]
    end

    subgraph "外部服务"
        J[🤖 OpenAI API<br/>langchain-openai 1.0.1]
        K[🧠 阿里云通义千问<br/>dashscope 1.24.7]
        L[🔍 网络搜索<br/>ddgs 9.8.0]
    end

    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    B --> H
    B --> I
    B --> J
    B --> K
    C --> I
    E --> L
    D --> H
```

## 📦 服务组件

### 🎨 suagent-app (前端应用)
- **技术栈**: Next.js 16.0.3, TypeScript, Material-UI v7.3.5, Tailwind CSS
- **端口**: 11451
- **核心功能**: 用户界面，智能体管理，实时聊天，文件管理，用户系统

### 🚀 suagent-server (核心API服务)
- **技术栈**: FastAPI 0.120.3, LangChain 1.0.3, LangGraph 1.0.2, Pydantic 2.12.3
- **端口**: 8000
- **核心功能**: 用户认证，智能体管理，聊天流式响应，MCP客户端集成，记忆系统

### 📄 suagent-rag (RAG服务)
- **技术栈**: MinIO 7.2.16, PGVector, PyPDF 6.1.3, MarkItDown 0.1.3
- **核心功能**: 文档处理，实时文件监听，自动分块向量化，混合检索（向量+BM25）

### ⚡ suagent-task (任务调度服务)
- **技术栈**: APScheduler, RabbitMQ 4.2.0, aio-pika
- **核心功能**: 定时任务调度，消息队列处理，记忆同步任务（每2小时），任务重试机制

### 🎥 suagent-youtube-mcp (MCP服务)
- **技术栈**: YouTube API, MCP Protocol, SSE
- **端口**: 10086
- **核心功能**: YouTube数据获取，视频信息查询，MCP协议支持

### 🤖 智能体管理
- **自定义智能体**: 支持自定义系统提示词、工具配置、MCP设置
- **智能体市场**: 发现和分享其他用户创建的智能体
- **个性化配置**: 按智能体配置不同工具和功能模块

### 💬 智能对话
- **实时流式对话**: 基于 Server-Sent Events 的流畅对话体验
- **多会话管理**: 支持多会话并行，自动生成会话标题
- **上下文理解**: 基于对话历史的智能回复和记忆

### 🧠 记忆系统
- **双层记忆架构**: Redis 短期记忆 + PGVector 长期记忆
- **自动记忆同步**: 定时将聊天记录同步到长期记忆
- **用户可控**: 记忆功能开关，用户可控制是否启用

### 📁 RAG 文档处理
- **多格式支持**: PDF、DOCX、PPTX、XLSX 等文档格式
- **智能分块**: 自动文档分块、向量化处理
- **混合检索**: 向量检索 + BM25 算法，提高检索准确性
- **实时监听**: 文件上传/删除的实时 RAG 处理

### 🔧 工具生态
- **内置工具**: 网页抓取、文件操作、网络搜索等
- **MCP 协议**: Model Context Protocol，支持第三方工具扩展
- **YouTube 集成**: 通过 MCP 服务提供 YouTube 数据访问

### 👥 用户系统
- **角色权限**: 管理员和普通用户权限分离
- **JWT 认证**: 无状态认证，安全可靠
- **用户操作**: 注册、登录、密码管理、个人信息设置

## 🚀 快速开始

### 📋 环境要求
- **Python**: 3.13
- **Node.js**: 24.11.1
- **PostgreSQL**: 17 (需要 PGVector 扩展)
- **Redis**: 
- **Docker & Docker Compose**: latest

### 🐳 一键部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/jeholppx/fenq-super-agent.git
cd fenq-super-agent

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的 API 密钥等

# 3. 启动所有服务
docker-compose up -d --build

# 4. 等待服务启动完成（约2-3分钟）
docker-compose logs -f

# 5. 验证部署
curl http://localhost:8000/health
```

### 🎯 访问服务
- **前端应用**: http://localhost:11451
- **API 文档**: http://localhost:8000/docs
- **MinIO 控制台**: http://localhost:9001
- **RabbitMQ 管理界面**: http://localhost:15672

## 📚 技术栈

### 前端技术
- **Next.js 16.0.3**: React 全栈框架，支持 SSR 和静态生成
- **TypeScript**: 类型安全的 JavaScript 超集
- **Material-UI v7.3.5**: React UI 组件库，实现 Material Design(仅Markdown功能)
- **Tailwind CSS**: 实用优先的 CSS 框架

### 后端技术
- **Python 3.13**: 主要编程语言
- **FastAPI 0.120.3**: 现代、快速的 Web 框架
- **LangChain 1.0.3 + LangGraph 1.0.2**: AI 应用开发框架
- **Pydantic 2.12.3**: 数据验证和序列化

### 数据存储
- **PostgreSQL + PGVector**: 主数据库 + 向量检索
- **Redis**: 缓存和短期记忆存储
- **MinIO**: S3 兼容的对象存储服务
- **RabbitMQ 4.2.0**: 消息队列和任务调度

### AI 集成
- **OpenAI API**: GPT 模型接口
- **阿里云通义千问**: 本土化大模型支持
- **MCP Protocol**: Model Context Protocol，工具扩展协议

## 🔧 配置说明

### 主要环境变量

```bash
# 数据库配置
DATABASE_URL="postgresql://username:password@localhost:5432/suagent"

# Redis 配置
REDIS_URL="redis://localhost:6379/0"

# MinIO 配置
MINIO_ENDPOINT="localhost:9000"
MINIO_ACCESS_KEY="your-access-key"
MINIO_SECRET_KEY="your-secret-key"

# AI 模型配置
OPENAI_API_KEY="your-openai-api-key"
DASHSCOPE_API_KEY="your-dashscope-api-key"

# JWT 配置
SECRET_KEY="your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## 📖 API 接口

### 认证模块
```http
POST /api/v1/auth/register    # 用户注册
POST /api/v1/auth/login       # 用户登录
GET  /api/v1/auth/me          # 获取当前用户信息
```

### 智能体管理
```http
GET    /api/v1/agents         # 获取智能体列表
POST   /api/v1/agents         # 创建智能体
PUT    /api/v1/agents/{id}    # 更新智能体
DELETE /api/v1/agents/{id}    # 删除智能体
```

### 聊天交互
```http
GET    /api/v1/chat           # 智能体对话（SSE 流式）
GET    /api/v1/sessions       # 会话列表
POST   /api/v1/sessions       # 创建会话
DELETE /api/v1/sessions/{id}  # 删除会话
```

### 文件管理
```http
POST   /api/v1/files/upload   # 上传文件
GET    /api/v1/files          # 文件列表
DELETE /api/v1/files          # 删除文件
GET    /api/v1/files/chunks   # 文件分块查看
```

## 🛠️ 开发指南

### 手动部署开发环境

```bash
# 1. 环境准备
python3 -m venv venv
source venv/bin/activate

# 2. 安装后端依赖
cd suagent-server && pip install -r requirements.txt
cd ../suagent-rag && pip install -r requirements.txt
cd ../suagent-task && pip install -r requirements.txt
cd ../suagent-youtube-mcp && pip install -r requirements.txt

# 3. 安装前端依赖
cd ../suagent-app
npm install

# 4. 启动数据库服务
请自行按照教程安装，教程后发

# 5. 启动后端服务
cd suagent-server && python start_server.py &
cd ../suagent-rag && python main.py &
cd ../suagent-task && python -m src.task_runner &
cd ../suagent-youtube-mcp && python mcp_run.py &

# 6. 启动前端服务
cd ../suagent-app && npm run dev
```

### 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📊 项目监控

### 健康检查
- **主服务**: http://localhost:8000/health
- **数据库**: http://localhost:8000/health/database
- **Redis**: http://localhost:8000/health/redis
- **MinIO**: http://localhost:8000/health/minio

### 日志管理
```bash
# 查看服务日志
docker-compose logs -f suagent-server
docker-compose logs -f suagent-app

# 应用日志目录
logs/
├── suagent-server/          # 主服务日志
├── suagent-rag/            # RAG服务日志
├── suagent-task/           # 任务调度日志
└── suagent-youtube-mcp/    # MCP服务日志
```

## 🚨 故障排除

### 常见问题

**Q: 服务启动失败**
```bash
# 检查端口占用
netstat -tulpn | grep :8000

# 检查服务状态
docker-compose ps
```

**Q: 数据库连接失败**
```bash
# 验证数据库连接
docker exec -it postgres psql -U suagent -d suagent -c "SELECT 1;"
```

**Q: 前端无法访问后端**
```bash
# 检查 CORS 配置
curl -H "Origin: http://localhost:11451" http://localhost:8000/health
```

## 💡 提示
前端的备案号是我的网站备案号，如果你的网站域名已经备案，记得改，没有备案空着，然后把这段注掉
位于`suagent-app/components/Footer.tsx`
```html
<div>
  <a
    href="https://beian.miit.gov.cn/"
    target="_blank"
    rel="noopener noreferrer"
    className="text-gray-500 hover:text-gray-700 transition-colors text-sm"
  >
    网站注册备案号：冀ICP备2022002900号-1
  </a>
</div>
```


## 📄 许可证

本项目采用 Apache 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目的支持：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化 Python Web 框架
- [Next.js](https://nextjs.org/) - React 全栈框架
- [LangChain](https://docs.langchain.com/) - AI 应用开发框架
- [PostgreSQL](https://www.postgresql.org/) - 开源对象关系数据库
- [MinIO](https://www.min.io/docs/) - 高性能对象存储
- [Material-UI](https://mui.com/material-ui/) - React UI 组件库

## 📞 联系方式

- **项目维护者**: Jehol FENQ
- **GitHub Issues**: [提交问题](https://github.com/jeholppx/fenq-super-agent/issues)
- **在线演示**: [http://suagent.jehol-ppx.com/](http://suagent.jehol-ppx.com/)

---

<div align="center">

## 🌟 感谢您的关注和支持！

**如果这个项目对您有帮助，请给我们一个 ⭐️**

[![Star History Chart](https://api.star-history.com/svg?repos=jeholppx/fenq-super-agent&type=Date)](https://star-history.com/#jeholppx/fenq-super-agent&Date)


Made with ❤️ by Jehol FENQ

**© 2024 Fenq Super Agent. All rights reserved.**

</div>

