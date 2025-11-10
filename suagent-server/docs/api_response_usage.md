# API 响应格式使用说明

## 概述

本项目采用统一的API响应格式，包含通用响应格式和分页响应格式。

## 响应格式结构

### 1. 通用响应格式 (ApiResponse)

```python
{
    "code": 200,          # 状态码
    "message": "OK",      # 响应消息
    "result": {...}       # 响应数据（可选）
}
```

### 2. 分页响应格式 (Pageable)

```python
{
    "page": 1,           # 当前页码
    "page_size": 10,     # 每页大小
    "total": 100,        # 总记录数
    "data": [...]        # 数据列表
}
```

## 状态码定义

### HTTP标准状态码

| 状态码 | 常量 | 说明 |
|--------|------|------|
| 200 | StatusCode.OK | 成功 |
| 201 | StatusCode.CREATED | 已创建 |
| 202 | StatusCode.ACCEPTED | 已接受 |
| 204 | StatusCode.NO_CONTENT | 无内容 |
| 400 | StatusCode.BAD_REQUEST | 请求错误 |
| 401 | StatusCode.UNAUTHORIZED | 未授权 |
| 403 | StatusCode.FORBIDDEN | 禁止访问 |
| 404 | StatusCode.NOT_FOUND | 未找到 |
| 409 | StatusCode.CONFLICT | 冲突 |
| 422 | StatusCode.UNPROCESSABLE_ENTITY | 无法处理的实体 |
| 429 | StatusCode.TOO_MANY_REQUESTS | 请求过多 |
| 500 | StatusCode.INTERNAL_SERVER_ERROR | 服务器错误 |
| 503 | StatusCode.SERVICE_UNAVAILABLE | 服务不可用 |

### 自定义状态码

| 状态码 | 常量 | 说明 |
|--------|------|------|
| 299 | StatusCode.BUSINESS_ERROR | 业务错误 |

## 使用示例

### 1. 基础使用

#### 成功响应

```python
from src.api.response import ApiResponse, success_response
from src.consts import StatusCode

# 方法1：使用类方法
response = ApiResponse.success(result={"id": 1, "name": "张三"})

# 方法2：使用便捷函数
response = success_response(result={"id": 1, "name": "张三"})

# 方法3：自定义消息
response = ApiResponse.success(
    result={"id": 1, "name": "张三"},
    message="用户创建成功"
)

# 输出
{
    "code": 200,
    "message": "OK",
    "result": {"id": 1, "name": "张三"}
}
```

#### 业务错误响应 (299)

```python
from src.api.response import business_error_response, error_response
from src.consts import StatusCode

# 方法1：使用专用函数（推荐）
response = business_error_response("用户名已存在")

# 方法2：使用通用函数
response = error_response("用户名已存在", code=StatusCode.BUSINESS_ERROR)

# 方法3：使用类方法
response = ApiResponse.error(
    message="用户名已存在",
    code=StatusCode.BUSINESS_ERROR
)

# 输出
{
    "code": 299,
    "message": "用户名已存在",
    "result": null
}
```

#### 其他错误响应

```python
from src.api.response import error_response
from src.consts import StatusCode

# 未找到
response = error_response("用户不存在", code=StatusCode.NOT_FOUND)
# 输出: {"code": 404, "message": "用户不存在", "result": null}

# 未授权
response = error_response("请先登录", code=StatusCode.UNAUTHORIZED)
# 输出: {"code": 401, "message": "请先登录", "result": null}

# 权限不足
response = error_response("权限不足", code=StatusCode.FORBIDDEN)
# 输出: {"code": 403, "message": "权限不足", "result": null}

# 服务器错误
response = error_response("服务器内部错误", code=StatusCode.INTERNAL_SERVER_ERROR)
# 输出: {"code": 500, "message": "服务器内部错误", "result": null}
```

### 2. FastAPI集成

#### 基础CRUD接口

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.model import get_db, crud_user, User
from src.api.response import ApiResponse, success_response, business_error_response
from src.consts import StatusCode

router = APIRouter()

# 创建用户
@router.post("/users", response_model=ApiResponse[User])
async def create_user(username: str, password: str, db: Session = Depends(get_db)):
    """创建用户"""
    try:
        # 检查用户是否存在
        existing = crud_user.get_by_username(db, username)
        if existing:
            return business_error_response("用户名已存在")
        
        # 创建用户
        user = crud_user.create_user(db, username, password)
        return success_response(result=user, message="用户创建成功")
        
    except Exception as e:
        return ApiResponse.error(
            message=f"创建失败: {str(e)}",
            code=StatusCode.INTERNAL_SERVER_ERROR
        )

# 获取用户
@router.get("/users/{user_id}", response_model=ApiResponse[User])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = crud_user.get(db, user_id)
    if not user:
        return ApiResponse.error("用户不存在", code=StatusCode.NOT_FOUND)
    
    return success_response(result=user)

# 更新用户
@router.put("/users/{user_id}", response_model=ApiResponse[User])
async def update_user(user_id: int, username: str, db: Session = Depends(get_db)):
    """更新用户信息"""
    user = crud_user.get(db, user_id)
    if not user:
        return ApiResponse.error("用户不存在", code=StatusCode.NOT_FOUND)
    
    # 更新
    update_data = {"username": username}
    updated_user = crud_user.update(db, user, update_data)
    
    return success_response(result=updated_user, message="更新成功")

# 删除用户
@router.delete("/users/{user_id}", response_model=ApiResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    success = crud_user.delete(db, user_id)
    if not success:
        return ApiResponse.error("用户不存在", code=StatusCode.NOT_FOUND)
    
    return success_response(message="删除成功")
```

### 3. 分页查询

#### 使用Pageable响应

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.model import get_db, crud_user, User
from src.api.response import ApiResponse, success_response, Pageable
from pydantic import BaseModel

router = APIRouter()

# 定义返回模型
class UserListResponse(BaseModel):
    id: int
    username: str
    role: str

# 分页查询用户
@router.get("/users", response_model=ApiResponse[Pageable[UserListResponse]])
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db)
):
    """分页查询用户列表"""
    # 方法1：从数据库查询结果创建
    page_data = crud_user.get_paginated(db, page=page, page_size=page_size)
    
    # 转换为Pageable对象
    pageable = Pageable.from_dict(page_data, data_key="items")
    
    return success_response(result=pageable)

# 或者直接使用
@router.get("/users/simple", response_model=ApiResponse[Pageable[User]])
async def list_users_simple(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """分页查询用户（简化版）"""
    page_data = crud_user.get_paginated(db, page=page, page_size=page_size)
    
    # 方法2：直接创建
    pageable = Pageable(
        page=page_data["page"],
        page_size=page_data["page_size"],
        total=page_data["total"],
        data=page_data["items"]
    )
    
    return success_response(result=pageable)
```

#### 分页响应示例

```json
{
    "code": 200,
    "message": "OK",
    "result": {
        "page": 1,
        "page_size": 10,
        "total": 100,
        "data": [
            {"id": 1, "username": "user1", "role": "admin"},
            {"id": 2, "username": "user2", "role": "user"},
            ...
        ]
    }
}
```

### 4. 高级用法

#### 自定义响应类型

```python
from typing import List
from pydantic import BaseModel
from src.api.response import ApiResponse, success_response

class UserStats(BaseModel):
    total_users: int
    active_users: int
    admin_count: int

@router.get("/users/stats", response_model=ApiResponse[UserStats])
async def get_user_stats(db: Session = Depends(get_db)):
    """获取用户统计信息"""
    stats = {
        "total_users": 100,
        "active_users": 80,
        "admin_count": 5
    }
    return success_response(result=stats)
```

#### 列表响应

```python
from typing import List

@router.get("/users/all", response_model=ApiResponse[List[User]])
async def get_all_users(db: Session = Depends(get_db)):
    """获取所有用户（不分页）"""
    users = crud_user.get_multi(db, limit=1000)
    return success_response(result=users)
```

#### 空响应

```python
@router.post("/users/notify")
async def notify_users():
    """通知用户（无返回数据）"""
    # 执行通知逻辑
    return success_response(message="通知发送成功")
    # 输出: {"code": 200, "message": "通知发送成功", "result": null}
```

### 5. 异常处理

#### 使用异常处理器

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.api.response import ApiResponse
from src.consts import StatusCode

app = FastAPI()

# 全局异常处理
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """处理ValueError异常"""
    response = ApiResponse.error(
        message=str(exc),
        code=StatusCode.BUSINESS_ERROR
    )
    return JSONResponse(
        status_code=200,  # HTTP状态码始终返回200
        content=response.dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    response = ApiResponse.error(
        message="服务器内部错误",
        code=StatusCode.INTERNAL_SERVER_ERROR
    )
    return JSONResponse(
        status_code=200,
        content=response.dict()
    )
```

#### 在路由中使用try-except

```python
@router.post("/users")
async def create_user(username: str, password: str, db: Session = Depends(get_db)):
    """创建用户（带异常处理）"""
    try:
        user = crud_user.create_user(db, username, password)
        return success_response(result=user)
    except ValueError as e:
        # 业务错误
        return business_error_response(str(e))
    except Exception as e:
        # 系统错误
        return ApiResponse.error(
            message="系统错误，请稍后重试",
            code=StatusCode.INTERNAL_SERVER_ERROR
        )
```

## 前端对接示例

### JavaScript/TypeScript

```typescript
// 定义响应类型
interface ApiResponse<T = any> {
    code: number;
    message: string;
    result: T | null;
}

interface Pageable<T> {
    page: number;
    page_size: number;
    total: number;
    data: T[];
}

// 请求函数
async function apiRequest<T>(url: string, options?: RequestInit): Promise<T> {
    const response = await fetch(url, options);
    const data: ApiResponse<T> = await response.json();
    
    // 判断业务状态
    if (data.code === 200) {
        return data.result as T;
    } else if (data.code === 299) {
        // 业务错误
        throw new Error(data.message);
    } else {
        // 其他错误
        throw new Error(`错误 ${data.code}: ${data.message}`);
    }
}

// 使用示例
interface User {
    id: number;
    username: string;
    role: string;
}

// 获取用户列表（分页）
async function getUserList(page: number = 1, pageSize: number = 10) {
    try {
        const pageable = await apiRequest<Pageable<User>>(
            `/api/users?page=${page}&page_size=${pageSize}`
        );
        
        console.log(`总记录数: ${pageable.total}`);
        console.log(`数据:`, pageable.data);
    } catch (error) {
        console.error('获取用户列表失败:', error.message);
    }
}

// 创建用户
async function createUser(username: string, password: string) {
    try {
        const user = await apiRequest<User>('/api/users', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        
        console.log('用户创建成功:', user);
    } catch (error) {
        if (error.message.includes('已存在')) {
            alert('用户名已存在');
        } else {
            alert('创建失败');
        }
    }
}
```

## 最佳实践

### 1. 状态码使用原则

- **200**: 操作成功
- **299**: 业务逻辑错误（如用户名已存在、余额不足等）
- **400**: 请求参数错误
- **401**: 未登录
- **403**: 无权限
- **404**: 资源不存在
- **500**: 服务器错误

### 2. 消息规范

- 200状态码：使用"OK"或简短的成功消息
- 299状态码：提供清晰的业务错误原因
- 其他状态码：根据实际情况提供具体错误信息

### 3. 分页参数

- `page`: 从1开始，不是0
- `page_size`: 建议默认10，最大100
- 使用Query参数验证确保参数合法

### 4. 返回数据

- 单个对象：直接返回对象
- 列表（不分页）：返回List[T]
- 列表（分页）：返回Pageable[T]
- 无数据：result为null，message说明操作结果

## 相关文件

- 状态码定义: `src/consts/status_code.py`
- 通用响应: `src/api/response/base_response.py`
- 分页响应: `src/api/response/pageable.py`

