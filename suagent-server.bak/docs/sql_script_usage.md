# PostgreSQL 初始化脚本使用说明

## 快速开始

### 方法一：使用psql命令行工具

```bash
# 连接到数据库并执行脚本
psql -h localhost -U suagent -d super_agent_db -f scripts/init_database.sql
```

### 方法二：使用环境变量

```bash
export PGHOST=localhost
export PGPORT=5432
export PGUSER=suagent
export PGPASSWORD=postgres
export PGDATABASE=super_agent_db

psql -f scripts/init_database.sql
```

### 方法三：使用Docker

```bash
docker exec -i postgres_container psql -U suagent -d super_agent_db < scripts/init_database.sql
```

## 脚本内容说明

### 1. 枚举类型

创建用户角色枚举：
- `admin` - 管理员
- `user` - 普通用户

### 2. 数据表

- **users**: 用户表
- **agents**: 智能体表
- **sessions**: 会话表
- **session_logs**: 会话日志表
- **user_memory_settings**: 用户记忆设置表

### 3. 触发器

自动更新时间戳触发器：每次更新记录时，自动更新 `updated_at` 字段

### 4. 视图

- `v_active_users`: 活跃用户视图
- `v_active_agents`: 活跃智能体视图
- `v_session_stats`: 会话统计视图
- `v_agent_stats`: 智能体统计视图

## 常用查询

### 查看所有表

```sql
\dt
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
```

### 查看视图

```sql
\dv
```

## 数据验证

### 验证表是否创建成功

```sql
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public';
```

### 验证索引

```sql
SELECT tablename, indexname 
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

## 备份和恢复

### 备份数据库

```bash
# 备份整个数据库
pg_dump -h localhost -U suagent -d super_agent_db -F c -f backup_$(date +%Y%m%d).dump

# 备份为SQL文件
pg_dump -h localhost -U suagent -d super_agent_db > backup_$(date +%Y%m%d).sql
```

### 恢复数据库

```bash
# 从自定义格式恢复
pg_restore -h localhost -U suagent -d super_agent_db -c backup.dump

# 从SQL文件恢复
psql -h localhost -U suagent -d super_agent_db < backup.sql
```
