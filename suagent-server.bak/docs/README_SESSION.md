# 会话表(Session)功能说明

## ✨ 已完成的功能

### 📊 数据模型

会话表（`sessions`）已完整实现，用于统计智能体下的会话信息。

**核心字段：**
- `agent_id` - 智能体英文名
- `session_id` - 唯一会话ID
- `title` - 会话标题
- 继承自Base的字段：`id`, `created_at`, `created_by`, `updated_at`, `updated_by`, `is_deleted`

### 🔧 CRUD操作

`src/model/crud_session.py` 提供了完整的增删改查功能：

| 功能 | 方法 | 说明 |
|------|------|------|
| ✅ **增** | `create_session()` | 创建新会话 |
| ✅ **删** | `delete_by_session_id()` | 软删除会话 |
| ✅ **改** | `update_title()` | 更新会话标题 |
| ✅ **查** | `get_by_session_id()` | 根据session_id查询 |
| ✅ **查** | `get_by_agent_id()` | 查询智能体的所有会话 |
| ✅ **查** | `search_by_title()` | 按标题模糊搜索 |
| ✅ **查** | `count_by_agent_id()` | 统计会话数量 |

## 🚀 快速开始

### 1. 初始化数据库

```bash
python -m src.model.init_db
```

### 2. 基本使用

```python
from src.model.database import get_db_session
from src.model.crud_session import crud_session

# 创建会话
with get_db_session() as db:
    session = crud_session.create_session(
        db=db,
        agent_id="demo_agent",
        session_id=1000000001,
        title="我的第一个会话",
        created_by="user123"
    )

# 查询会话
with get_db_session() as db:
    session = crud_session.get_by_session_id(db=db, session_id=1000000001)

# 更新标题
with get_db_session() as db:
    crud_session.update_title(
        db=db,
        session_id=1000000001,
        title="新标题",
        updated_by="user123"
    )
```

## 📂 相关文件

### 模型与CRUD
- `src/model/base.py` - Base模型定义
- `src/model/session.py` - Session模型定义
- `src/model/crud_session.py` - Session的CRUD操作

### SQL脚本
- `scripts/init_database.sql` - 完整数据库初始化脚本
- `scripts/init_sessions.sql` - 会话表初始化脚本

### 文档
- `docs/session_table_guide.md` - 详细使用指南

## 💡 使用场景

### 场景1: 用户开始新对话
创建新会话，初始标题为空

### 场景2: 第一轮对话后设置标题
根据对话内容自动生成或手动设置标题

### 场景3: 继续已有会话
根据session_id获取会话信息，继续对话

### 场景4: 用户修改标题
允许用户随时重命名会话标题

### 场景5: 查看历史会话
按智能体查询所有会话列表

### 场景6: 搜索会话
按标题关键词模糊搜索

### 场景7: 删除会话
软删除会话（数据仍保留，可恢复）

## 📊 数据库视图

### v_active_sessions
查看所有活跃会话（未删除）

```sql
SELECT * FROM v_active_sessions;
```

### v_session_details
查看会话详情（包含智能体信息和消息数量）

```sql
SELECT * FROM v_session_details WHERE agent_id = 'demo_agent';
```

## 🎯 特性总结

✅ 完整的模型定义  
✅ 丰富的CRUD操作  
✅ SQL初始化脚本  
✅ 索引优化  
✅ 软删除机制  
✅ 数据库视图  
✅ 触发器自动更新时间戳
