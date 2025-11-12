# SuAgent Tasks - 定时任务系统

这是从SuAgent主项目中拆分出来的独立定时任务系统，负责执行各种定时和异步任务。

## 功能特性

- **定时记忆同步**: 自动同步用户的长期记忆数据
- **存储监控**: 监控MinIO存储使用情况
- **分布式任务**: 基于Celery的分布式任务队列
- **任务监控**: 提供Flower监控界面

## 项目结构

```
suagent-tasks/
├── src/
│   ├── scheduler/          # 定时任务核心模块
│   │   ├── tasks.py       # Celery任务定义
│   │   ├── celery_app.py  # Celery应用配置
│   │   ├── config.py      # 调度器配置
│   │   ├── memory_sync_service.py  # 记忆同步服务
│   │   ├── minio_client.py         # MinIO客户端
│   │   └── utils/         # 工具模块
│   ├── model/             # 数据模型
│   ├── utils/             # 工具函数
│   ├── config/            # 配置文件
│   └── consts/            # 常量定义
├── config/                # 环境配置
├── docs/                  # 文档
├── scripts/               # 脚本文件
├── scheduler_main.py      # 主入口文件
└── requirements.txt       # Python依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制配置文件并根据需要修改：

```bash
cp config/scheduler.env.example .env
```

主要配置项：
- `CELERY_BROKER_URL`: Redis连接URL
- `CELERY_RESULT_BACKEND`: Redis结果后端
- `DATABASE_URL`: PostgreSQL数据库连接
- `MINIO_ENDPOINT`: MinIO服务端点
- `MINIO_ACCESS_KEY`: MinIO访问密钥
- `MINIO_SECRET_KEY`: MinIO密钥

### 3. 启动服务

#### 启动Celery Worker
```bash
python scheduler_main.py worker
```

#### 启动Celery Beat (定时任务调度器)
```bash
python scheduler_main.py beat
```

#### 启动Flower监控
```bash
python scheduler_main.py flower
```

### 4. 验证配置

```bash
python scheduler_main.py validate
```

### 5. 查看状态

```bash
python scheduler_main.py status
```

## 主要命令

```bash
# 启动各种服务
python scheduler_main.py worker      # 启动Worker
python scheduler_main.py beat        # 启动定时任务调度器
python scheduler_main.py flower      # 启动监控界面

# 管理任务
python scheduler_main.py task sync_daily           # 运行每日同步任务
python scheduler_main.py task sync_user user123    # 同步指定用户
python scheduler_main.py task monitor              # 运行监控任务

# 系统管理
python scheduler_main.py validate     # 验证配置
python scheduler_main.py status       # 查看系统状态
```

## 定时任务

系统支持以下定时任务：

1. **每日记忆同步** (`sync_daily_user_memory`)
   - 每天凌晨2点执行
   - 同步所有启用长期记忆的用户数据

2. **存储监控** (`monitor_storage_usage`)
   - 每6小时执行一次
   - 监控MinIO存储使用情况

3. **用户记忆同步** (`sync_user_memories`)
   - 按需执行指定用户的记忆同步

## 监控

访问Flower监控界面：
- URL: http://localhost:5555
- 默认用户名/密码: admin/password

可在配置文件中修改端口和认证信息。

## 日志

系统日志位于：
- `/var/log/celery/scheduler.log` - 主调度器日志
- `/var/log/celery/worker.log` - Worker日志
- `/var/log/celery/beat.log` - Beat调度器日志
- `/var/log/celery/flower.log` - Flower监控日志

## 部署

详细部署指南请参考：
- [部署指南](docs/scheduler_deployment_guide.md)
- [架构说明](docs/scheduler_architecture.md)

## 注意事项

1. 本项目依赖PostgreSQL数据库和Redis服务
2. 需要正确配置MinIO连接信息
3. 确保有足够的权限访问数据库和存储服务
4. 建议在生产环境中使用supervisor等工具管理进程