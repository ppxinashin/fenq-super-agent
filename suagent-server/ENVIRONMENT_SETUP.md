# Conda 环境设置说明

## 当前环境

✅ **正在使用的环境**: `suagent-server` conda 环境
✅ **Python 版本**: 3.13.9
✅ **环境路径**: `/home/ubuntu/miniconda3/envs/suagent-server`

## 环境验证

运行以下命令验证环境设置：

```bash
# 检查当前环境
python check_environment.py

# 或者手动检查
conda info --envs  # 确认 suagent-server 环境存在
which python       # 应该指向 suagent-server 环境
python --version   # 应该显示 Python 3.13.9
```

## 关键依赖包

以下包已安装在 `suagent-server` 环境中：

### Web框架
- `fastapi==0.120.3` - Web框架
- `uvicorn==0.38.0` - ASGI服务器
- `pydantic==2.12.3` - 数据验证

### 认证相关
- `python-jose[cryptography]==3.5.0` - JWT处理
- `PyJWT==2.10.1` - JWT token生成验证

### 工具库
- `loguru==0.7.3` - 日志库
- `aiohttp==3.11.12` - HTTP客户端

## 项目结构

```
suagent-server/
├── src/
│   ├── api_middlewares/          # 🆕 FastAPI认证中间件
│   │   ├── __init__.py
│   │   └── jwt_middleware.py
│   ├── middlewares/              # 🔄 LangChain中间件
│   │   ├── __init__.py
│   │   ├── my_logger_middleware.py
│   │   └── session_middleware.py
│   ├── service/                  # 服务层
│   │   ├── auth_service.py
│   │   └── token_service.py
│   ├── controller/               # 控制器层
│   │   └── auth_controller.py
│   ├── model/                    # 数据模型
│   ├── request/                  # 请求模型
│   ├── response/                 # 响应模型
│   └── main.py                   # 🚀 主入口文件
├── check_environment.py          # 🔍 环境检查脚本
├── start_server.py               # 🚀 启动脚本（conda环境）
├── test_auth.py                  # 🧪 测试脚本（conda环境）
└── AUTH_API_DOCS.md             # 📚 API文档
```

## 使用方法

### 1. 启动服务器
```bash
# 直接运行（自动使用conda环境中的Python）
python start_server.py

# 或者明确指定conda环境
/home/ubuntu/miniconda3/envs/suagent-server/bin/python start_server.py
```

### 2. 运行测试
```bash
# 运行认证功能测试
python test_auth.py
```

### 3. 环境检查
```bash
# 验证所有配置正确
python check_environment.py
```

## 重要提示

### 环境隔离
- ✅ 所有脚本都使用shebang指向conda环境中的Python
- ✅ 确保不使用系统Python或其他conda环境
- ✅ 所有依赖都安装在`suagent-server`环境中

### 路径设置
- ✅ 脚本自动添加`src/`目录到Python路径
- ✅ 使用相对路径导入项目模块

### 依赖管理
- ✅ 已安装所有必需的包
- ✅ JWT包已正确配置（python-jose[cryptography]）

## 故障排除

如果遇到问题，请检查：

1. **环境确认**:
   ```bash
   python check_environment.py
   ```

2. **依赖安装**:
   ```bash
   pip install python-jose[cryptography]
   pip install fastapi uvicorn
   ```

3. **路径问题**:
   - 确保在项目根目录中运行脚本
   - 检查`src/`目录存在

## 安全配置

在生产环境中，请确保：

1. **修改默认密钥**:
   ```env
   JWT_SECRET_KEY=your-production-secret-key
   ```

2. **配置HTTPS**:
   - 使用反向代理（Nginx）
   - 配置SSL证书

3. **环境隔离**:
   - 不要在生产环境使用调试模式
   - 配置适当的CORS策略