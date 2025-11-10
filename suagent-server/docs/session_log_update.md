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

```python
# ✅ 正确：同一会话使用同一智能体
crud_session_log.create_log(db, session_id=100, agent_id="agent_a", role="user", content="消息1")
crud_session_log.create_log(db, session_id=100, agent_id="agent_a", role="assistant", content="回复1")

# ❌ 错误：尝试在同一会话使用不同智能体（会抛出ValueError）
crud_session_log.create_log(db, session_id=100, agent_id="agent_b", role="user", content="消息2")
# 抛出: ValueError: 会话ID 100 已绑定到智能体 agent_a，不能使用智能体 agent_b 创建日志
```

## 使用示例

### 1. 创建会话日志（必须指定agent_id）

```python
from src.model import get_db_session, crud_session_log

with get_db_session() as db:
    # 创建会话日志（第一条日志绑定会话到智能体）
    log = crud_session_log.create_log(
        db=db,
        session_id=123456789,
        agent_id="my_agent",  # 必填参数
        role="user",
        content="你好",
        created_by="system"
    )
    
    # 后续日志必须使用相同的agent_id
    log2 = crud_session_log.create_log(
        db=db,
        session_id=123456789,
        agent_id="my_agent",  # 必须与第一条日志相同
        role="assistant",
        content="你好！有什么可以帮您？",
        created_by="system"
    )
```

### 2. 获取会话所属的智能体

```python
with get_db_session() as db:
    # 获取会话绑定的智能体ID
    agent_id = crud_session_log.get_session_agent(
        db=db,
        session_id=123456789
    )
    print(f"会话绑定到智能体: {agent_id}")
```

### 3. 根据智能体ID查询日志

```python
with get_db_session() as db:
    # 查询某个智能体的所有日志
    logs = crud_session_log.get_by_agent_id(
        db=db,
        agent_id="my_agent",
        limit=100
    )
    print(f"智能体共有 {len(logs)} 条日志")
```

### 4. 根据会话ID和智能体ID查询

```python
with get_db_session() as db:
    # 查询特定会话和智能体的日志
    logs = crud_session_log.get_by_session_and_agent(
        db=db,
        session_id=123456789,
        agent_id="my_agent"
    )
    print(f"查询到 {len(logs)} 条日志")
```

### 5. 获取智能体的所有会话列表

```python
with get_db_session() as db:
    # 获取智能体的所有会话ID（去重）
    session_ids = crud_session_log.get_sessions_by_agent(
        db=db,
        agent_id="my_agent",
        limit=100
    )
    print(f"智能体的会话列表: {session_ids}")
```

## 新增CRUD方法

### CRUDSessionLog类新增/更新方法

| 方法名 | 说明 | 参数变化 |
|--------|------|----------|
| `create_log()` | 创建会话日志 | **新增必填参数**: agent_id |
| `get_session_agent()` | 获取会话所属智能体 | 新增方法 |
| `get_by_agent_id()` | 根据智能体ID查询日志 | 新增方法 |
| `get_by_session_and_agent()` | 根据会话和智能体查询 | 新增方法 |
| `get_sessions_by_agent()` | 获取智能体的所有会话ID | 新增方法 |

### create_log方法更新

**原方法签名：**
```python
def create_log(db, session_id, role, content, created_by="system")
```

**新方法签名：**
```python
def create_log(db, session_id, agent_id, role, content, created_by="system")
```

**⚠️ 非向后兼容**：必须提供agent_id参数！

## 异常处理

### ValueError: 会话已绑定到其他智能体

当尝试为已存在的会话使用不同的智能体ID创建日志时，会抛出`ValueError`异常。

```python
try:
    crud_session_log.create_log(
        db=db,
        session_id=existing_session_id,
        agent_id="different_agent",
        role="user",
        content="消息"
    )
except ValueError as e:
    print(f"错误：{e}")
    # 可以先查询会话所属的智能体
    correct_agent = crud_session_log.get_session_agent(db, existing_session_id)
    print(f"应该使用智能体: {correct_agent}")
```

## FastAPI集成示例

### 1. 创建会话日志的API

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.model import get_db, crud_session_log

router = APIRouter()

class CreateLogRequest(BaseModel):
    session_id: int
    agent_id: str
    role: str
    content: str

@router.post("/session-logs")
async def create_session_log(
    request: CreateLogRequest,
    db: Session = Depends(get_db)
):
    """创建会话日志"""
    try:
        log = crud_session_log.create_log(
            db=db,
            session_id=request.session_id,
            agent_id=request.agent_id,
            role=request.role,
            content=request.content,
            created_by="api"
        )
        return log
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 2. 查询智能体会话列表的API

```python
@router.get("/agents/{agent_id}/sessions")
async def get_agent_sessions(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """获取智能体的所有会话"""
    session_ids = crud_session_log.get_sessions_by_agent(
        db=db,
        agent_id=agent_id
    )
    return {
        "agent_id": agent_id,
        "session_count": len(session_ids),
        "session_ids": session_ids
    }
```

### 3. 验证会话归属的中间件

```python
from fastapi import Request

async def validate_session_agent(
    request: Request,
    session_id: int,
    agent_id: str,
    db: Session = Depends(get_db)
):
    """验证会话是否属于指定智能体"""
    existing_agent = crud_session_log.get_session_agent(db, session_id)
    
    if existing_agent and existing_agent != agent_id:
        raise HTTPException(
            status_code=403,
            detail=f"会话 {session_id} 属于智能体 {existing_agent}，无权访问"
        )
    
    return True
```

## 数据库迁移

### 对于新项目

直接运行初始化脚本即可：

```bash
python -m src.model.init_db
# 或
python scripts/init_and_demo.py
```

### 对于已有数据

如果数据库中已有会话日志数据，需要手动添加agent_id字段并设置默认值：

```sql
-- 手动SQL迁移（PostgreSQL）
ALTER TABLE session_logs ADD COLUMN agent_id VARCHAR(100);

-- 为现有数据设置默认agent_id（根据实际情况调整）
UPDATE session_logs SET agent_id = 'default_agent' WHERE agent_id IS NULL;

-- 设置为NOT NULL
ALTER TABLE session_logs ALTER COLUMN agent_id SET NOT NULL;

-- 添加索引
CREATE INDEX idx_agent_id ON session_logs(agent_id);
CREATE INDEX idx_session_id_agent_id ON session_logs(session_id, agent_id);
```

## 应用场景

### 1. 多智能体系统

在多智能体系统中，确保每个会话只与一个智能体交互：

```python
# 用户开始与agent_a对话
log1 = crud_session_log.create_log(db, session_id=1, agent_id="agent_a", role="user", content="问题")
log2 = crud_session_log.create_log(db, session_id=1, agent_id="agent_a", role="assistant", content="回答")

# 用户开始新会话与agent_b对话
log3 = crud_session_log.create_log(db, session_id=2, agent_id="agent_b", role="user", content="问题")
```

### 2. 会话统计和分析

按智能体统计会话数量和活跃度：

```python
with get_db_session() as db:
    # 获取各智能体的会话数量
    agents = ["agent_a", "agent_b", "agent_c"]
    
    for agent_id in agents:
        session_ids = crud_session_log.get_sessions_by_agent(db, agent_id)
        log_count = len(crud_session_log.get_by_agent_id(db, agent_id))
        
        print(f"智能体 {agent_id}:")
        print(f"  - 会话数: {len(session_ids)}")
        print(f"  - 消息数: {log_count}")
```

### 3. 会话上下文管理

在中间件中使用会话-智能体绑定进行上下文管理：

```python
class SessionMiddleware:
    def process(self, session_id: int, message: str):
        with get_db_session() as db:
            # 获取会话绑定的智能体
            agent_id = crud_session_log.get_session_agent(db, session_id)
            
            if agent_id:
                # 使用已绑定的智能体继续对话
                return self.route_to_agent(agent_id, message)
            else:
                # 新会话，选择合适的智能体
                agent_id = self.select_agent(message)
                return self.route_to_agent(agent_id, message)
```

## 注意事项

1. **必填字段**：agent_id 是必填字段，创建日志时必须指定
2. **绑定验证**：系统会自动验证会话-智能体绑定关系，无法绕过
3. **异常处理**：调用代码需要捕获 ValueError 异常
4. **数据一致性**：确保会话ID和智能体ID都是有效的
5. **性能优化**：agent_id字段已添加索引，查询性能良好

## 测试验证

运行示例脚本测试完整功能：

```bash
# 完整示例（包含会话绑定验证）
python examples/crud_example.py

# 快速初始化和演示
python scripts/init_and_demo.py
```

示例代码中包含了会话绑定验证的测试，会尝试用不同的agent_id访问同一会话，验证是否正确抛出异常。

## 相关文件

- `src/model/session_log.py` - 会话日志模型定义（添加agent_id字段）
- `src/model/crud_session_log.py` - 会话日志CRUD操作（添加验证和新方法）
- `examples/crud_example.py` - 完整使用示例
- `scripts/init_and_demo.py` - 快速初始化演示

