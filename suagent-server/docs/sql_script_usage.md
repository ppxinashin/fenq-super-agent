# PostgreSQL 初始化脚本使用说明

## 脚本文件

- **文件路径**: `scripts/init_database.sql`
- **数据库**: PostgreSQL >= 12
- **字符编码**: UTF-8

## 快速开始

### 方法一：使用psql命令行工具

```bash
# 1. 连接到PostgreSQL服务器
psql -h localhost -U suagent -d postgres

# 2. 创建数据库（如果还没有）
CREATE DATABASE super_agent_db OWNER suagent;

# 3. 退出并连接到新数据库
\q
psql -h localhost -U suagent -d super_agent_db

# 4. 执行初始化脚本
\i scripts/init_database.sql

# 或者直接一条命令执行
psql -h localhost -U suagent -d super_agent_db -f scripts/init_database.sql
```

### 方法二：使用环境变量

```bash
# 设置环境变量
export PGHOST=localhost
export PGPORT=5432
export PGUSER=suagent
export PGPASSWORD=postgres
export PGDATABASE=super_agent_db

# 执行脚本
psql -f scripts/init_database.sql
```

### 方法三：使用Docker

```bash
# 如果使用Docker运行PostgreSQL
docker exec -i postgres_container psql -U suagent -d super_agent_db < scripts/init_database.sql

# 或者复制到容器内执行
docker cp scripts/init_database.sql postgres_container:/tmp/
docker exec -it postgres_container psql -U suagent -d super_agent_db -f /tmp/init_database.sql
```

## 脚本内容说明

### 1. 枚举类型

创建用户角色枚举：
- `admin` - 管理员
- `user` - 普通用户

### 2. 数据表

#### 用户表 (users)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键（雪花ID） |
| username | VARCHAR(50) | 用户名（唯一） |
| password | VARCHAR(32) | MD5加密密码 |
| salt | VARCHAR(4) | 盐值 |
| role | user_role | 用户角色 |
| created_at | TIMESTAMP | 创建时间 |
| created_by | VARCHAR(100) | 创建人 |
| updated_at | TIMESTAMP | 更新时间 |
| updated_by | VARCHAR(100) | 更新人 |
| is_deleted | BOOLEAN | 软删除标记 |

**索引**:
- `idx_users_username` - 用户名索引
- `idx_users_role` - 角色索引
- `idx_users_created_at` - 创建时间索引

#### 智能体表 (agents)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键（雪花ID） |
| agent_id | VARCHAR(100) | 智能体英文名（唯一） |
| agent_name | VARCHAR(100) | 智能体中文名 |
| description | TEXT | 介绍 |
| system_prompt | TEXT | 系统提示词 |
| tools | JSONB | 工具清单 |
| mcp_enabled | BOOLEAN | MCP开关 |
| mcp_servers | JSONB | MCP服务器配置 |
| created_at | TIMESTAMP | 创建时间 |
| created_by | VARCHAR(100) | 创建人 |
| updated_at | TIMESTAMP | 更新时间 |
| updated_by | VARCHAR(100) | 更新人 |
| is_deleted | BOOLEAN | 软删除标记 |

**索引**:
- `idx_agents_agent_id` - 智能体ID索引
- `idx_agents_agent_name` - 智能体名称索引
- `idx_agents_created_at` - 创建时间索引

#### 会话日志表 (session_logs)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键（雪花ID） |
| session_id | BIGINT | 会话ID |
| agent_id | VARCHAR(100) | 智能体英文名 |
| role | VARCHAR(20) | 角色 |
| content | TEXT | 消息内容 |
| created_at | TIMESTAMP | 创建时间 |
| created_by | VARCHAR(100) | 创建人 |
| updated_at | TIMESTAMP | 更新时间 |
| updated_by | VARCHAR(100) | 更新人 |
| is_deleted | BOOLEAN | 软删除标记 |

**索引**:
- `idx_session_logs_session_id` - 会话ID索引
- `idx_session_logs_agent_id` - 智能体ID索引
- `idx_session_logs_session_id_agent_id` - 联合索引
- `idx_session_logs_session_id_created_at` - 会话ID+时间索引

### 3. 触发器

**自动更新时间戳触发器**:
- 每次更新记录时，自动更新 `updated_at` 字段

### 4. 视图

#### v_active_users
活跃用户视图（未删除的用户）

```sql
SELECT * FROM v_active_users;
```

#### v_active_agents
活跃智能体视图

```sql
SELECT * FROM v_active_agents;
```

#### v_session_stats
会话统计视图

```sql
SELECT * FROM v_session_stats;
```

#### v_agent_stats
智能体统计视图（包含会话数、消息数等）

```sql
SELECT * FROM v_agent_stats;
```

### 5. 示例数据

脚本会自动插入以下示例数据：

**用户**:
- 管理员: `admin` / `admin123`
- 普通用户: `demo_user` / `user123`

**智能体**:
- `demo_agent` - 演示智能体

**会话日志**:
- 会话ID: 1000000001
- 2条示例消息

## 自定义配置

### 修改数据库名称

编辑脚本第7-14行：

```sql
CREATE DATABASE your_database_name
    WITH 
    OWNER = your_username
    ENCODING = 'UTF8'
    ...
```

### 禁用示例数据

注释掉脚本中"7. 插入示例数据"部分（第185-240行）：

```sql
-- 注释掉这些INSERT语句
-- INSERT INTO users ...
-- INSERT INTO agents ...
-- INSERT INTO session_logs ...
```

### 修改用户权限

编辑脚本第278-281行：

```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_username;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_username;
```

## 常用查询

### 查看所有表

```sql
\dt

-- 或
SELECT tablename FROM pg_tables WHERE schemaname = 'public';
```

### 查看表结构

```sql
\d users
\d agents
\d session_logs
```

### 查看索引

```sql
\di

-- 或
SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public';
```

### 查看视图

```sql
\dv

-- 或
SELECT viewname FROM pg_views WHERE schemaname = 'public';
```

### 查看统计信息

```sql
-- 查看表记录数
SELECT 
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public';

-- 查看表大小
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 数据验证

### 验证表是否创建成功

```sql
-- 检查表
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'agents', 'session_logs');
-- 应该返回 3

-- 检查枚举类型
SELECT typname FROM pg_type WHERE typname = 'user_role';
-- 应该返回 user_role
```

### 验证示例数据

```sql
-- 检查用户
SELECT username, role FROM users WHERE is_deleted = FALSE;

-- 检查智能体
SELECT agent_id, agent_name FROM agents WHERE is_deleted = FALSE;

-- 检查会话日志
SELECT session_id, agent_id, role FROM session_logs WHERE is_deleted = FALSE;
```

### 验证索引

```sql
-- 检查索引是否创建
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

### 验证触发器

```sql
-- 检查触发器
SELECT 
    trigger_name,
    event_object_table,
    action_timing,
    event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public';
```

## 重置数据库

### 删除所有数据（保留结构）

```sql
-- 清空表数据
TRUNCATE TABLE session_logs CASCADE;
TRUNCATE TABLE agents CASCADE;
TRUNCATE TABLE users CASCADE;

-- 重新插入示例数据
-- 执行脚本中的INSERT语句
```

### 完全重置（删除所有）

```sql
-- 删除所有视图
DROP VIEW IF EXISTS v_agent_stats CASCADE;
DROP VIEW IF EXISTS v_session_stats CASCADE;
DROP VIEW IF EXISTS v_active_agents CASCADE;
DROP VIEW IF EXISTS v_active_users CASCADE;

-- 删除所有表
DROP TABLE IF EXISTS session_logs CASCADE;
DROP TABLE IF EXISTS agents CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 删除枚举类型
DROP TYPE IF EXISTS user_role CASCADE;

-- 删除触发器函数
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- 重新执行初始化脚本
\i scripts/init_database.sql
```

## 备份和恢复

### 备份数据库

```bash
# 备份整个数据库
pg_dump -h localhost -U suagent -d super_agent_db -F c -f backup_$(date +%Y%m%d).dump

# 备份为SQL文件
pg_dump -h localhost -U suagent -d super_agent_db > backup_$(date +%Y%m%d).sql

# 仅备份数据（不含结构）
pg_dump -h localhost -U suagent -d super_agent_db --data-only > data_backup.sql

# 仅备份结构（不含数据）
pg_dump -h localhost -U suagent -d super_agent_db --schema-only > schema_backup.sql
```

### 恢复数据库

```bash
# 从自定义格式恢复
pg_restore -h localhost -U suagent -d super_agent_db -c backup.dump

# 从SQL文件恢复
psql -h localhost -U suagent -d super_agent_db < backup.sql
```

## 故障排查

### 问题1：权限不足

```
ERROR: permission denied for table users
```

**解决方案**:
```sql
-- 授予权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO suagent;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO suagent;
```

### 问题2：枚举类型已存在

```
ERROR: type "user_role" already exists
```

**解决方案**:
脚本已包含检查逻辑，不会重复创建。如需重新创建：
```sql
DROP TYPE user_role CASCADE;
-- 然后重新运行脚本
```

### 问题3：表已存在

```
ERROR: relation "users" already exists
```

**解决方案**:
脚本使用 `CREATE TABLE IF NOT EXISTS`，不会报错。如需重建：
```sql
DROP TABLE users CASCADE;
-- 然后重新运行脚本
```

### 问题4：连接失败

```
psql: could not connect to server
```

**解决方案**:
- 检查PostgreSQL服务是否运行
- 检查连接参数（主机、端口、用户名、密码）
- 检查防火墙设置
- 检查pg_hba.conf配置

## 性能优化建议

### 1. 分析和优化

```sql
-- 分析表统计信息
ANALYZE users;
ANALYZE agents;
ANALYZE session_logs;

-- 查看查询计划
EXPLAIN ANALYZE SELECT * FROM users WHERE username = 'admin';
```

### 2. 维护索引

```sql
-- 重建索引
REINDEX TABLE users;
REINDEX TABLE agents;
REINDEX TABLE session_logs;
```

### 3. 清理和压缩

```sql
-- 清理死元组
VACUUM ANALYZE users;
VACUUM ANALYZE agents;
VACUUM ANALYZE session_logs;

-- 完全清理（需要表锁）
VACUUM FULL users;
```

## 监控和日志

### 查看慢查询

```sql
-- 查看当前正在执行的查询
SELECT pid, age(clock_timestamp(), query_start), usename, query 
FROM pg_stat_activity 
WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%'
ORDER BY query_start DESC;
```

### 查看表访问统计

```sql
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

## 相关文档

- **数据库使用文档**: `docs/database_usage.md`
- **用户角色更新说明**: `docs/user_role_update.md`
- **会话日志更新说明**: `docs/session_log_update.md`
- **数据库功能总结**: `docs/database_summary.md`

## 技术支持

如遇到问题，请检查：
1. PostgreSQL版本是否 >= 12
2. 用户权限是否正确
3. 数据库连接是否正常
4. 日志文件中的错误信息

