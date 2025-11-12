# Session Log 中间件使用说明

## 概述

SessionMiddleware 是一个用于自动记录对话日志的中间件。它会在智能体与用户交互时，自动将用户消息和AI响应记录到数据库的 `session_logs` 表中。

## 工作原理

中间件通过拦截智能体的消息流来自动记录对话：

1. **用户消息记录**：在 `before_model` 钩子中，当用户消息发送到模型之前，中间件会自动记录用户消息
2. **AI响应记录**：在 `after_model` 钩子中，当模型生成响应之后，中间件会自动记录AI响应

## 实现细节

### 1. 中间件定义

位置：`src/middlewares/session_middleware.py`

```python
class SessionMiddleware(AgentMiddleware[AgentState, BaseContext]):
    """Session日志中间件 - 自动记录用户消息和AI响应"""
    
    def before_model(self, state: AgentState, runtime: Runtime[BaseContext]):
        """记录用户消息"""
        # 从 runtime.context 获取 session_id, agent_id, user_id
        # 记录到数据库
    
    def after_model(self, state: AgentState, runtime: Runtime[BaseContext]):
        """记录AI响应"""
        # 从 runtime.context 获取 session_id, agent_id, user_id
        # 记录到数据库
```

### 2. 上下文扩展

为了支持session_id的传递，我们扩展了 `BaseContext`：

位置：`src/context/base_context.py`

```python
@dataclass
class BaseContext:
    user_id: Optional[str] = None
    chat_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[int] = None  # 新增字段
```

### 3. 使用中间件

在创建 MyAgent 时，将 SessionMiddleware 添加到中间件列表中：

```python
from src.middlewares import get_my_logger_middleware, get_session_middleware
from src.context import BaseContext

# 创建上下文（包含session_id）
context = BaseContext(
    user_id=str(user_id),
    chat_id=public_chat_id,
    agent_id=agent_id,
    session_id=session_id  # 必须提供session_id
)

# 创建智能体，添加session中间件
agent = MyAgent(
    checkpointer=await RedisShortMemory.get_acheckpointer(),
    middlewares=[
        get_my_logger_middleware(),
        get_session_middleware()  # 添加session日志中间件
    ],
    tools=tools,
    system_prompt=system_prompt,
    user_id=str(user_id),
    agent_id=agent_id,
    chat_id=public_chat_id,
    context=context  # 传递context
)
```

## 优势

### 1. 自动化

- 无需在每个API接口中手动调用 `crud_session_log.create_log`
- 减少代码重复，降低维护成本
- 保证日志记录的一致性

### 2. 解耦

- 日志记录逻辑与业务逻辑分离
- 中间件可以轻松启用/禁用
- 便于单元测试

### 3. 独立事务

- 中间件内部使用独立的数据库会话 (`get_db_session()`)
- 日志记录失败不会影响主业务流程
- 异常会被捕获并记录到日志中

## 数据库表结构

记录保存到 `session_logs` 表：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键ID（雪花ID） |
| session_id | BIGINT | 会话ID |
| agent_id | VARCHAR(100) | 智能体英文名 |
| role | VARCHAR(20) | 角色（user/assistant） |
| content | TEXT | 消息内容 |
| created_at | TIMESTAMP | 创建时间 |
| created_by | VARCHAR(100) | 创建人（用户ID） |

## 注意事项

### 1. 必须提供完整的上下文

中间件需要以下信息才能正常工作：
- `session_id`: 会话ID
- `agent_id`: 智能体ID
- `user_id`: 用户ID

如果缺少任何一个，中间件会记录警告并跳过该消息的记录。

### 2. 数据库连接

中间件内部使用 `get_db_session()` 创建独立的数据库会话，这意味着：
- 日志记录操作是独立的事务
- 如果记录失败，不会影响主流程
- 每次记录都会创建和关闭数据库连接

### 3. 异常处理

中间件内部捕获所有异常，确保不会影响主业务流程：
- 记录失败时会在日志中记录错误
- 不会向上抛出异常
- 主业务流程继续执行

## 示例

### 完整示例：在 agent_controller 中使用

```python
from src.middlewares import get_my_logger_middleware, get_session_middleware
from src.context import BaseContext

@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. 获取用户ID
    user_id = current_user.id
    
    # 2. 解析会话ID
    session_id, public_chat_id = _resolve_session_identity(
        agent_id=request.agent_id,
        incoming_chat_id=request.chat_id,
        db=db
    )
    
    # 3. 创建上下文
    context = BaseContext(
        user_id=str(user_id),
        chat_id=public_chat_id,
        agent_id=request.agent_id,
        session_id=session_id  # 关键：传递session_id
    )
    
    # 4. 创建智能体（包含session中间件）
    agent = MyAgent(
        checkpointer=await RedisShortMemory.get_acheckpointer(),
        middlewares=[
            get_my_logger_middleware(),
            get_session_middleware()  # 添加session日志中间件
        ],
        tools=tools,
        system_prompt=agent_db.system_prompt,
        user_id=str(user_id),
        agent_id=request.agent_id,
        chat_id=public_chat_id,
        context=context  # 传递context
    )
    
    # 5. 调用智能体（中间件自动记录对话）
    async for chunk in agent.astream({"messages": [HumanMessage(content=message)]}):
        yield chunk
```

## 对比：使用中间件 vs 手动记录

### 使用中间件（推荐）

```python
# 只需在创建Agent时添加中间件
agent = MyAgent(
    middlewares=[get_session_middleware()],
    context=context  # 传递包含session_id的context
)

# 调用Agent，中间件自动记录
result = await agent.ainvoke({"messages": [HumanMessage(content="你好")]})
```

### 手动记录（旧方式）

```python
# 调用前手动记录用户消息
crud_session_log.create_log(
    db=db,
    session_id=session_id,
    agent_id=agent_id,
    role="user",
    content="你好",
    created_by=str(user_id)
)

# 调用Agent
result = await agent.ainvoke({"messages": [HumanMessage(content="你好")]})

# 调用后手动记录AI响应
crud_session_log.create_log(
    db=db,
    session_id=session_id,
    agent_id=agent_id,
    role="assistant",
    content=result["output"],
    created_by=str(user_id)
)
```

可以看到，使用中间件大大简化了代码，提高了可维护性。

## 排查问题

### 日志没有记录？

检查以下几点：

1. **确认context中包含session_id**
   ```python
   logger.info(f"Context: session_id={context.session_id}")
   ```

2. **检查中间件是否已添加**
   ```python
   agent = MyAgent(
       middlewares=[get_session_middleware()],  # 确认这一行存在
       context=context
   )
   ```

3. **查看应用日志**
   ```bash
   # 查找中间件的日志输出
   grep "用户消息已记录" app.log
   grep "AI响应已记录" app.log
   grep "记录.*失败" app.log
   ```

4. **检查数据库连接**
   ```python
   # 确认数据库连接正常
   with get_db_session() as db:
       count = db.query(SessionLog).count()
       logger.info(f"Total logs: {count}")
   ```

## 总结

SessionMiddleware 提供了一种优雅的方式来自动记录对话日志，通过将日志记录逻辑从业务代码中分离出来，提高了代码的可维护性和可测试性。只需在创建 Agent 时添加中间件并传递包含 session_id 的 context，即可实现自动记录。

