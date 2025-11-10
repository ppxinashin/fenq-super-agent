# RAG文件查询使用说明

## 概述

RAG文件查询模块用于查询向量数据库中存储的文件分块信息，支持：
- 查看指定agent_id/user_id下的所有文件
- 查看单个文件的所有分块
- 获取文件摘要信息
- 查询特定分块

## 数据表结构

动态表名格式：`{vector_store_collection}_{agent_id}_{user_id}`

```sql
CREATE TABLE doc_football_admin (
    langchain_id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,
    langchain_metadata JSON
);
```

### Metadata JSON格式

```json
{
    "source": "football/admin/足球知识详细教程文档四：数据解读.md",
    "minio_bucket": "suagent",
    "chunk_index": 0,
    "total_chunks": 5,
    "content_type": "text/markdown",
    "agent_id": "football",
    "user_id": "admin"
}
```

## 查询方法

### 1. 获取文件列表

查询指定agent_id/user_id下的所有文件：

```python
from src.model import rag_file_query, get_db_session

with get_db_session() as db:
    # 获取文件列表
    files = rag_file_query.get_file_list(
        db=db,
        agent_id="football",
        user_id="admin"
    )
    
    for file in files:
        print(f"文件: {file['source']}")
        print(f"总分块数: {file['total_chunks']}")
```

**返回示例**：
```python
[
    {
        "source": "football/admin/足球知识详细教程文档一.md",
        "total_chunks": 3,
        "agent_id": "football",
        "user_id": "admin"
    },
    {
        "source": "football/admin/足球知识详细教程文档二.md",
        "total_chunks": 5,
        "agent_id": "football",
        "user_id": "admin"
    }
]
```

### 2. 获取文件所有分块

根据文件名查询所有分块信息：

```python
with get_db_session() as db:
    # 获取文件的所有分块
    chunks = rag_file_query.get_file_chunks(
        db=db,
        agent_id="football",
        user_id="admin",
        source="football/admin/足球知识详细教程文档四：数据解读.md"
    )
    
    for chunk in chunks:
        print(f"分块 {chunk['chunk_index']}: 长度 {chunk['content_length']}")
        print(f"内容预览: {chunk['content'][:100]}...")
```

**返回示例**：
```python
[
    {
        "langchain_id": "550e8400-e29b-41d4-a716-446655440000",
        "chunk_index": 0,
        "content": "这是第一块内容...",
        "content_length": 1024,
        "metadata": {
            "source": "football/admin/足球知识详细教程文档四：数据解读.md",
            "minio_bucket": "suagent",
            "chunk_index": 0,
            "total_chunks": 5,
            "content_type": "text/markdown",
            "agent_id": "football",
            "user_id": "admin"
        }
    },
    {
        "langchain_id": "550e8400-e29b-41d4-a716-446655440001",
        "chunk_index": 1,
        "content": "这是第二块内容...",
        "content_length": 980,
        "metadata": {...}
    }
]
```

### 3. 获取文件摘要

获取文件的统计信息：

```python
with get_db_session() as db:
    # 获取文件摘要
    summary = rag_file_query.get_file_summary(
        db=db,
        agent_id="football",
        user_id="admin",
        source="football/admin/足球知识详细教程文档四：数据解读.md"
    )
    
    if summary:
        print(f"文件: {summary['source']}")
        print(f"总分块数: {summary['total_chunks']}")
        print(f"总内容长度: {summary['total_content_length']}")
```

**返回示例**：
```python
{
    "source": "football/admin/足球知识详细教程文档四：数据解读.md",
    "total_chunks": 5,
    "total_content_length": 5120,
    "minio_bucket": "suagent",
    "content_type": "text/markdown",
    "agent_id": "football",
    "user_id": "admin"
}
```

### 4. 获取特定分块

根据chunk_index获取单个分块：

```python
with get_db_session() as db:
    # 获取指定分块
    chunk = rag_file_query.get_chunk_by_index(
        db=db,
        agent_id="football",
        user_id="admin",
        source="football/admin/足球知识详细教程文档四：数据解读.md",
        chunk_index=2
    )
    
    if chunk:
        print(f"分块内容: {chunk['content']}")
        print(f"内容长度: {chunk['content_length']}")
```

### 5. 检查表是否存在

在查询前检查表是否存在：

```python
with get_db_session() as db:
    # 检查表是否存在
    exists = rag_file_query.table_exists(
        db=db,
        agent_id="football",
        user_id="admin"
    )
    
    if exists:
        print("表存在，可以查询")
    else:
        print("表不存在，该用户还没有上传文件")
```

## FastAPI接口示例

### 1. 获取文件列表接口

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.model import get_db, rag_file_query
from src.api.response import (
    ApiResponse,
    success_response,
    error_response,
    RAGFileListResponse
)
from src.consts import StatusCode

router = APIRouter()

@router.get("/rag/files", response_model=ApiResponse[list[RAGFileListResponse]])
async def get_rag_files(
    agent_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """获取RAG文件列表"""
    # 检查表是否存在
    if not rag_file_query.table_exists(db, agent_id, user_id):
        return success_response(result=[], message="该用户还没有上传文件")
    
    # 获取文件列表
    files = rag_file_query.get_file_list(db, agent_id, user_id)
    
    # 转换为响应模型
    file_responses = [RAGFileListResponse(**file) for file in files]
    
    return success_response(result=file_responses)
```

### 2. 获取文件分块接口

```python
from src.api.response import RAGFileChunkResponse

@router.get("/rag/files/chunks", response_model=ApiResponse[list[RAGFileChunkResponse]])
async def get_file_chunks(
    agent_id: str,
    user_id: str,
    source: str,
    db: Session = Depends(get_db)
):
    """获取文件的所有分块"""
    # 检查表是否存在
    if not rag_file_query.table_exists(db, agent_id, user_id):
        return error_response("表不存在", code=StatusCode.NOT_FOUND)
    
    # 获取分块
    chunks = rag_file_query.get_file_chunks(db, agent_id, user_id, source)
    
    if not chunks:
        return error_response("文件不存在或没有分块", code=StatusCode.NOT_FOUND)
    
    # 转换为响应模型
    chunk_responses = [RAGFileChunkResponse(**chunk) for chunk in chunks]
    
    return success_response(result=chunk_responses)
```

### 3. 获取文件摘要接口

```python
from src.api.response import RAGFileSummaryResponse

@router.get("/rag/files/summary", response_model=ApiResponse[RAGFileSummaryResponse])
async def get_file_summary(
    agent_id: str,
    user_id: str,
    source: str,
    db: Session = Depends(get_db)
):
    """获取文件摘要"""
    # 获取摘要
    summary = rag_file_query.get_file_summary(db, agent_id, user_id, source)
    
    if not summary:
        return error_response("文件不存在", code=StatusCode.NOT_FOUND)
    
    return success_response(result=RAGFileSummaryResponse(**summary))
```

### 4. 获取特定分块接口

```python
@router.get("/rag/files/chunk", response_model=ApiResponse[RAGFileChunkResponse])
async def get_chunk(
    agent_id: str,
    user_id: str,
    source: str,
    chunk_index: int,
    db: Session = Depends(get_db)
):
    """获取指定分块"""
    # 获取分块
    chunk = rag_file_query.get_chunk_by_index(
        db, agent_id, user_id, source, chunk_index
    )
    
    if not chunk:
        return error_response("分块不存在", code=StatusCode.NOT_FOUND)
    
    return success_response(result=RAGFileChunkResponse(**chunk))
```

## 响应示例

### 文件列表响应

```json
{
    "code": 200,
    "message": "OK",
    "result": [
        {
            "source": "football/admin/足球知识详细教程文档一.md",
            "total_chunks": 3,
            "agent_id": "football",
            "user_id": "admin"
        },
        {
            "source": "football/admin/足球知识详细教程文档二.md",
            "total_chunks": 5,
            "agent_id": "football",
            "user_id": "admin"
        }
    ]
}
```

### 文件分块响应

```json
{
    "code": 200,
    "message": "OK",
    "result": [
        {
            "langchain_id": "550e8400-e29b-41d4-a716-446655440000",
            "chunk_index": 0,
            "content": "这是第一块内容...",
            "content_length": 1024,
            "metadata": {
                "source": "football/admin/足球知识详细教程文档四：数据解读.md",
                "minio_bucket": "suagent",
                "chunk_index": 0,
                "total_chunks": 5,
                "content_type": "text/markdown",
                "agent_id": "football",
                "user_id": "admin"
            }
        }
    ]
}
```

### 文件摘要响应

```json
{
    "code": 200,
    "message": "OK",
    "result": {
        "source": "football/admin/足球知识详细教程文档四：数据解读.md",
        "total_chunks": 5,
        "total_content_length": 5120,
        "minio_bucket": "suagent",
        "content_type": "text/markdown",
        "agent_id": "football",
        "user_id": "admin"
    }
}
```

## 使用场景

### 1. 文件管理界面

展示用户上传的所有文件及其分块情况：

```python
# 获取文件列表
files = rag_file_query.get_file_list(db, agent_id, user_id)

# 为每个文件获取摘要
for file in files:
    summary = rag_file_query.get_file_summary(
        db, agent_id, user_id, file['source']
    )
    print(f"文件: {summary['source']}")
    print(f"分块数: {summary['total_chunks']}")
    print(f"总大小: {summary['total_content_length']} 字符")
```

### 2. 文件预览

点击文件查看详细内容：

```python
# 获取文件的所有分块
chunks = rag_file_query.get_file_chunks(db, agent_id, user_id, source)

# 显示每个分块
for i, chunk in enumerate(chunks):
    print(f"\n--- 分块 {i+1}/{len(chunks)} ---")
    print(f"长度: {chunk['content_length']} 字符")
    print(f"内容: {chunk['content']}")
```

### 3. 分块导航

按chunk_index逐个查看分块：

```python
# 查看第一块
chunk = rag_file_query.get_chunk_by_index(
    db, agent_id, user_id, source, chunk_index=0
)

# 查看下一块
next_chunk = rag_file_query.get_chunk_by_index(
    db, agent_id, user_id, source, chunk_index=1
)
```

## 注意事项

### 1. 表名动态性

表名根据 `agent_id` 和 `user_id` 动态生成，确保参数正确：

```python
# 正确
table_name = f"{settings.vector_store_collection}_football_admin"

# 示例
# vector_store_collection = "doc"
# agent_id = "football"
# user_id = "admin"
# 表名 = "doc_football_admin"
```

### 2. 表存在性检查

查询前建议先检查表是否存在：

```python
if rag_file_query.table_exists(db, agent_id, user_id):
    files = rag_file_query.get_file_list(db, agent_id, user_id)
else:
    print("表不存在")
```

### 3. 错误处理

所有方法都包含异常处理，失败时返回空列表或None：

```python
files = rag_file_query.get_file_list(db, agent_id, user_id)
if not files:
    print("没有文件或查询失败")
```

### 4. JSON字段查询

使用PostgreSQL的JSON操作符查询metadata：

```sql
-- 查询source字段
langchain_metadata->>'source'

-- 查询chunk_index并转换为整数
CAST(langchain_metadata->>'chunk_index' AS INTEGER)
```

### 5. 性能考虑

- 文件列表查询使用GROUP BY，对大量分块会有性能影响
- 建议添加合适的索引：
  ```sql
  CREATE INDEX idx_metadata_source ON table_name ((langchain_metadata->>'source'));
  ```

## 相关文件

- 查询模型: `src/model/rag_file_query.py`
- 响应模型: `src/api/response/rag_file_response.py`
- 配置文件: `src/config/settings.py` (vector_store_collection)

## 扩展功能

可以基于此模块扩展更多功能：

1. **文件搜索**: 根据文件名模糊搜索
2. **内容搜索**: 在分块内容中搜索关键词
3. **统计分析**: 分析文件大小分布、分块数量分布
4. **批量操作**: 批量获取多个文件的摘要信息

