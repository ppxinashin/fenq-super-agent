# 删除逻辑说明文档

## 概述

项目中所有的删除操作都使用**软删除**机制，即只更新 `is_deleted` 字段，不进行物理删除。

## 删除机制详解

### 1. 基础软删除（CRUDBase）

所有 CRUD 类都继承自 `CRUDBase`，基类提供了统一的软删除方法：

**文件**: `src/model/crud_base.py`

```python
def delete(self, db: Session, id: int, deleted_by: str = "admin") -> bool:
    """
    软删除记录
    
    Args:
        db: 数据库会话
        id: 记录ID
        deleted_by: 删除人
        
    Returns:
        是否删除成功
    """
    obj = self.get(db=db, id=id)
    if obj:
        obj.is_deleted = True        # 标记为已删除
        obj.updated_by = deleted_by  # 记录删除人
        db.add(obj)
        db.commit()
        return True
    return False
```

**特点**：
- ✅ 只更新 `is_deleted` 和 `updated_by` 字段
- ✅ 不进行物理删除
- ✅ 可追溯删除操作（记录删除人）
- ✅ 数据可恢复

### 2. 物理删除（谨慎使用）

基类也提供了物理删除方法，但**不推荐使用**：

```python
def hard_delete(self, db: Session, id: int) -> bool:
    """
    物理删除记录（谨慎使用！）
    
    注意：此操作不可恢复
    """
    obj = db.query(self.model).filter(self.model.id == id).first()
    if obj:
        db.delete(obj)  # 真正的物理删除
        db.commit()
        return True
    return False
```

## 各模块删除实现

### 1. 会话删除（Session）

**文件**: `src/model/crud_session.py`

```python
def delete_by_session_id(
    self,
    db: DBSession,
    session_id: int,
    deleted_by: str = "system"
) -> bool:
    """根据session_id删除会话（软删除）"""
    session = self.get_by_session_id(db=db, session_id=session_id)
    if not session:
        return False
    
    # 调用基类的 delete 方法（软删除）
    return self.delete(db=db, id=session.id, deleted_by=deleted_by)
```

**删除逻辑**：
- 查询会话
- 调用基类 `delete` 方法进行软删除
- 更新 `is_deleted` 和 `updated_by` 字段

### 2. 会话日志批量删除（SessionLog）

**文件**: `src/model/crud_session_log.py`

```python
def delete_by_session_id(
    self,
    db: Session,
    session_id: int,
    deleted_by: str = "system"
) -> int:
    """软删除某个会话的所有日志"""
    # 使用批量更新，提高性能
    count = db.query(SessionLog).filter(
        SessionLog.session_id == session_id,
        SessionLog.is_deleted == False
    ).update(
        {
            "is_deleted": True,
            "updated_by": deleted_by
        },
        synchronize_session=False
    )
    
    db.commit()
    return count
```

**优化点**：
- ✅ 使用批量更新而非逐条更新
- ✅ 提高了大量数据删除时的性能
- ✅ 减少数据库交互次数

**性能对比**：
- ❌ **旧方法**：循环查询 → 逐条更新 → 多次数据库交互
- ✅ **新方法**：单次批量更新 → 一次数据库交互

### 3. 用户删除（User）

**文件**: `src/model/crud_user.py`

用户删除直接使用基类的 `delete` 方法：

```python
# 在 controller 中调用
crud_user.delete(db=db, id=user_id, deleted_by="admin")
```

### 4. 智能体删除（Agent）

**文件**: `src/model/crud_agent.py`

智能体删除直接使用基类的 `delete` 方法：

```python
# 在 controller 中调用
crud_agent.delete(db=db, id=agent_id, deleted_by=current_user.id)
```

## 控制器层删除实现

### 会话删除接口

**文件**: `src/api/controller/session_controller.py`

```python
@router.delete("/delete", summary="删除会话")
async def delete_session(
    request: SessionDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除会话（软删除）
    
    说明：删除会话时，同时删除会话相关的所有日志
    权限：只能删除自己创建的会话
    """
    # 1. 检查会话是否存在
    session = crud_session.get_by_session_id(db=db, session_id=request.session_id)
    if not session:
        return error_response(
            message=f"会话 {request.session_id} 不存在",
            code=status.HTTP_404_NOT_FOUND
        )
    
    # 2. 权限检查：只能删除自己创建的会话
    if str(session.created_by) != str(current_user.id):
        return error_response(
            message="无权删除该会话，只能删除自己创建的会话",
            code=status.HTTP_403_FORBIDDEN
        )
    
    # 3. 删除会话（软删除）
    success = crud_session.delete_by_session_id(
        db=db,
        session_id=request.session_id,
        deleted_by=str(current_user.id)
    )
    
    # 4. 同时删除会话的所有日志（软删除）
    if success:
        crud_session_log.delete_by_session_id(
            db=db,
            session_id=request.session_id,
            deleted_by=str(current_user.id)
        )
    
    return success_response(message="会话删除成功")
```

**删除流程**：
1. 验证会话是否存在
2. 验证用户权限（只能删除自己的会话）
3. 软删除会话
4. 批量软删除该会话的所有日志

## 查询时过滤已删除数据

所有查询操作都会自动过滤已删除的数据：

```python
# 基类的 get 方法
def get(self, db: Session, id: int) -> Optional[ModelType]:
    return db.query(self.model).filter(
        self.model.id == id,
        self.model.is_deleted == False  # 过滤已删除数据
    ).first()

# 基类的 get_multi 方法
def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
    query = db.query(self.model).filter(
        self.model.is_deleted == False  # 过滤已删除数据
    )
    return query.offset(skip).limit(limit).all()
```

## 数据库表结构要求

所有需要软删除的表都必须包含以下字段：

```sql
CREATE TABLE example_table (
    id BIGINT PRIMARY KEY,
    -- 其他业务字段...
    
    -- 软删除必需字段
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- 审计字段
    created_by VARCHAR(50) NOT NULL,
    updated_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 软删除的优势

1. **数据安全**
   - 误删除可以恢复
   - 保留历史数据用于审计

2. **业务追溯**
   - 记录删除人（`updated_by`）
   - 记录删除时间（`updated_at`）

3. **关联数据完整性**
   - 关联数据不会因为主数据删除而丢失
   - 可以通过查询已删除数据找到历史关联

4. **性能优势**
   - 删除操作更快（只是UPDATE而非DELETE）
   - 不会触发复杂的级联删除

## 注意事项

### 1. 唯一索引问题

如果表有唯一索引，软删除后可能导致唯一性冲突：

```sql
-- 问题：软删除后，username 仍然存在于数据库中
CREATE UNIQUE INDEX idx_username ON users(username);

-- 解决方案：将 is_deleted 加入唯一索引
CREATE UNIQUE INDEX idx_username_not_deleted 
ON users(username) WHERE is_deleted = false;
```

### 2. 定期清理

软删除会导致表数据增长，建议定期归档或清理：

```python
# 示例：清理 90 天前的软删除数据
def cleanup_old_deleted_records(db: Session, days: int = 90):
    """清理指定天数前的软删除记录"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # 这里可以选择硬删除或归档到历史表
    db.query(Session).filter(
        Session.is_deleted == True,
        Session.updated_at < cutoff_date
    ).delete()
    
    db.commit()
```

### 3. 性能优化

- 在 `is_deleted` 字段上创建索引
- 使用批量更新代替逐条更新
- 大量数据删除时考虑分批处理

```sql
-- 为 is_deleted 创建索引
CREATE INDEX idx_is_deleted ON sessions(is_deleted);
```

## 总结

✅ **当前删除逻辑的特点**：
1. 所有删除操作都是软删除
2. 只更新 `is_deleted` 和 `updated_by` 字段
3. 批量删除使用批量更新提高性能
4. 查询时自动过滤已删除数据
5. 支持权限控制和审计追踪

✅ **已优化的内容**：
1. `crud_session_log.py` 的批量删除改为批量更新
2. 所有删除操作都记录删除人
3. 所有查询都过滤 `is_deleted = False`

❌ **不要使用**：
- `hard_delete` 方法（除非有特殊需求）
- 直接使用 `db.delete()` 物理删除
- 不记录 `deleted_by` 的删除操作

