# 快速启动指南

## 5 分钟快速上手 Fenq Super Agent

### 前置要求

- Python >= 3.10
- pip
- （可选）Docker 和 Docker Compose

### 步骤 1: 克隆项目

```bash
git clone <your-repo-url>
cd fenq-super-agent
```

### 步骤 2: 安装依赖

#### 方法 1: 使用安装脚本（推荐）

```bash
bash scripts/setup.sh
```

#### 方法 2: 手动安装

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 步骤 3: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用其他编辑器
```

**最少需要配置**：

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 步骤 4: 运行第一个示例

```bash
# 激活虚拟环境（如果还没激活）
source venv/bin/activate

# 运行简单对话示例
python examples/simple_chat.py
```

**预期输出**：

```
============================================================
Fenq Super Agent - 简单对话示例
============================================================

👤 用户: 你好，请介绍一下你自己

🤖 Agent: 你好！我是 Fenq Super Agent，一个智能 AI 助手...

------------------------------------------------------------
```

### 步骤 5: 启动 API 服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

**访问 API 文档**：http://localhost:8000/docs

### 步骤 6: 测试 API

#### 使用 curl

```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，世界！",
    "session_id": "test_001",
    "enable_tools": true
  }'
```

#### 使用 Python 客户端

```bash
python examples/api_client.py
```

## 🎯 常用功能速览

### 1. 简单对话

```python
from src.agents import create_graph_agent

agent = create_graph_agent()
response = agent.invoke("你好")
print(response)
```

### 2. 使用工具

```python
from src.agents import create_graph_agent
from src.tools import create_web_search_tool, create_calculator_tool

tools = [create_web_search_tool(), create_calculator_tool()]
agent = create_graph_agent(tools=tools)

response = agent.invoke("搜索最新的 AI 新闻")
print(response)
```

### 3. 带记忆的对话

```python
from src.agents import create_graph_agent
from src.memory import get_redis_memory
from langchain_core.messages import HumanMessage, AIMessage

# 需要先启动 Redis
# docker run -d -p 6379:6379 redis:7-alpine

agent = create_graph_agent()
memory = get_redis_memory("user_123")

# 保存对话
memory.add_message(HumanMessage(content="我叫张三"))
memory.add_message(AIMessage(content="你好，张三！"))

# 构建上下文
history = memory.messages
context = "\n".join([f"{m.type}: {m.content}" for m in history])
response = agent.invoke(f"{context}\n\n当前问题: 我叫什么名字？")
print(response)
```

### 4. RAG 检索

```python
from src.vectorstore import get_vector_store
from langchain_core.documents import Document

# 需要先启动 PostgreSQL with PGVector
# docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres pgvector/pgvector:pg16

vector_store = get_vector_store()

# 添加文档
docs = [
    Document(page_content="Python 是一种编程语言"),
    Document(page_content="LangChain 是 AI 框架"),
]
vector_store.add_documents(docs)

# 搜索
results = vector_store.similarity_search("什么是 LangChain", k=2)
for doc in results:
    print(doc.page_content)
```

## 🐳 使用 Docker（可选）

### 启动依赖服务

```bash
# 启动 PostgreSQL 和 Redis
make docker-up

# 或
docker-compose up -d
```

### 停止服务

```bash
make docker-down

# 或
docker-compose down
```

## 📖 下一步

1. **阅读完整文档**: [README.md](README.md)
2. **了解架构设计**: [ARCHITECTURE.md](ARCHITECTURE.md)
3. **查看项目总结**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
4. **运行更多示例**: 
   - `examples/with_memory.py` - 带记忆的对话
   - `examples/rag_example.py` - RAG 示例
   - `examples/api_client.py` - API 客户端

## 🔧 常见问题

### 1. OpenAI API 错误

```
错误: openai.AuthenticationError
解决: 检查 .env 中的 OPENAI_API_KEY 是否正确
```

### 2. Redis 连接失败

```
错误: redis.exceptions.ConnectionError
解决: 启动 Redis 服务
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. PostgreSQL 连接失败

```
错误: psycopg.OperationalError
解决: 启动 PostgreSQL 服务
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres pgvector/pgvector:pg16
```

### 4. Playwright 浏览器未安装

```
错误: playwright._impl._api_types.Error: Executable doesn't exist
解决: 运行 playwright install chromium
```

## 💡 提示

- 如果只想测试基本对话功能，只需要配置 `OPENAI_API_KEY`
- Redis 和 PostgreSQL 只在使用记忆或 RAG 功能时需要
- 使用 `make help` 查看所有可用的便捷命令
- API 文档会自动生成，访问 `/docs` 查看

## 🎉 完成！

你已经成功启动了 Fenq Super Agent！

接下来可以：
- 探索更多示例代码
- 自定义工具和 Agent
- 集成到你的应用中
- 部署到生产环境

如有问题，请查看 [README.md](README.md) 或提交 Issue。

---

祝使用愉快！⭐

