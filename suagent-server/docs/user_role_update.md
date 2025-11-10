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

# 两种角色类型
UserRole.ADMIN  # 管理员
UserRole.USER   # 普通用户
```

## 使用示例

### 1. 创建用户时指定角色

```python
from src.model import get_db_session, crud_user, UserRole

with get_db_session() as db:
    # 创建普通用户（默认）
    user = crud_user.create_user(
        db=db,
        username="zhangsan",
        plain_password="password123",
        role=UserRole.USER,  # 可省略，默认为USER
        created_by="admin"
    )
    
    # 创建管理员用户
    admin = crud_user.create_user(
        db=db,
        username="admin",
        plain_password="admin123",
        role=UserRole.ADMIN,  # 指定为管理员
        created_by="system"
    )
```

### 2. 根据角色查询用户

```python
with get_db_session() as db:
    # 查询所有管理员
    admins = crud_user.get_by_role(db=db, role=UserRole.ADMIN)
    
    # 查询所有普通用户
    users = crud_user.get_by_role(db=db, role=UserRole.USER)
```

### 3. 检查用户是否为管理员

```python
with get_db_session() as db:
    # 检查用户是否为管理员
    is_admin = crud_user.is_admin(db=db, user_id=user_id)
    
    if is_admin:
        print("该用户是管理员")
    else:
        print("该用户是普通用户")
```

### 4. 更新用户角色

```python
with get_db_session() as db:
    # 将普通用户提升为管理员
    updated_user = crud_user.update_role(
        db=db,
        user_id=user_id,
        new_role=UserRole.ADMIN,
        updated_by="super_admin"
    )
    
    # 将管理员降级为普通用户
    updated_user = crud_user.update_role(
        db=db,
        user_id=admin_id,
        new_role=UserRole.USER,
        updated_by="super_admin"
    )
```

## 新增CRUD方法

### CRUDUser类新增方法

| 方法名 | 说明 | 参数 | 返回值 |
|--------|------|------|--------|
| `get_by_role()` | 根据角色查询用户 | db, role, limit | List[User] |
| `update_role()` | 更新用户角色 | db, user_id, new_role, updated_by | Optional[User] |
| `is_admin()` | 检查是否为管理员 | db, user_id | bool |

### create_user方法更新

原方法签名：
```python
def create_user(db, username, plain_password, created_by="system")
```

新方法签名：
```python
def create_user(db, username, plain_password, role=UserRole.USER, created_by="system")
```

**向后兼容**：如果不指定role参数，默认创建普通用户。

## FastAPI集成示例

### 1. 权限检查装饰器

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.model import get_db, crud_user

def require_admin(user_id: int, db: Session = Depends(get_db)):
    """要求用户为管理员"""
    if not crud_user.is_admin(db=db, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return True
```

### 2. API路由示例

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.model import get_db, crud_user, UserRole

router = APIRouter()

@router.get("/users/admins")
async def get_admins(db: Session = Depends(get_db)):
    """获取所有管理员用户"""
    admins = crud_user.get_by_role(db=db, role=UserRole.ADMIN)
    return admins

@router.post("/users/{user_id}/promote")
async def promote_to_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)  # 需要管理员权限
):
    """将用户提升为管理员"""
    user = crud_user.update_role(
        db=db,
        user_id=user_id,
        new_role=UserRole.ADMIN,
        updated_by="admin"
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
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

如果数据库中已有用户数据，需要手动添加role字段。建议使用Alembic进行数据库迁移：

```sql
-- 手动SQL迁移（PostgreSQL）
ALTER TABLE users ADD COLUMN role VARCHAR(10) NOT NULL DEFAULT 'user';
CREATE INDEX idx_role ON users(role);
```

## 注意事项

1. **默认角色**：新创建的用户默认为普通用户（UserRole.USER）
2. **角色限制**：只能是 admin 或 user，通过Enum类型强制约束
3. **向后兼容**：现有代码无需修改，不指定role时自动使用默认值
4. **权限控制**：建议在API层实现权限检查逻辑
5. **数据索引**：role字段已添加索引，查询性能优化

## 完整示例

查看完整的角色功能示例：

```bash
# 运行示例脚本
python examples/crud_example.py

# 运行快速演示
python scripts/init_and_demo.py
```

## 相关文件

- `src/model/user.py` - 用户模型定义（包含UserRole枚举）
- `src/model/crud_user.py` - 用户CRUD操作（包含角色相关方法）
- `examples/crud_example.py` - 完整使用示例
- `scripts/init_and_demo.py` - 快速初始化演示

