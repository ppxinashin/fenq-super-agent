# RAG文件查询使用说明

## 概述

RAG文件查询模块用于查询向量数据库中存储的文件分块信息。

## 数据表结构

动态表名格式：`{vector_store_collection}_{agent_id}_{user_id}`

### Metadata JSON格式

```json
{
    "source": "football/admin/足球知识详细教程文档四.md",
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

```python
from src.model import rag_file_query, get_db_session

with get_db_session() as db:
    files = rag_file_query.get_file_list(
        db=db,
        agent_id="football",
        user_id="admin"
    )
```

### 2. 获取文件所有分块

```python
with get_db_session() as db:
    chunks = rag_file_query.get_file_chunks(
        db=db,
        agent_id="football",
        user_id="admin",
        source="football/admin/文档.md"
    )
```

### 3. 获取文件摘要

```python
with get_db_session() as db:
    summary = rag_file_query.get_file_summary(
        db=db,
        agent_id="football",
        user_id="admin",
        source="football/admin/文档.md"
    )
```

### 4. 获取特定分块

```python
with get_db_session() as db:
    chunk = rag_file_query.get_chunk_by_index(
        db=db,
        agent_id="football",
        user_id="admin",
        source="football/admin/文档.md",
        chunk_index=2
    )
```

### 5. 检查表是否存在

```python
with get_db_session() as db:
    exists = rag_file_query.table_exists(
        db=db,
        agent_id="football",
        user_id="admin"
    )
```

## 注意事项

### 1. 表名动态性

表名根据 `agent_id` 和 `user_id` 动态生成，确保参数正确。

### 2. 表存在性检查

查询前建议先检查表是否存在。

### 3. 错误处理

所有方法都包含异常处理，失败时返回空列表或None。
