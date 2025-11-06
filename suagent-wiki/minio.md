# MinIO 事件监听和向量化存储

## 功能说明

本模块实现了 MinIO S3 对象存储的事件监听功能，当有新文件上传到 MinIO 时，自动将文档进行向量化并存储到 PostgreSQL 向量数据库中。

## 核心功能

### MinioEventListener 类

监听 MinIO 的 `s3:ObjectCreated:*` 事件，并自动处理上传的文档：

1. **事件监听**: 实时监听 MinIO 桶中的对象创建事件
2. **文档下载**: 从 MinIO 下载新上传的文件（字节流）
3. **智能分块**: 使用专用的 Chunker 根据文件类型自动选择合适的解析和分块策略
4. **向量化**: 使用 DashScope 的文本嵌入模型进行向量化
5. **存储**: 将向量存储到 PostgreSQL 的 PGVector 数据库中

## 支持的文件类型

通过集成 `src.rag.chunker` 模块，支持以下文件类型：

- **PDF 文档** (`.pdf`) - 使用 `PDFChunker`
  - 支持多页 PDF 文档解析
  - 自动提取文本内容
  
- **Markdown 文档** (`.md`) - 使用 `MarkdownChunker`
  - 保留 Markdown 格式
  - 支持 UTF-8 和 GBK 编码
  
- **Office 文档** - 使用 `OfficeChunker` (基于 markitdown)
  - Word: `.doc`, `.docx`
  - Excel: `.xls`, `.xlsx`
  - PowerPoint: `.ppt`, `.pptx`
  
- **JSON 文档** (`.json`) - 使用 `JSONChunker`
  - 智能 JSON 结构分块
  - 保持数据完整性

- **纯文本** (`.txt`) - 通过通用文本处理

## 配置要求

确保在 `.env` 文件中配置以下环境变量：

```env
# DashScope API Key (用于向量化)
DASHSCOPE_API_KEY=your_dashscope_api_key

# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_BUCKET_NAME=suagent

# PostgreSQL 向量数据库配置
POSTGRES_RAG_HOST=localhost
POSTGRES_RAG_PORT=5432
POSTGRES_RAG_USER=suagent_rag
POSTGRES_RAG_PASSWORD=postgres
POSTGRES_RAG_DB=super_agent_rag_db

# 向量存储配置
VECTOR_STORE_COLLECTION=suagent_documents
```

## 使用方法

### 方式 1: 作为独立程序运行

```bash
cd /home/ubuntu/fenq-super-agent/suagent-server
python -m src.rag.minio.minio_event
```

### 方式 2: 在代码中使用

```python
from src.rag.minio.minio_event import start_event_listener

# 监听所有对象
start_event_listener()

# 或者只监听特定前缀的对象
start_event_listener(prefix='documents/')
```

### 方式 3: 使用类实例

```python
from src.rag.minio.minio_event import MinioEventListener

listener = MinioEventListener()

# 启动监听
listener.listen_events(prefix='')

# 或者手动处理单个文档
listener.process_document('path/to/file.pdf')
```

## 工作流程

```
上传文件到 MinIO
    ↓
触发 s3:ObjectCreated:* 事件
    ↓
MinioEventListener 检测到事件
    ↓
获取文件的 content_type
    ↓
选择合适的 Chunker (PDF/Markdown/Office/JSON)
    ↓
从 MinIO 下载文件（字节流）
    ↓
Chunker 解析并分块文档
    ↓
转换为 LangChain Document 对象
    ↓
使用 DashScope 进行向量化
    ↓
存储到 PostgreSQL 向量数据库
```

## 文档元数据

每个存储的文档块都包含以下元数据：

- `source`: MinIO 中的对象名称（文件路径）
- `minio_bucket`: MinIO 桶名称
- `chunk_index`: 当前块的索引（从 0 开始）
- `total_chunks`: 文档总块数
- `content_type`: 文件的 MIME 类型

## 注意事项

1. **事件通知配置**: MinIO 需要配置事件通知才能触发事件监听。可以通过 MinIO 控制台或 mc 命令行工具配置。

2. **数据库准备**: 确保 PostgreSQL 数据库已安装 PGVector 扩展：
   ```sql
   CREATE EXTENSION vector;
   ```

3. **依赖安装**: 确保安装了所有必要的依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. **Chunker 集成**: 本模块使用项目中已实现的 `src.rag.chunker` 模块进行文档分块，无需额外配置。

5. **文件大小限制**: 对于超大文件，可能需要在各个 Chunker 中调整分割参数。

6. **并发处理**: 当前实现是单线程顺序处理，如果需要高并发，可以考虑使用多进程或异步处理。

## 错误处理与日志

- 使用 `loguru` 进行日志记录，支持控制台和文件输出
- 不支持的文件类型会被跳过并记录警告日志
- 处理失败的文档会记录错误信息（包含堆栈跟踪）但不会中断监听
- 无需临时文件，直接处理字节流，避免文件系统操作

## 查询向量数据库

处理完成后，可以使用 PGVector 进行相似度搜索：

```python
from src.rag.minio.minio_event import MinioEventListener

listener = MinioEventListener()

# 相似度搜索
results = listener.vector_store.similarity_search(
    query="你的搜索问题",
    k=5  # 返回最相似的 5 个结果
)

for doc in results:
    print(f"来源: {doc.metadata['source']}")
    print(f"内容: {doc.page_content[:200]}...")
    print("-" * 50)
```

## 技术栈

- **MinIO**: S3 兼容对象存储，事件驱动架构
- **自定义 Chunker 系统**: 
  - `PDFChunker`: 基于 pypdf
  - `MarkdownChunker`: 支持多编码 Markdown
  - `OfficeChunker`: 基于 markitdown
  - `JSONChunker`: 智能 JSON 分块
- **LangChain**: 向量存储框架和文本分割器
- **DashScope**: 阿里云通义千问的文本嵌入服务
- **PostgreSQL + PGVector**: 向量数据库
- **Loguru**: 日志管理
- **Python 3.13+**: 编程语言

## 架构优势

1. **模块化设计**: Chunker 系统独立于事件监听器，易于扩展
2. **零临时文件**: 直接处理字节流，性能更高，无需清理
3. **智能路由**: 根据文件类型自动选择最佳 Chunker
4. **完整元数据**: 保留文件来源、块索引等信息，便于溯源
5. **可靠日志**: 使用 loguru 记录所有操作，便于调试和监控

