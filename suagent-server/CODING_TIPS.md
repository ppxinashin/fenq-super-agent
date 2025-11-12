# 编码和开发最佳实践

## 🔤 UTF-8 编码问题解决

### 问题原因
`main.py` 出现乱码的原因：
1. 文件保存时使用了错误的字符编码
2. 编辑器或IDE编码设置不正确
3. 文件传输过程中编码被改变

### 解决方案

#### 1. 确保UTF-8编码
```bash
# 检查文件编码
file filename.py

# 转换为UTF-8编码（如果需要）
iconv -f 原编码 -t utf-8 原文件 > 新文件
```

#### 2. 编辑器设置
- **VS Code**: 右下角状态栏检查编码，确保是 UTF-8
- **Vim/Neovim**: `set encoding=utf-8`
- **PyCharm**: Settings → Editor → File Encodings → UTF-8

#### 3. Python文件头（可选）
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

## 🛠️ 开发环境最佳实践

### 1. Conda环境管理
```bash
# 确认当前环境
conda info --envs
which python

# 激活环境（如果需要）
conda activate suagent-server

# 安装包
pip install package_name
```

### 2. 脚本安全性
所有可执行脚本使用绝对路径：
```python
#!/home/ubuntu/miniconda3/envs/suagent-server/bin/python
```

### 3. 路径管理
```python
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
```

## 📝 代码质量

### 1. 异常处理
```python
try:
    # 可能出错的代码
    result = risky_operation()
except SpecificException as e:
    logger.error(f"特定异常: {e}")
    raise
except Exception as e:
    logger.error(f"未处理异常: {e}", exc_info=True)
    raise
```

### 2. 日志记录
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("信息日志")
logger.warning("警告日志")
logger.error("错误日志")
```

### 3. SQLAlchemy语法
```python
# 正确方式
from sqlalchemy import text
conn.execute(text("SQL语句"))

# 错误方式
conn.execute("SQL语句")  # 会报警告
```

## 🚀 调试技巧

### 1. 环境检查
```bash
# 运行环境检查
python check_environment.py
```

### 2. 导入测试
```python
import sys
sys.path.insert(0, 'src')

# 测试关键模块导入
try:
    from module import function
    print("✅ 导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
```

### 3. 快速验证
```bash
# 验证主文件
python -c "from src.main import app; print('应用加载成功')"

# 检查数据库连接
python -c "
from src.model.database import engine
with engine.connect() as conn:
    print('数据库连接正常')
"
```

## 🔧 常见问题排查

### 1. 编码问题
- **症状**: 文件显示乱码或导入失败
- **解决**: 检查文件编码，确保UTF-8

### 2. 导入错误
- **症状**: ModuleNotFoundError
- **解决**: 检查Python路径，使用正确的导入语句

### 3. 环境问题
- **症状**: 包版本冲突或找不到包
- **解决**: 确认在正确的conda环境中

### 4. 数据库连接问题
- **症状**: 连接失败或SQL语法错误
- **解决**: 检查连接字符串，使用`text()`包装SQL

## 📚 项目结构约定

```
src/
├── api_middlewares/          # FastAPI中间件
├── middlewares/              # LangChain中间件
├── service/                  # 业务服务层
├── controller/               # API控制器层
├── model/                    # 数据模型层
├── request/                  # 请求模型
├── response/                 # 响应模型
└── utils/                    # 工具函数
```

## 🎯 安全提醒

1. **不要提交敏感信息**: 密码、API密钥等
2. **使用环境变量**: 配置通过.env文件管理
3. **代码审查**: 重要修改需要仔细检查
4. **备份重要文件**: 在大规模修改前备份

## 🔍 故障排除清单

- [ ] 环境检查通过
- [ ] 文件编码正确（UTF-8）
- [ ] 所有包已安装
- [ ] 导入语句正确
- [ ] 数据库连接正常
- [ ] 日志配置正确
- [ ] 脚本权限正确