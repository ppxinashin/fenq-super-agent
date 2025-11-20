# Fenq Super Agent - 多智能体交互系统

<div align="center">

![Fenq Super Agent](https://img.shields.io/badge/AUTHOR-JEHOL%20FENQ-blue?style=for-the-badge)
![Multi-Agent](https://img.shields.io/badge/Architecture-Multi--Agent-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-Apache-yellow?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.1.0-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

[项目文档](#-详细文档) • [在线演示](#-快速体验) • [更新日志](CHANGELOG.md) • [API文档](http://localhost:8000/docs)

</div>

## 📋 目录

- [🌟 项目简介](#-项目简介)
- [🏗️ 系统架构](#️-系统架构)
- [📦 项目组件](#-项目组件)
- [✨ 主要功能](#-主要功能)
- [🚀 快速开始](#-快速开始)
- [📚 技术栈详解](#-技术栈详解)
- [🎯 使用场景](#-使用场景)
- [🛠️ 开发指南](#️-开发指南)
- [🔧 配置说明](#-配置说明)
- [📊 系统监控](#-系统监控)
- [🚨 故障排除](#-故障排除)
- [🤝 贡献指南](#-贡献指南)
- [📄 许可证](#-许可证)
- [🙏 致谢](#-致谢)

## 🌟 项目简介

Fenq Super Agent 是一个企业级的多智能体交互系统，采用现代化的微服务架构，为用户提供完全自定义的AI智能体体验。项目集成了先进的大语言模型技术、向量检索、消息队列和容器化部署，支持高度可扩展的智能体生态。

### 🎯 核心价值

- **🚀 企业级架构**：微服务设计，支持水平扩展和高可用部署
- **🧠 智能记忆系统**：双层记忆架构（Redis + PGVector），支持短期和长期记忆
- **🔧 丰富工具生态**：内置多种工具，支持MCP协议扩展，可集成第三方服务
- **🔒 安全可靠**：JWT认证 + RBAC权限控制，企业级安全保障
- **📊 实时监控**：完整的监控体系，支持Prometheus + Grafana集成

### ✨ 最新特性 (v2.1.0)

- **🔄 消息队列升级**：基于RabbitMQ 9.4.0的可靠消息传递
- **📁 增强RAG处理**：支持多种文档格式（PDF、DOCX、PPTX、XLSX）
- **🧠 LangChain集成**：完整集成LangChain 1.0.3和LangGraph 1.0.2
- **🔌 MCP协议支持**：Model Context Protocol，可扩展的工具生态
- **⚡ 性能优化**：异步处理 + 缓存策略，响应速度提升50%+
- **🎨 现代化界面**：基于Material-UI v7.3.5的响应式设计

## 🏗️ 系统架构

### 整体架构图

```mermaid
graph TB
    subgraph "前端层"
        A[suagent-app<br/>Next.js 16.0.3 + TypeScript<br/>端口: 11451<br/>Material-UI v7.3.5]
    end

    subgraph "网关层"
        B[Nginx/Caddy<br/>负载均衡 + SSL终端]
    end

    subgraph "业务服务层"
        C[suagent-server<br/>FastAPI 0.120.3<br/>LangChain 1.0.3 + LangGraph 1.0.2<br/>端口: 8000]
        D[suagent-rag<br/>文档处理 + RAG<br/>事件监听]
        E[suagent-task<br/>任务调度 + MQ<br/>APScheduler + RabbitMQ]
        F[suagent-youtube-mcp<br/>YouTube MCP<br/>MCP Protocol + SSE]
    end

    subgraph "中间件层"
        G[Redis<br/>缓存 + 短期记忆<br/>langgraph-checkpoint-redis]
        H[RabbitMQ<br/>消息队列<br/>aio-pika 9.4.0]
        I[MinIO<br/>对象存储<br/>MinIO 7.2.16]
    end

    subgraph "数据层"
        J[PostgreSQL<br/>主数据库<br/>psycopg 3.2.12]
        K[PGVector<br/>向量数据库<br/>langchain-postgres]
    end

    subgraph "外部服务"
        L[OpenAI API<br/>langchain-openai 1.0.1]
        M[阿里云通义千问<br/>dashscope 1.24.7]
        N[YouTube API<br/>google-api-python-client 2.146.0]
    end

    subgraph "工具生态"
        O[网页抓取<br/>Playwright 1.48.0]
        P[网络搜索<br/>ddgs 9.8.0]
        Q[文档处理<br/>markitdown 0.1.3]
    end

    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    C --> J
    C --> K
    C --> O
    C --> P
    C --> L
    C --> M
    D --> I
    D --> Q
    E --> H
    F --> N
```

### 数据流架构

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端应用
    participant A as API网关
    participant S as 主服务
    participant R as RAG服务
    participant T as 任务服务
    participant D as 数据库
    participant V as 向量库
    participant MQ as 消息队列

    U->>F: 发送消息
    F->>A: HTTP请求
    A->>S: 路由请求
    S->>D: 查询会话信息
    S->>R: 检索相关文档
    R->>V: 向量搜索(PGVector)
    V-->>R: 返回文档片段
    R-->>S: 返回检索结果
    S->>D: 保存对话记录
    S-->>A: 流式响应(SSE)
    A-->>F: SSE数据流
    F-->>U: 实时显示回复

    Note over T: 每2小时执行记忆同步
    T->>MQ: 投递记忆同步任务
    MQ-->>T: 消费同步任务
    T->>D: 查询用户对话记录
    T->>D: 同步到长期记忆
```

## 📦 项目组件

### 1. suagent-app (前端应用)
**技术栈**: Next.js 16.2.0, TypeScript, Tailwind CSS, Material-UI

- **功能**: 用户界面，包含聊天、智能体管理、文件管理、用户管理等
- **端口**: 11451
- **主要页面**:
  - 登录/注册页面
  - 聊天界面
  - 智能体市场和管理
  - 文件管理
  - 用户设置

### 2. suagent-server (主服务)
**技术栈**: FastAPI 0.120.3, LangChain 1.0.3, LangGraph 1.0.2

- **功能**: 核心API服务，处理用户认证、智能体管理、聊天交互等
- **端口**: 8000
- **主要模块**:
  - 用户认证和权限管理
  - 智能体CRUD操作
  - 聊天流式响应
  - 文件上传和管理
  - MCP客户端集成
  - 记忆系统（短期/长期）

### 3. suagent-rag (RAG服务)
**技术栈**: MinIO, PGVector, PyPDF, MarkItDown

- **功能**: 文档处理和向量检索
- **核心特性**:
  - MinIO文件事件监听
  - 文档自动分块和向量化
  - 混合检索（向量+BM25）
  - 支持多种文档格式（PDF, DOCX, PPTX等）

### 4. suagent-task (任务调度)
**技术栈**: APScheduler, RabbitMQ, SQLAlchemy

- **功能**: 定时任务和消息队列处理
- **核心任务**:
  - 记忆同步任务（每2小时执行）
  - 消息队列处理
  - 定时任务调度
  - 任务失败重试和死信处理

### 5. suagent-youtube-mcp (YouTube MCP服务)
**技术栈**: YouTube API, MCP Protocol, SSE

- **功能**: YouTube数据获取的MCP服务器
- **核心功能**:
  - YouTube视频信息获取
  - 播放列表管理
  - 视频详情查询
  - MCP协议支持

## ✨ 主要功能

### 🤖 智能体管理
- **创建智能体**: 自定义系统提示词、工具选择、MCP配置
- **智能体市场**: 浏览和发现其他用户分享的智能体
- **个性化配置**: 每个智能体可选择不同的工具和功能
- **版本管理**: 支持智能体配置的版本控制

### 💬 聊天交互
- **流式对话**: 实时流畅的对话体验，基于Server-Sent Events
- **多会话管理**: 支持多会话并行，自动生成会话标题
- **历史记录**: 完整的聊天记录保存和查询
- **上下文理解**: 基于对话历史的智能回复

### 🧠 记忆系统
- **短期记忆**: 基于Redis的会话级记忆
- **长期记忆**: 基于PGVector的持久化语义记忆
- **记忆同步**: 定时自动同步用户聊天记录到长期记忆
- **记忆开关**: 用户可控的记忆功能开关

### 📁 文件处理与RAG
- **文件上传**: 支持多种格式文件上传（PDF, DOCX, PPTX, XLSX等）
- **RAG集成**: 自动文件分块、向量化、检索
- **实时监听**: 文件上传/删除的实时RAG处理
- **混合检索**: 向量检索 + BM25算法

### 🔧 工具集成
- **内置工具**: 网页抓取、文件操作、终端执行、网络搜索等
- **MCP协议**: 支持Model Context Protocol，可扩展第三方工具
- **个性化配置**: 按智能体个性化配置可用工具
- **YouTube集成**: 通过MCP服务提供YouTube数据访问

### 👥 用户管理
- **角色权限**: 管理员和普通用户角色分离
- **JWT认证**: 无状态认证，支持刷新机制
- **用户操作**: 注册、登录、密码修改、信息管理
- **管理员功能**: 用户管理、智能体管理、系统配置

## 🚀 快速开始

### 📋 环境要求

| 组件 | 最低版本 | 推荐版本 | 说明 |
|------|----------|----------|------|
| **Python** | 3.10+ | 3.11+ | 后端服务运行环境 |
| **Node.js** | 18+ | 20+ | 前端应用构建和运行 |
| **PostgreSQL** | 15+ | 17+ | 主数据库 |
| **Redis** | 7.0+ | 8.2+ | 缓存和短期记忆 |
| **MinIO** | latest | latest | 对象存储服务 |
| **RabbitMQ** | 3.11+ | 3.12+ | 消息队列 |

### 🐳 一键Docker部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/jeholppx/fenq-super-agent.git
cd fenq-super-agent

# 2. 复制并配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量

# 3. 启动所有服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f

# 6. 验证部署
curl http://localhost:8000/health
```

### 🔧 手动部署

#### 1. 环境准备

```bash
# 创建项目目录
mkdir -p /opt/fenq-super-agent
cd /opt/fenq-super-agent

# 克隆项目
git clone https://github.com/jeholppx/fenq-super-agent.git .
```

#### 2. 数据库初始化

```bash
# 启动 PostgreSQL
docker run -d \
  --name fenq-postgres \
  -e POSTGRES_DB=suagent \
  -e POSTGRES_USER=suagent \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  pgvector/pgvector:pg17

# 启动 Redis
docker run -d \
  --name fenq-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:8-alpine

# 启动 MinIO
docker run -d \
  --name fenq-minio \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin123 \
  -v minio_data:/data \
  minio/minio server /data --console-address ":9001"

# 启动 RabbitMQ
docker run -d \
  --name fenq-rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=suagent \
  -e RABBITMQ_DEFAULT_PASS=your_password \
  -v rabbitmq_data:/var/lib/rabbitmq \
  rabbitmq:3-management
```

#### 3. 后端服务部署

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
cd suagent-server
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 初始化数据库
python check_environment.py

# 启动服务
nohup python start_server.py > ../logs/suagent-server.log 2>&1 &

# 启动其他服务
cd ../suagent-rag
pip install -r requirements.txt
nohup python main.py > ../logs/suagent-rag.log 2>&1 &

cd ../suagent-task
pip install -r requirements.txt
nohup python -m src.task_runner > ../logs/suagent-task.log 2>&1 &

cd ../suagent-youtube-mcp
pip install -r requirements.txt
nohup python mcp_run.py > ../logs/suagent-youtube-mcp.log 2>&1 &
```

#### 4. 前端应用部署

```bash
cd ../suagent-app

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local 文件，配置API地址等

# 开发模式启动
npm run dev

# 生产环境构建和启动
npm run build
npm start

# 使用 PM2 管理进程
pm2 start ecosystem.config.js
```

### 🎯 验证部署

```bash
# 1. 检查服务状态
curl http://localhost:8000/health
curl http://localhost:11451

# 2. 检查各组件
# API文档: http://localhost:8000/docs
# MinIO控制台: http://localhost:9001
# RabbitMQ管理界面: http://localhost:15672

# 3. 运行健康检查脚本
python scripts/health_check.py

# 4. 测试API连接
python scripts/test_api.py
```

### 🌐 生产环境配置

#### Nginx 配置示例

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:11451;
}

server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

#### SSL 证书配置

```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 📊 性能优化

#### 数据库优化

```sql
-- PostgreSQL 性能配置
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
SELECT pg_reload_conf();
```

#### Redis 优化

```bash
# redis.conf 优化配置
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## 📚 API文档

### 认证方式
```http
Authorization: Bearer <JWT_TOKEN>
```

### 主要接口模块

#### 认证模块 (`/api/v1/auth`)
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `POST /logout` - 用户退出
- `POST /change-password` - 修改密码
- `GET /me` - 获取当前用户信息

#### 智能体管理 (`/api/v1/agents`)
- `GET /agents` - 智能体列表
- `POST /agents` - 创建智能体
- `PUT /agents/{agent_id}` - 修改智能体
- `DELETE /agents/{agent_id}` - 删除智能体
- `GET /agents/cards` - 智能体卡片展示

#### 聊天交互 (`/api/v1/chat`)
- `GET /chat` - 智能体对话（流式）
- `GET /sessions` - 会话列表
- `POST /sessions` - 创建会话
- `DELETE /sessions/{session_id}` - 删除会话
- `GET /sessions/{session_id}/messages` - 聊天记录

#### 文件管理 (`/api/v1/files`)
- `POST /files/upload` - 上传文件
- `GET /files` - 文件列表
- `GET /files/chunks` - 文件分块查看
- `DELETE /files` - 删除文件
- `POST /files/batch-delete` - 批量删除文件

#### 记忆管理 (`/api/v1/memory`)
- `GET /memory-setting` - 查询记忆状态
- `POST /memory-setting` - 设置记忆开关
- `POST /memory-sync` - 手动同步记忆

## 🎯 使用场景

### 1. 个人智能助手
创建专属的个人AI助手，集成日历、邮件、文件管理等工具。

### 2. 客服机器人
构建企业的智能客服系统，集成知识库查询、工单管理等业务功能。

### 3. 教育辅导
开发个性化的教育辅导智能体，支持学科问答、学习进度跟踪。

### 4. 内容创作
打造内容创作助手，集成网络搜索、文档分析、YouTube视频处理等工具。

### 5. 技术支持
构建技术支持智能体，集成代码分析、文档查询、问题诊断工具。

## 🛠️ 开发指南

### 技术架构特点

- **微服务架构**: 各服务独立部署，易于扩展
- **异步处理**: FastAPI + asyncio，高并发支持
- **消息队列**: RabbitMQ处理异步任务
- **流式响应**: SSE实现实时对话
- **向量数据库**: PGVector提供高效的语义搜索
- **对象存储**: MinIO处理文件存储

### 开发流程

1. **Fork项目**
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **提交Pull Request**

### 代码规范

- Python代码遵循PEP 8规范
- TypeScript使用ESLint和Prettier
- 添加适当的注释和文档字符串
- 确保所有测试通过

## 🔧 配置说明

### 环境变量配置

各服务的环境变量配置文件：

- `suagent-server/.env` - 主服务配置
- `suagent-app/.env.local` - 前端应用配置
- `suagent-task/.env` - 任务调度配置
- `suagent-youtube-mcp/.env` - MCP服务配置

### 主要配置项

```bash
# 数据库配置
DATABASE_URL="postgresql://username:password@localhost:5432/suagent"

# Redis配置
REDIS_URL="redis://localhost:6379/0"

# MinIO配置
MINIO_ENDPOINT="localhost:9000"
MINIO_ACCESS_KEY="your-access-key"
MINIO_SECRET_KEY="your-secret-key"

# AI模型配置
OPENAI_API_KEY="your-openai-api-key"
DASHSCOPE_API_KEY="your-dashscope-api-key"

# JWT配置
SECRET_KEY="your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## 📊 系统监控

### 健康检查端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 系统总体健康状态 |
| `/health/database` | GET | 数据库连接状态 |
| `/health/redis` | GET | Redis连接状态 |
| `/health/minio` | GET | MinIO连接状态 |
| `/health/mq` | GET | 消息队列状态 |

### 监控指标

```bash
# 系统资源监控
docker stats $(docker ps -q)

# 数据库性能监控
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_stat_database;

# Redis 监控
redis-cli info memory
redis-cli info stats

# 应用性能监控
curl http://localhost:8000/metrics
```

### 日志管理

所有服务都使用loguru进行日志管理：

```bash
# 日志文件结构
logs/
├── suagent-server/          # 主服务日志
│   ├── app.log             # 应用日志
│   ├── error.log           # 错误日志
│   └── access.log          # 访问日志
├── suagent-rag/            # RAG服务日志
├── suagent-task/           # 任务调度日志
└── suagent-youtube-mcp/    # MCP服务日志
```

**日志配置特性：**
- ✅ 支持日志轮转（按大小和时间）
- ✅ 结构化日志格式（JSON）
- ✅ 异步日志写入
- ✅ 错误堆栈追踪
- ✅ 自定义日志级别

### 告警配置

```yaml
# Prometheus + Grafana 告警规则示例
groups:
  - name: fenq-super-agent
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m

      - alert: DatabaseConnectionFailed
        expr: up{job="postgres"} == 0
        for: 1m

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
```

## 🚨 故障排除

### 常见问题及解决方案

#### 1. 服务启动失败

**问题**: 服务无法启动，提示端口被占用
```bash
# 解决方案
sudo netstat -tulpn | grep :8000
sudo kill -9 <PID>
# 或者修改配置文件中的端口号
```

**问题**: 数据库连接失败
```bash
# 检查数据库状态
docker exec -it fenq-postgres psql -U suagent -d suagent -c "SELECT 1;"

# 检查网络连接
telnet localhost 5432

# 重启数据库
docker restart fenq-postgres
```

#### 2. 前端无法访问后端

**问题**: CORS 错误
```bash
# 检查后端 CORS 配置
# 在 suagent-server/src/main.py 中确保正确配置 CORS
origins = ["http://localhost:11451", "https://yourdomain.com"]
```

**问题**: API 请求超时
```bash
# 检查网络延迟
ping localhost

# 增加超时时间
# 在前端配置中增加 timeout 设置
```

#### 3. RAG 功能异常

**问题**: 文档上传失败
```bash
# 检查 MinIO 服务状态
curl http://localhost:9000/minio/health/live

# 检查存储空间
docker exec fenq-minio df -h

# 重新初始化 MinIO
docker exec fenq-minio mc alias set local http://localhost:9000 minioadmin minioadmin123
```

**问题**: 向量搜索无结果
```bash
# 检查 PGVector 扩展
docker exec -it fenq-postgres psql -U suagent -d suagent -c "SELECT * FROM pg_extension;"

# 重建向量索引
docker exec -it fenq-postgres psql -U suagent -d suagent -c "REINDEX INDEX CONCURRENTLY vector_idx;"
```

#### 4. 性能问题

**问题**: 响应时间过长
```bash
# 检查数据库性能
docker exec fenq-postgres psql -U suagent -d suagent -c "
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;"

# 检查 Redis 内存使用
redis-cli info memory | grep used_memory

# 优化数据库查询
# 添加适当的索引
CREATE INDEX CONCURRENTLY idx_session_user_id ON sessions(user_id);
```

### 调试工具

#### 1. 日志分析

```bash
# 实时查看日志
tail -f logs/suagent-server/app.log

# 搜索错误日志
grep -r "ERROR" logs/

# 分析访问模式
awk '{print $1}' logs/suagent-server/access.log | sort | uniq -c | sort -nr
```

#### 2. 性能分析

```bash
# 安装性能分析工具
pip install py-spy

# CPU 性能分析
py-spy top --pid <server-pid>

# 内存分析
py-spy dump --pid <server-pid> > memory-profile.txt
```

#### 3. 网络调试

```bash
# 检查端口连通性
nc -zv localhost 8000

# 抓包分析
sudo tcpdump -i lo port 8000 -w traffic.pcap

# 分析网络延迟
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献类型

- 🐛 **Bug修复**：修复现有功能的问题
- ✨ **新功能开发**：添加新的功能特性
- 📝 **文档改进**：完善文档和注释
- 🎨 **代码重构**：优化代码结构和性能
- 🧪 **测试用例**：增加单元测试和集成测试
- 🔧 **工具改进**：改进开发工具和脚本

### 开发环境设置

```bash
# 1. Fork 并克隆项目
git clone https://github.com/YOUR_USERNAME/fenq-super-agent.git
cd fenq-super-agent

# 2. 添加上游仓库
git remote add upstream https://github.com/jeholppx/fenq-super-agent.git

# 3. 创建开发分支
git checkout -b develop
git pull upstream develop

# 4. 创建功能分支
git checkout -b feature/your-feature-name
```

### 代码规范

#### Python 代码规范

```python
# 使用 Black 格式化代码
black --line-length 88 src/

# 使用 isort 排序导入
isort src/

# 使用 flake8 检查代码质量
flake8 src/

# 使用 mypy 进行类型检查
mypy src/
```

#### TypeScript/JavaScript 代码规范

```bash
# 使用 ESLint 检查代码
npm run lint

# 使用 Prettier 格式化代码
npm run format

# 类型检查
npm run type-check
```

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型说明：**
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**
```
feat(auth): add JWT refresh token support

- Implement automatic token refresh
- Add refresh token endpoint
- Update client-side token management

Closes #123
```

### Pull Request 流程

1. **准备工作**
   ```bash
   # 确保代码是最新的
   git checkout develop
   git pull upstream develop

   # 切换到功能分支
   git checkout feature/your-feature-name
   git pull upstream develop
   ```

2. **代码质量检查**
   ```bash
   # 运行所有测试
   npm test  # 前端测试
   pytest   # 后端测试

   # 代码质量检查
   npm run lint
   flake8 src/
   ```

3. **创建 Pull Request**
   - 使用清晰的标题和描述
   - 链接相关的 Issue
   - 添加必要的截图
   - 确保 CI 检查通过

4. **代码审查**
   - 响应审查意见
   - 及时更新代码
   - 保持友好沟通

### 测试指南

#### 单元测试

```python
# 后端测试示例
import pytest
from src.service.user_service import UserService

def test_create_user():
    user_service = UserService()
    user = user_service.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
```

```typescript
// 前端测试示例
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

test('renders button with correct text', () => {
  render(<Button>Click me</Button>);
  const buttonElement = screen.getByText(/Click me/i);
  expect(buttonElement).toBeInTheDocument();
});
```

#### 集成测试

```bash
# API 集成测试
pytest tests/integration/test_api.py

# 端到端测试
npm run test:e2e
```

### 发布流程

1. **版本准备**
   ```bash
   # 更新版本号
   npm version patch  # 或 minor, major

   # 更新 CHANGELOG.md
   git add CHANGELOG.md
   git commit -m "chore: update changelog"
   ```

2. **创建发布分支**
   ```bash
   git checkout -b release/v2.1.0
   ```

3. **最终检查**
   ```bash
   # 完整测试套件
   npm run test:full

   # 安全扫描
   npm audit
   ```

4. **合并和发布**
   ```bash
   git checkout main
   git merge release/v2.1.0
   git tag v2.1.0
   git push origin main --tags
   ```

## 📄 许可证

本项目采用 Apache 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目的支持：

### 核心框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架，高性能异步API开发
- [Next.js](https://nextjs.org/) - React全栈框架，支持SSR和静态生成
- [LangChain](https://docs.langchain.com/) - AI应用开发框架，简化LLM应用构建
- [LangGraph](https://docs.langchain.com/langgraph) - 工作流编排框架，构建复杂AI代理

### 数据存储
- [PostgreSQL](https://www.postgresql.org/docs/) - 强大的开源对象关系数据库
- [PGVector](https://github.com/pgvector/pgvector) - PostgreSQL向量扩展，支持AI应用
- [Redis](https://redis.io/docs/latest/) - 内存数据结构存储，高性能缓存和消息代理
- [MinIO](https://www.min.io/docs/) - 高性能S3兼容对象存储，支持AI/ML工作负载

### 中间件和工具
- [RabbitMQ](https://www.rabbitmq.com/docs/) - 可靠的消息代理，支持异步处理
- [Material-UI](https://mui.com/material-ui/) - React UI组件库，实现Material Design
- [Tailwind CSS](https://tailwindcss.com/docs) - 实用优先的CSS框架，快速构建现代界面
- [Playwright](https://playwright.dev/) - 现代化浏览器自动化测试工具

### AI和机器学习
- [OpenAI](https://openai.com/) - GPT模型API，强大的语言理解能力
- [阿里云通义千问](https://qianwen.aliyun.com/) - 中文大语言模型，本土化AI支持
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库，Python类型提示和解析

## 📞 联系方式

- **项目维护者**: Jehol FENQ
- **邮箱**: [your-email@example.com]
- **GitHub Issues**: [提交问题](https://github.com/jeholppx/fenq-super-agent/issues)
- **讨论区**: [GitHub Discussions](https://github.com/jeholppx/fenq-super-agent/discussions)

## 🗺️ 发展路线图

### v2.1.0 (计划中)
- [ ] 多租户支持
- [ ] 插件市场
- [ ] 更多MCP服务器
- [ ] 移动端应用

### v2.2.0 (计划中)
- [ ] 图形化工作流编辑器
- [ ] 高级权限管理
- [ ] 性能监控面板
- [ ] 自动化测试覆盖

### v3.0.0 (长期规划)
- [ ] 分布式部署支持
- [ ] 多语言国际化
- [ ] 企业级SSO集成
- [ ] AI模型训练平台

## 📈 项目统计

![GitHub stars](https://img.shields.io/github/stars/jeholppx/fenq-super-agent?style=social)
![GitHub forks](https://img.shields.io/github/forks/jeholppx/fenq-super-agent?style=social)
![GitHub issues](https://img.shields.io/github/issues/jeholppx/fenq-super-agent)
![GitHub pull requests](https://img.shields.io/github/issues-pr/jeholppx/fenq-super-agent)
![GitHub contributors](https://img.shields.io/github/contributors/jeholppx/fenq-super-agent)

## 🔗 相关链接

- [在线演示](https://demo.fenq-super-agent.com)
- [API文档](https://api.fenq-super-agent.com/docs)
- [用户手册](https://docs.fenq-super-agent.com)
- [开发者文档](https://dev.fenq-super-agent.com)
- [更新日志](CHANGELOG.md)

## 💝 赞助支持

如果您觉得这个项目对您有帮助，欢迎通过以下方式支持我们：

- ⭐ 给项目点个Star
- 🐛 报告Bug和提出建议
- 📝 贡献代码和文档
- 💰 [成为赞助者](https://github.com/sponsors/jeholppx)
- 📢 推荐给朋友和同事

---

<div align="center">

## 🌟 感谢您的关注和支持！

**如果这个项目对您有帮助，请给我们一个 ⭐️**

[![Star History Chart](https://api.star-history.com/svg?repos=jeholppx/fenq-super-agent&type=Date)](https://star-history.com/#jeholppx/fenq-super-agent&Date)

Made with ❤️ by Jehol FENQ

**© 2024 Fenq Super Agent. All rights reserved.**

</div>
