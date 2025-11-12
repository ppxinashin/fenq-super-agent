# 数据库使用说明

## 数据表结构

### 1. 用户表 (users)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BigInteger | 主键（雪花ID） |
| username | String(50) | 用户名（唯一） |
| password | String(32) | 密码（MD5加密） |
| salt | String(4) | 盐值 |
| role | Enum | 用户角色（admin/user） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
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

### 3. 会话日志表 (session_logs)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BigInteger | 主键（雪花ID） |
| session_id | BigInteger | 会话ID |
| agent_id | String(100) | 智能体英文名 |
| role | String(20) | 角色 |
| content | Text | 消息内容 |

## 数据库初始化

### 配置数据库连接

在 `.env` 文件中配置：

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=suagent
POSTGRES_PASSWORD=postgres
POSTGRES_DB=super_agent_db
```

### 初始化数据库表

```bash
python -m src.model.init_db
```

## 基本使用方法

### 引入模块

```python
from src.model import get_db_session, crud_user, crud_agent, crud_session_log
```

### 使用会话管理器

```python
with get_db_session() as db:
    # 执行数据库操作
    user = crud_user.get(db, user_id)
```

## 通用CRUD方法

所有CRUD类都提供以下方法：

- `create()` - 创建记录
- `get()` - 根据ID获取记录
- `get_multi()` - 列表查询
- `get_paginated()` - 分页查询
- `update()` - 更新记录
- `delete()` - 软删除
- `hard_delete()` - 物理删除
