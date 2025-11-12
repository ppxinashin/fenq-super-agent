# Session表结构详细说明

## 📊 表结构图

```
┌─────────────────────────────────────────────────────────────┐
│                      sessions (会话表)                       │
├──────────────────┬──────────────┬─────────┬─────────────────┤
│ 字段名           │ 类型         │ 约束    │ 说明            │
├──────────────────┼──────────────┼─────────┼─────────────────┤
│ id               │ BIGINT       │ PK      │ 主键(雪花ID)    │
│ agent_id         │ VARCHAR(100) │ NOT NULL│ 智能体英文名    │
│ session_id       │ BIGINT       │ UNIQUE  │ 会话ID(唯一)    │
│ title            │ VARCHAR(200) │ NULL    │ 会话标题        │
│ created_at       │ TIMESTAMP    │         │ 创建时间        │
│ created_by       │ VARCHAR(100) │         │ 创建人          │
│ updated_at       │ TIMESTAMP    │         │ 更新时间        │
│ updated_by       │ VARCHAR(100) │         │ 更新人          │
│ is_deleted       │ BOOLEAN      │         │ 软删除标记      │
└──────────────────┴──────────────┴─────────┴─────────────────┘
```

## 🔗 表关系图

```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│     agents       │         │    sessions      │         │  session_logs    │
│   (智能体表)     │         │   (会话表)       │         │  (会话日志表)    │
├──────────────────┤         ├──────────────────┤         ├──────────────────┤
│ agent_id (UK)    │◄───────┤ agent_id (FK)    │◄───────┤ session_id (FK)  │
│ agent_name       │    1:N  │ session_id (UK)  │    1:N  │ agent_id (FK)    │
│ description      │         │ title            │         │ role             │
└──────────────────┘         └──────────────────┘         └──────────────────┘
```

**关系说明**:
- `agents` ←→ `sessions`: 一对多（一个智能体可以有多个会话）
- `sessions` ←→ `session_logs`: 一对多（一个会话包含多条消息记录）

## 📋 字段详细说明

### 主键字段

#### id (BIGINT)
- **类型**: BIGINT (19位整数)
- **约束**: PRIMARY KEY
- **默认值**: 使用雪花算法生成
- **说明**: 表的主键，全局唯一ID

### 业务字段

#### agent_id (VARCHAR(100))
- **类型**: VARCHAR(100)
- **约束**: NOT NULL, INDEX
- **说明**: 智能体的英文标识符
- **用途**: 关联agents表，标识会话属于哪个智能体

#### session_id (BIGINT)
- **类型**: BIGINT
- **约束**: UNIQUE, NOT NULL, INDEX
- **默认值**: 使用雪花算法生成
- **说明**: 会话的唯一标识符

#### title (VARCHAR(200))
- **类型**: VARCHAR(200)
- **约束**: NULLABLE
- **默认值**: NULL
- **说明**: 会话的标题/主题
- **用途**: 
  - 初始创建时为NULL
  - 第一轮对话后自动生成或手动设置
  - 用户可随时修改

### 审计字段（继承自Base）

#### created_at (TIMESTAMP)
- **类型**: TIMESTAMP WITHOUT TIME ZONE
- **约束**: INDEX
- **默认值**: CURRENT_TIMESTAMP
- **说明**: 记录创建时间

#### created_by (VARCHAR(100))
- **类型**: VARCHAR(100)
- **默认值**: 'admin'
- **说明**: 记录创建人

#### updated_at (TIMESTAMP)
- **类型**: TIMESTAMP WITHOUT TIME ZONE
- **默认值**: CURRENT_TIMESTAMP
- **更新**: 自动更新（通过触发器）
- **说明**: 记录最后更新时间

#### updated_by (VARCHAR(100))
- **类型**: VARCHAR(100)
- **默认值**: 'admin'
- **说明**: 记录最后更新人

#### is_deleted (BOOLEAN)
- **类型**: BOOLEAN
- **默认值**: FALSE
- **说明**: 软删除标记

## 🔍 索引设计

### 索引列表

| 索引名 | 字段 | 类型 | 用途 |
|--------|------|------|------|
| `PRIMARY KEY` | id | 主键索引 | 快速通过主键查询 |
| `UNIQUE` | session_id | 唯一索引 | 保证会话ID唯一 |
| `idx_session_agent_id` | agent_id | 普通索引 | 查询某智能体的所有会话 |
| `idx_session_session_id` | session_id | 普通索引 | 快速查询指定会话 |
| `idx_session_agent_id_session_id` | agent_id, session_id | 复合索引 | 优化组合查询 |
| `idx_sessions_created_at` | created_at | 普通索引 | 支持时间排序和范围查询 |

## 🔄 触发器

### update_sessions_updated_at

**功能**: 自动更新`updated_at`字段

**触发时机**: BEFORE UPDATE

## 📈 数据库视图

### v_active_sessions (活跃会话视图)

查询所有未删除的会话

### v_session_details (会话详情视图)

查询会话详情，包括智能体名称和消息数量

## 💾 存储估算

### 单行数据大小估算

| 字段 | 平均大小 |
|------|----------|
| id | 8 bytes |
| agent_id | ~20 bytes |
| session_id | 8 bytes |
| title | ~50 bytes |
| created_at | 8 bytes |
| created_by | ~20 bytes |
| updated_at | 8 bytes |
| updated_by | ~20 bytes |
| is_deleted | 1 byte |
| **总计** | **~143 bytes** |

加上PostgreSQL的行开销（~23 bytes），每行约 **166 bytes**

## 🔐 约束和验证

### 主键约束
```sql
PRIMARY KEY (id)
```

### 唯一约束
```sql
UNIQUE (session_id)
```

### 非空约束
```sql
agent_id NOT NULL
session_id NOT NULL
```

## 📝 DDL语句

完整的表创建语句：

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id BIGINT PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    session_id BIGINT UNIQUE NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'admin',
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100) DEFAULT 'admin',
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 创建索引
CREATE INDEX idx_session_agent_id ON sessions(agent_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_session_session_id ON sessions(session_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_session_agent_id_session_id ON sessions(agent_id, session_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
```
