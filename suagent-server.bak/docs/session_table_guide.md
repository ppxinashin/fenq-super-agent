# 会话表(Session)使用指南

## 表结构

### 字段说明

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| `id` | BIGINT | 主键ID（雪花ID） | PRIMARY KEY |
| `agent_id` | VARCHAR(100) | 智能体英文名 | NOT NULL |
| `session_id` | BIGINT | 会话ID | NOT NULL, UNIQUE |
| `title` | VARCHAR(200) | 会话标题 | NULLABLE |
| `created_at` | TIMESTAMP | 创建时间 | 自动 |
| `updated_at` | TIMESTAMP | 更新时间 | 自动 |
| `is_deleted` | BOOLEAN | 软删除标记 | 默认FALSE |

### 索引

- `idx_session_agent_id`: agent_id索引
- `idx_session_session_id`: session_id唯一索引
- `idx_session_agent_id_session_id`: 复合索引
- `idx_sessions_created_at`: 创建时间索引

## 核心功能

### 1. 创建会话

```python
from src.model.database import get_db_session
from src.model.crud_session import crud_session

with get_db_session() as db:
    session = crud_session.create_session(
        db=db,
        agent_id="demo_agent",
        session_id=1000000001,
        title="第一次对话",
        created_by="user123"
    )
```

### 2. 查询会话

#### 根据session_id查询

```python
with get_db_session() as db:
    session = crud_session.get_by_session_id(
        db=db,
        session_id=1000000001
    )
```

#### 查询智能体的所有会话

```python
with get_db_session() as db:
    sessions = crud_session.get_by_agent_id(
        db=db,
        agent_id="demo_agent",
        skip=0,
        limit=10
    )
```

### 3. 更新会话标题

```python
with get_db_session() as db:
    session = crud_session.update_title(
        db=db,
        session_id=1000000001,
        title="关于Python编程的讨论",
        updated_by="user123"
    )
```

### 4. 删除会话（软删除）

```python
with get_db_session() as db:
    success = crud_session.delete_by_session_id(
        db=db,
        session_id=1000000001,
        deleted_by="user123"
    )
```

### 5. 统计会话数量

```python
with get_db_session() as db:
    count = crud_session.count_by_agent_id(
        db=db,
        agent_id="demo_agent"
    )
```

## 数据库初始化

### 方式1：使用Python脚本

```bash
python -m src.model.init_db
```

### 方式2：使用SQL脚本

```bash
psql -U suagent -d super_agent_db -f scripts/init_sessions.sql
```

## 相关模块

- **模型定义**: `src/model/session.py`
- **CRUD操作**: `src/model/crud_session.py`
- **SQL脚本**: `scripts/init_sessions.sql`
