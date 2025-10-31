# 架构设计文档

## 项目概述

Fenq Super Agent 是一个基于 LangChain 和 LangGraph 的智能 AI Agent 系统，采用模块化设计，支持工具扩展、记忆管理和 RAG 功能。

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                     前端 / API 客户端                    │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                   FastAPI 服务层                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  健康检查路由  │  Agent 路由  │  其他路由...     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Agent 核心层                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │           LangGraph 状态图引擎                    │  │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────┐  │  │
│  │  │  Agent节点 │→ │  Tool节点   │→ │ 判断节点 │  │  │
│  │  └────────────┘  └─────────────┘  └──────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────┬──────────────────┬──────────────────┬────────────┘
      │                  │                  │
      ▼                  ▼                  ▼
┌───────────┐   ┌──────────────┐   ┌─────────────┐
│  工具层    │   │   记忆层      │   │   RAG层     │
├───────────┤   ├──────────────┤   ├─────────────┤
│ • 网页搜索 │   │ Redis 存储   │   │  PGVector   │
│ • 网页抓取 │   │ 会话管理     │   │  向量检索   │
│ • 计算器   │   │ 上下文保持   │   │  文档存储   │
│ • 自定义... │   └──────────────┘   └─────────────┘
└───────────┘
      │
      ▼
┌─────────────────────────────────┐
│        LLM Provider             │
│  OpenAI / 通义千问 / 其他...     │
└─────────────────────────────────┘
```

## 核心模块

### 1. Agent 模块 (`src/agents/`)

**职责**：实现 AI Agent 的核心逻辑

**组件**：
- `BaseAgent`: 基础 Agent 类，提供通用功能
- `GraphAgent`: 基于 LangGraph 的高级 Agent 实现

**工作流程**：
1. 接收用户输入
2. 构建 LangGraph 状态图
3. 执行 Agent 节点（调用 LLM）
4. 判断是否需要调用工具
5. 执行工具节点
6. 返回最终结果

**关键特性**：
- 支持同步/异步/流式调用
- 灵活的工具绑定机制
- 可自定义系统提示词

### 2. 工具模块 (`src/tools/`)

**职责**：为 Agent 提供各种能力

**内置工具**：
- `web_search`: DuckDuckGo 网页搜索
- `web_scraper`: Playwright 网页抓取
- `calculator`: 安全的数学表达式计算

**扩展方式**：
```python
from langchain_core.tools import tool

@tool
def custom_tool(input: str) -> str:
    """工具描述"""
    # 实现逻辑
    return result
```

### 3. 记忆模块 (`src/memory/`)

**职责**：管理对话历史和上下文

**实现方式**：
- 使用 Redis 作为持久化存储
- 实现 LangChain 的 `BaseChatMessageHistory` 接口
- 支持会话隔离和过期机制

**数据结构**：
```
Redis Key: chat_history:{session_id}
Value: List of JSON-serialized messages
TTL: 7 days (可配置)
```

### 4. 向量存储模块 (`src/vectorstore/`)

**职责**：实现 RAG（检索增强生成）功能

**技术栈**：
- PostgreSQL + PGVector 扩展
- OpenAI Embeddings (text-embedding-3-small)

**核心功能**：
- 文档向量化存储
- 相似度检索
- 元数据过滤
- 与 Agent 集成

### 5. API 模块 (`src/api/`)

**职责**：提供 RESTful API 服务

**端点**：
- `POST /api/agent/chat` - 标准聊天
- `POST /api/agent/chat/stream` - 流式聊天
- `DELETE /api/agent/memory/{session_id}` - 清除记忆
- `GET /api/health` - 健康检查

**特性**：
- 基于 FastAPI
- 支持 CORS
- 自动生成 OpenAPI 文档
- 异步处理

### 6. 配置模块 (`src/config/`)

**职责**：统一管理应用配置

**实现方式**：
- 使用 Pydantic Settings
- 支持环境变量
- 类型安全
- 默认值和验证

**配置分类**：
- 应用基础配置
- LLM 配置
- 数据库配置
- 工具配置

## 数据流

### 1. 简单对话流程

```
用户输入 → FastAPI → GraphAgent → LLM → 返回结果
```

### 2. 带工具调用流程

```
用户输入 → FastAPI → GraphAgent
                         ↓
                    Agent 节点 (LLM)
                         ↓
                    判断：需要工具？
                         ↓ Yes
                    Tool 节点 (执行工具)
                         ↓
                    返回工具结果 → Agent 节点 → 最终回答
```

### 3. 带记忆的对话流程

```
用户输入 → FastAPI → 加载历史记忆 (Redis)
                         ↓
                    构建完整上下文
                         ↓
                    GraphAgent → LLM → 结果
                         ↓
                    保存到记忆 (Redis) → 返回
```

### 4. RAG 查询流程

```
用户查询 → FastAPI → GraphAgent
                         ↓
                    Agent 节点决定调用 RAG 工具
                         ↓
                    向量检索 (PGVector)
                         ↓
                    返回相关文档
                         ↓
                    Agent 基于文档生成回答 → 返回
```

## 设计原则

### 1. 模块化
- 每个模块职责单一
- 模块间松耦合
- 易于扩展和替换

### 2. 可配置
- 所有配置通过环境变量
- 支持多环境部署
- 默认值合理

### 3. 可观测
- 完善的日志记录
- 关键操作追踪
- 错误详细记录

### 4. 可扩展
- 工具系统可插拔
- Agent 可自定义
- 支持自定义 LLM Provider

### 5. 类型安全
- 使用 Python 类型提示
- Pydantic 数据验证
- 减少运行时错误

## 性能优化

### 1. 异步处理
- FastAPI 全异步
- LangGraph 支持异步
- 减少阻塞等待

### 2. 连接池
- Redis 连接池
- PostgreSQL 连接池
- 复用连接减少开销

### 3. 缓存策略
- 向量查询结果缓存
- LLM 响应缓存（可选）
- 减少重复计算

### 4. 流式响应
- 支持 SSE 流式输出
- 提升用户体验
- 减少首字节时间

## 安全考虑

### 1. 输入验证
- Pydantic 模型验证
- 防止注入攻击
- 限制输入长度

### 2. 错误处理
- 优雅的错误捕获
- 不泄露敏感信息
- 详细的错误日志

### 3. 认证授权
- 可扩展的认证机制
- API Key 管理
- 会话隔离

### 4. 安全的工具执行
- 沙箱环境（计算器）
- 限制网络访问
- 超时保护

## 部署方案

### 1. 开发环境
```bash
# 本地运行所有服务
docker-compose up -d
python main.py
```

### 2. 生产环境
- 使用 Gunicorn + Uvicorn workers
- Nginx 反向代理
- 独立的 PostgreSQL 和 Redis 集群
- 环境变量配置管理

### 3. 容器化部署
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 监控和日志

### 1. 日志系统
- Loguru 统一日志
- 分级日志（INFO, ERROR）
- 日志轮转和压缩
- 结构化日志格式

### 2. 指标监控
- API 响应时间
- Agent 调用次数
- 工具使用统计
- 错误率监控

### 3. 健康检查
- `/api/health` 端点
- 依赖服务状态检查
- 自动恢复机制

## 未来扩展

### 1. 多模态支持
- 图像理解（GPT-4V）
- 语音输入输出
- 文档解析增强

### 2. Agent 协作
- 多 Agent 系统
- Agent 间通信
- 任务分配和协调

### 3. 高级 RAG
- 混合检索策略
- 重排序机制
- 多文档推理

### 4. 自主学习
- 用户反馈收集
- 模型微调
- 持续优化

## 参考资源

- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [PGVector 文档](https://github.com/pgvector/pgvector)

