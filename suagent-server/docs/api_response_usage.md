# API 响应格式使用说明

## 响应格式结构

### 1. 通用响应格式 (ApiResponse)

```python
{
    "code": 200,
    "message": "OK",
    "result": {...}
}
```

### 2. 分页响应格式 (Pageable)

```python
{
    "page": 1,
    "page_size": 10,
    "total": 100,
    "data": [...]
}
```

## 状态码定义

| 状态码 | 常量 | 说明 |
|--------|------|------|
| 200 | StatusCode.OK | 成功 |
| 299 | StatusCode.BUSINESS_ERROR | 业务错误 |
| 400 | StatusCode.BAD_REQUEST | 请求错误 |
| 401 | StatusCode.UNAUTHORIZED | 未授权 |
| 403 | StatusCode.FORBIDDEN | 禁止访问 |
| 404 | StatusCode.NOT_FOUND | 未找到 |
| 500 | StatusCode.INTERNAL_SERVER_ERROR | 服务器错误 |

## 使用方法

### 成功响应

```python
from src.api.response import ApiResponse, success_response

response = ApiResponse.success(result={"id": 1, "name": "张三"})
# 或
response = success_response(result={"id": 1, "name": "张三"})
```

### 业务错误响应

```python
from src.api.response import business_error_response

response = business_error_response("用户名已存在")
```

### 分页查询

```python
from src.api.response import Pageable

pageable = Pageable(
    page=page_data["page"],
    page_size=page_data["page_size"],
    total=page_data["total"],
    data=page_data["items"]
)
return success_response(result=pageable)
```

## 相关文件

- 状态码定义: `src/consts/status_code.py`
- 通用响应: `src/api/response/base_response.py`
- 分页响应: `src/api/response/pageable.py`
