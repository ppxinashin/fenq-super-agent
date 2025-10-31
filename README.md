# Fenq Super Agent

🤖 基于 LangChain 和 LangGraph 的智能 AI Agent 系统

## ✨ 特性

- 🚀 **基于 LangGraph**：使用 LangGraph 1.x 构建复杂的 Agent 工作流
- 🧠 **智能对话**：支持多轮对话和上下文理解
- 🔧 **工具扩展**：内置多种工具（网页搜索、网页抓取、计算器等）
- 💾 **记忆管理**：基于 Redis 的对话历史持久化
- 📚 **RAG 支持**：使用 PGVector 实现检索增强生成
- 🌐 **REST API**：基于 FastAPI 的现代化 API 服务
- 📖 **代码清晰**：模块化设计，代码可读性强

## 📁 项目结构

```
fenq-super-agent/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── agents/                   # Agent 模块
│   │   ├── __init__.py
│   │   ├── base_agent.py         # 基础 Agent 类
│   │   └── graph_agent.py        # LangGraph Agent 实现
│   ├── api/                      # API 服务模块
│   │   ├── __init__.py
│   │   ├── app.py                # FastAPI 应用
│   │   └── routes/               # API 路由
│   │       ├── __init__.py
│   │       ├── agent.py          # Agent 相关路由
│   │       └── health.py         # 健康检查路由
│   ├── config/                   # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py           # 配置管理
│   ├── memory/                   # 记忆管理模块
│   │   ├── __init__.py
│   │   └── redis_memory.py       # Redis 记忆存储
│   ├── tools/                    # 工具集模块
│   │   ├── __init__.py
│   │   ├── calculator.py         # 计算器工具
│   │   ├── web_scraper.py        # 网页抓取工具
│   │   └── web_search.py         # 网页搜索工具
│   ├── utils/                    # 工具函数模块
│   │   ├── __init__.py
│   │   └── logger.py             # 日志配置
│   └── vectorstore/              # 向量存储模块
│       ├── __init__.py
│       └── pgvector_store.py     # PGVector 实现
├── examples/                     # 示例代码
│   ├── __init__.py
│   ├── simple_chat.py            # 简单对话示例
│   ├── with_memory.py            # 带记忆的对话示例
│   ├── rag_example.py            # RAG 示例
│   └── api_client.py             # API 客户端示例
├── main.py                       # 主入口文件
├── requirements.txt              # 依赖列表
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git 忽略文件
├── LICENSE                       # 许可证
└── README.md                     # 项目文档
```

## 🚀 快速开始

### 1. 环境要求

- Python >= 3.10
- PostgreSQL >= 14（带 PGVector 扩展）
- Redis >= 6.0

### 2. 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd fenq-super-agent

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器（用于网页抓取）
playwright install chromium
```

### 3. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置
nano .env  # 或使用其他编辑器
```

必需的配置项：

```bash
# OpenAI API Key（必需）
OPENAI_API_KEY=your_openai_api_key_here

# PostgreSQL 配置（如果使用 RAG 功能）
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=fenq_agent

# Redis 配置（如果使用记忆功能）
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 4. 启动 PostgreSQL 和 Redis（可选）

如果你的系统上还没有安装这些服务，可以使用 Docker 快速启动：

```bash
# 启动 PostgreSQL with PGVector
docker run -d \
  --name fenq-postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=fenq_agent \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# 启动 Redis
docker run -d \
  --name fenq-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### 5. 运行示例

#### 5.1 简单对话示例

```bash
python examples/simple_chat.py
```

#### 5.2 带记忆的对话

```bash
python examples/with_memory.py
```

#### 5.3 RAG 示例

```bash
python examples/rag_example.py
```

### 6. 启动 API 服务

```bash
# 启动 FastAPI 服务
python main.py

# 服务将在 http://localhost:8000 启动
# API 文档: http://localhost:8000/docs
```

#### 6.1 测试 API

```bash
# 运行 API 客户端示例
python examples/api_client.py

# 或使用 curl
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "session_id": "test_001"}'
```

## 📖 使用指南

### Agent 使用

```python
from src.agents import create_graph_agent
from src.tools import create_web_search_tool, create_calculator_tool

# 创建工具
tools = [
    create_web_search_tool(),
    create_calculator_tool(),
]

# 创建 Agent
agent = create_graph_agent(tools=tools)

# 同步调用
response = agent.invoke("搜索一下最新的 AI 新闻")
print(response)

# 异步调用
import asyncio
response = await agent.ainvoke("计算 123 * 456")
print(response)
```

### 记忆管理

```python
from src.memory import get_redis_memory
from langchain_core.messages import HumanMessage, AIMessage

# 创建记忆实例
memory = get_redis_memory(session_id="user_123")

# 添加消息
memory.add_message(HumanMessage(content="你好"))
memory.add_message(AIMessage(content="你好！有什么可以帮助你的？"))

# 获取历史
history = memory.messages
print(history)

# 清除记忆
memory.clear()
```

### RAG 使用

```python
from src.vectorstore import get_vector_store
from langchain_core.documents import Document

# 创建向量存储
vector_store = get_vector_store(collection_name="my_docs")

# 添加文档
documents = [
    Document(page_content="Python 是一种编程语言", metadata={"source": "doc1"}),
    Document(page_content="LangChain 是一个 AI 框架", metadata={"source": "doc2"}),
]
vector_store.add_documents(documents)

# 相似度搜索
results = vector_store.similarity_search("什么是 LangChain？", k=3)
for doc in results:
    print(doc.page_content)
```

## 🔧 自定义工具

你可以轻松创建自定义工具：

```python
from langchain_core.tools import tool
from src.agents import create_graph_agent

@tool
def my_custom_tool(query: str) -> str:
    """我的自定义工具描述"""
    # 实现你的工具逻辑
    return f"处理结果: {query}"

# 使用自定义工具
agent = create_graph_agent(tools=[my_custom_tool])
response = agent.invoke("使用我的自定义工具")
```

## 📡 API 端点

### 健康检查

```
GET /api/health
GET /api/ping
```

### Agent 对话

```
POST /api/agent/chat
POST /api/agent/chat/stream  # 流式响应
DELETE /api/agent/memory/{session_id}  # 清除记忆
```

详细的 API 文档请访问：http://localhost:8000/docs

## 🛠️ 技术栈

- **核心框架**：LangChain 1.0.3, LangGraph 1.0.2
- **Web 框架**：FastAPI 0.120.3
- **LLM 集成**：langchain-openai 1.0.1, dashscope 1.24.7
- **向量存储**：langchain-postgres 0.0.16, PGVector
- **数据库驱动**：psycopg 3.2.12
- **缓存/记忆**：Redis 7.0.1
- **工具库**：
  - BeautifulSoup4 4.14.2（网页解析）
  - Playwright 1.48.0（浏览器自动化）
  - ddgs 9.6.1（DuckDuckGo 搜索）
  - pypdf 6.1.3（PDF 处理）
- **日志**：loguru 0.7.3
- **配置**：python-dotenv 1.2.1

## 📝 开发建议

### 代码风格

本项目遵循以下原则：

1. **模块化设计**：每个功能模块独立，职责清晰
2. **类型提示**：使用 Python 类型注解提高代码可读性
3. **文档字符串**：每个函数和类都有详细的文档说明
4. **日志记录**：关键操作都有日志记录，便于调试
5. **错误处理**：完善的异常处理机制

### 扩展建议

- **添加新工具**：在 `src/tools/` 目录下创建新的工具模块
- **自定义 Agent**：继承 `BaseAgent` 或 `GraphAgent` 创建自定义 Agent
- **扩展 API**：在 `src/api/routes/` 目录下添加新的路由
- **添加中间件**：在 `src/api/app.py` 中添加 FastAPI 中间件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](LICENSE) 文件。

## 👤 作者

Fenq - 个人作品，不喜勿喷

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI](https://openai.com/)

---

⭐ 如果这个项目对你有帮助，欢迎 Star！
