# 用户角色功能更新说明

## 更新内容

为用户表（User）添加了角色字段，支持两种角色类型：**admin**（管理员）和 **user**（普通用户）。

## 数据表变更

### 用户表新增字段

| 字段名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| role | Enum | 用户角色(admin/user) | user |

### 索引变更

新增索引：`idx_role` - 优化角色查询性能

## 角色枚举类

```python
from src.model import UserRole

UserRole.ADMIN  # 管理员
UserRole.USER   # 普通用户
```

## 使用方法

### 1. 创建用户时指定角色

```python
from src.model import get_db_session, crud_user, UserRole

with get_db_session() as db:
    # 创建普通用户（默认）
    user = crud_user.create_user(
        db=db,
        username="zhangsan",
        plain_password="password123",
        role=UserRole.USER
    )
    
    # 创建管理员用户
    admin = crud_user.create_user(
        db=db,
        username="admin",
        plain_password="admin123",
        role=UserRole.ADMIN
    )
```

### 2. 根据角色查询用户

```python
with get_db_session() as db:
    admins = crud_user.get_by_role(db=db, role=UserRole.ADMIN)
    users = crud_user.get_by_role(db=db, role=UserRole.USER)
```

### 3. 检查用户是否为管理员

```python
with get_db_session() as db:
    is_admin = crud_user.is_admin(db=db, user_id=user_id)
```

### 4. 更新用户角色

```python
with get_db_session() as db:
    updated_user = crud_user.update_role(
        db=db,
        user_id=user_id,
        new_role=UserRole.ADMIN,
        updated_by="super_admin"
    )
```

## 新增CRUD方法

| 方法名 | 说明 | 参数 | 返回值 |
|--------|------|------|--------|
| `get_by_role()` | 根据角色查询用户 | db, role, limit | List[User] |
| `update_role()` | 更新用户角色 | db, user_id, new_role, updated_by | Optional[User] |
| `is_admin()` | 检查是否为管理员 | db, user_id | bool |

## 数据库迁移

### 对于新项目

```bash
python -m src.model.init_db
```

### 对于已有数据

```sql
ALTER TABLE users ADD COLUMN role VARCHAR(10) NOT NULL DEFAULT 'user';
CREATE INDEX idx_role ON users(role);
```

## 注意事项

1. **默认角色**：新创建的用户默认为普通用户
2. **角色限制**：只能是 admin 或 user
3. **向后兼容**：不指定role时自动使用默认值
