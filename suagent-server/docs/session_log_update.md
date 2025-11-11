# 会话日志表更新说明

## 更新内容

为会话日志表（SessionLog）添加了智能体英文名字段，并通过验证逻辑确保**一个会话ID只能属于一个智能体**。

## 数据表变更

### 新增字段

| 字段名 | 类型 | 说明 | 必填 |
|--------|------|------|------|
| agent_id | String(100) | 智能体英文名 | 是 |

### 索引变更

新增索引：
- `idx_agent_id` - agent_id单列索引
- `idx_session_id_agent_id` - session_id和agent_id的联合索引

## 核心约束

### 会话ID与智能体绑定

**重要规则**：一旦某个会话ID创建了第一条日志并绑定到某个智能体，后续该会话的所有日志都必须使用相同的智能体ID。

## 使用方法

### 1. 创建会话日志（必须指定agent_id）

```python
from src.model import get_db_session, crud_session_log

with get_db_session() as db:
    log = crud_session_log.create_log(
        db=db,
        session_id=123456789,
        agent_id="my_agent",
        role="user",
        content="你好",
        created_by="system"
    )
```

### 2. 获取会话所属的智能体

```python
with get_db_session() as db:
    agent_id = crud_session_log.get_session_agent(
        db=db,
        session_id=123456789
    )
```

### 3. 根据智能体ID查询日志

```python
with get_db_session() as db:
    logs = crud_session_log.get_by_agent_id(
        db=db,
        agent_id="my_agent",
        limit=100
    )
```

## 新增CRUD方法

| 方法名 | 说明 | 参数变化 |
|--------|------|----------|
| `create_log()` | 创建会话日志 | **新增必填参数**: agent_id |
| `get_session_agent()` | 获取会话所属智能体 | 新增方法 |
| `get_by_agent_id()` | 根据智能体ID查询日志 | 新增方法 |
| `get_by_session_and_agent()` | 根据会话和智能体查询 | 新增方法 |
| `get_sessions_by_agent()` | 获取智能体的所有会话ID | 新增方法 |

## 数据库迁移

### 对于新项目

```bash
python -m src.model.init_db
```

### 对于已有数据

```sql
ALTER TABLE session_logs ADD COLUMN agent_id VARCHAR(100);
UPDATE session_logs SET agent_id = 'default_agent' WHERE agent_id IS NULL;
ALTER TABLE session_logs ALTER COLUMN agent_id SET NOT NULL;
CREATE INDEX idx_agent_id ON session_logs(agent_id);
CREATE INDEX idx_session_id_agent_id ON session_logs(session_id, agent_id);
```

## 注意事项

1. **必填字段**：agent_id 是必填字段
2. **绑定验证**：系统会自动验证会话-智能体绑定关系
3. **异常处理**：调用代码需要捕获 ValueError 异常
