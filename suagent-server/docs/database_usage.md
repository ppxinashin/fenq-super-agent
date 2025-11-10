# 数据库使用说明

本文档介绍如何使用项目中的数据库模型和CRUD操作。

## 目录结构

```
src/model/
├── __init__.py              # 模块导出
├── base.py                  # 基础模型类
├── user.py                  # 用户表模型
├── agent.py                 # 智能体表模型
├── session_log.py           # 会话日志表模型
├── database.py              # 数据库连接和会话管理
├── init_db.py               # 数据库初始化脚本
├── crud_base.py             # CRUD操作基类
├── crud_user.py             # 用户表CRUD操作
├── crud_agent.py            # 智能体表CRUD操作
└── crud_session_log.py      # 会话日志表CRUD操作
```

## 数据表结构

### 1. 用户表 (users)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BigInteger | 主键（雪花ID） |
| username | String(50) | 用户名（唯一） |
| password | String(32) | 密码（MD5加密） |
| salt | String(4) | 盐值（从uuid4中取最后四位） |
| created_at | DateTime | 创建时间 |
| created_by | String(100) | 创建人 |
| updated_at | DateTime | 更新时间 |
| updated_by | String(100) | 更新人 |
| is_deleted | Boolean | 是否删除 |

### 2. 智能体表 (agents)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BigInteger | 主键（雪花ID） |
| agent_id | String(100) | 智能体英文名（唯一） |
| agent_name | String(100) | 智能体中文名 |
| description | Text | 智能体介绍 |
| system_prompt | Text | 系统提示词 |
| tools | JSON | 绑定工具清单 |
| mcp_enabled | Boolean | MCP开关 |
| mcp_servers | JSON | MCP服务器列表 |
| created_at | DateTime | 创建时间 |
| created_by | String(100) | 创建人 |
| updated_at | DateTime | 更新时间 |
| updated_by | String(100) | 更新人 |
| is_deleted | Boolean | 是否删除 |

### 3. 会话日志表 (session_logs)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BigInteger | 主键（雪花ID） |
| session_id | BigInteger | 会话ID |
| role | String(20) | 角色(user/assistant/system) |
| content | Text | 消息内容 |
| created_at | DateTime | 创建时间 |
| created_by | String(100) | 创建人 |
| updated_at | DateTime | 更新时间 |
| updated_by | String(100) | 更新人 |
| is_deleted | Boolean | 是否删除 |

## 数据库初始化

### 1. 配置数据库连接

在 `.env` 文件中配置数据库连接信息：

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=suagent
POSTGRES_PASSWORD=postgres
POSTGRES_DB=super_agent_db
```

### 2. 初始化数据库表

```python
from src.model import init_database

# 初始化数据库（创建所有表）
init_database()
```

或者直接运行初始化脚本：

```bash
python -m src.model.init_db
```

## CRUD操作使用

### 用户表操作

```python
from src.model import crud_user, get_db_session

with get_db_session() as db:
    # 1. 创建用户
    user = crud_user.create_user(
        db=db,
        username="zhangsan",
        plain_password="password123",
        created_by="admin"
    )
    
    # 2. 根据用户名查询
    user = crud_user.get_by_username(db=db, username="zhangsan")
    
    # 3. 用户认证
    user = crud_user.authenticate(
        db=db,
        username="zhangsan",
        plain_password="password123"
    )
    
    # 4. 更新密码
    user = crud_user.update_password(
        db=db,
        user_id=user.id,
        new_password="newpassword456",
        updated_by="admin"
    )
    
    # 5. 分页查询
    result = crud_user.get_paginated(db=db, page=1, page_size=10)
    print(f"总记录数: {result['total']}")
    print(f"用户列表: {result['items']}")
    
    # 6. 列表查询
    users = crud_user.get_multi(db=db, skip=0, limit=10)
    
    # 7. 软删除
    crud_user.delete(db=db, id=user.id, deleted_by="admin")
```

### 智能体表操作

```python
from src.model import crud_agent, get_db_session

with get_db_session() as db:
    # 1. 创建智能体
    agent = crud_agent.create_agent(
        db=db,
        agent_id="test_agent",
        agent_name="测试智能体",
        system_prompt="你是一个测试智能体",
        description="这是一个测试智能体",
        tools=["tool1", "tool2"],
        mcp_enabled=True,
        mcp_servers={
            "amap-maps": {
                "type": "sse",
                "url": "https://mcp.api-inference.modelscope.net/afbe1094621a49/sse"
            }
        },
        created_by="admin"
    )
    
    # 2. 根据agent_id查询
    agent = crud_agent.get_by_agent_id(db=db, agent_id="test_agent")
    
    # 3. 根据名称查询
    agent = crud_agent.get_by_name(db=db, agent_name="测试智能体")
    
    # 4. 模糊搜索
    agents = crud_agent.search_by_name(db=db, keyword="测试")
    
    # 5. 更新工具列表
    agent = crud_agent.update_tools(
        db=db,
        agent_id="test_agent",
        tools=["tool1", "tool2", "tool3"],
        updated_by="admin"
    )
    
    # 6. 更新MCP配置
    agent = crud_agent.update_mcp_config(
        db=db,
        agent_id="test_agent",
        mcp_enabled=False,
        mcp_servers={},
        updated_by="admin"
    )
    
    # 7. 分页查询
    result = crud_agent.get_paginated(db=db, page=1, page_size=10)
    
    # 8. 软删除
    crud_agent.delete(db=db, id=agent.id, deleted_by="admin")
```

### 会话日志表操作

```python
from src.model import crud_session_log, get_db_session

with get_db_session() as db:
    session_id = 123456789  # 会话ID
    
    # 1. 创建会话日志
    log = crud_session_log.create_log(
        db=db,
        session_id=session_id,
        role="user",
        content="你好",
        created_by="system"
    )
    
    # 2. 根据会话ID查询所有日志
    logs = crud_session_log.get_by_session_id(db=db, session_id=session_id)
    
    # 3. 获取最新的N条日志
    logs = crud_session_log.get_latest_by_session_id(
        db=db,
        session_id=session_id,
        limit=10
    )
    
    # 4. 分页查询会话日志
    result = crud_session_log.get_paginated_by_session(
        db=db,
        session_id=session_id,
        page=1,
        page_size=20
    )
    
    # 5. 统计日志数量
    count = crud_session_log.count_by_session_id(db=db, session_id=session_id)
    
    # 6. 删除会话所有日志
    count = crud_session_log.delete_by_session_id(
        db=db,
        session_id=session_id,
        deleted_by="system"
    )
```

## FastAPI集成

在FastAPI中使用数据库依赖注入：

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.model import get_db, crud_user

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = crud_user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.get("/users")
async def list_users(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """分页查询用户列表"""
    result = crud_user.get_paginated(db=db, page=page, page_size=page_size)
    return result
```

## 通用CRUD方法

所有CRUD类都继承自 `CRUDBase`，提供以下通用方法：

### 1. create - 创建记录

```python
obj = crud.create(db=db, obj_in=data_dict, created_by="admin")
```

### 2. get - 根据ID获取记录

```python
obj = crud.get(db=db, id=1)
```

### 3. get_multi - 列表查询

```python
items = crud.get_multi(
    db=db,
    skip=0,          # 跳过记录数
    limit=100,       # 限制返回数量
    order_by="id",   # 排序字段
    order_desc=True  # 是否降序
)
```

### 4. get_paginated - 分页查询

```python
result = crud.get_paginated(
    db=db,
    page=1,          # 页码（从1开始）
    page_size=10,    # 每页记录数
    order_by="id",   # 排序字段
    order_desc=True  # 是否降序
)

# 返回结果包含：
# - items: 数据列表
# - total: 总记录数
# - page: 当前页码
# - page_size: 每页记录数
# - total_pages: 总页数
# - has_prev: 是否有上一页
# - has_next: 是否有下一页
```

### 5. update - 更新记录

```python
obj = crud.update(
    db=db,
    db_obj=obj,
    obj_in=update_dict,
    updated_by="admin"
)
```

### 6. delete - 软删除

```python
success = crud.delete(db=db, id=1, deleted_by="admin")
```

### 7. hard_delete - 物理删除（谨慎使用！）

```python
success = crud.hard_delete(db=db, id=1)
```

## 注意事项

1. **软删除**：默认使用软删除（is_deleted=True），查询时自动过滤已删除记录
2. **雪花ID**：使用雪花算法生成唯一ID，无需手动指定
3. **时间戳**：created_at 和 updated_at 自动维护
4. **事务管理**：使用 `get_db_session()` 上下文管理器自动处理事务和回滚
5. **密码安全**：用户密码使用 MD5(明文密码+盐) 方式加密

## 运行示例

查看完整的使用示例：

```bash
python examples/crud_example.py
```

该示例演示了所有表的CRUD操作。

