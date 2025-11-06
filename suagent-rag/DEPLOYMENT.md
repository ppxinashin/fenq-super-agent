# SuAgent-RAG 部署和运行说明

## 环境要求

- **Conda**: Miniconda 或 Anaconda
- **Python**: 3.13
- **操作系统**: Linux (推荐 Ubuntu)

## 快速开始

### 1. 安装 Conda（如果尚未安装）

请访问 [Miniconda 官网](https://docs.conda.io/en/latest/miniconda.html) 下载并安装。

### 2. 初始化环境

首次使用前，运行初始化脚本创建 conda 环境并安装依赖：

```bash
./setup_env.sh
```

这个脚本会：
- 创建名为 `suagent-rag` 的 conda 环境
- 使用 Python 3.13
- 自动安装 `requirements.txt` 中的所有依赖

### 3. 检查环境

验证环境是否正确配置：

```bash
./check_env.sh
```

### 4. 启动服务

```bash
./start.sh
```

## 后台运行脚本

本项目提供了一套完整的后台运行管理脚本，用于启动、停止和监控 MinIO 事件监听器服务。所有脚本都会自动激活 conda 环境。

## 脚本列表

### 0. `setup_env.sh` - 初始化环境（首次运行）
创建 conda 环境并安装项目依赖。

```bash
./setup_env.sh
```

**功能：**
- 创建 conda 环境 `suagent-rag`
- 指定 Python 版本 3.13
- 安装 requirements.txt 中的所有依赖
- 自动升级 pip

### 0.1. `check_env.sh` - 检查环境
验证 conda 环境和依赖是否正确安装。

```bash
./check_env.sh
```

**检查内容：**
- conda 是否安装
- conda 环境是否存在
- Python 版本是否正确
- 关键依赖包是否已安装

### 1. `start.sh` - 启动服务
启动服务并在后台运行，所有日志输出将重定向到 `logs/suagent-rag.log` 文件。

```bash
./start.sh
```

**功能：**
- 自动初始化并激活 conda 环境
- 检查 conda 环境是否存在
- 检查服务是否已在运行
- 使用 conda 环境中的 Python 启动程序
- 后台运行（使用 nohup 和 conda run）
- 保存进程 PID 到 `logs/suagent-rag.pid`
- 将所有输出（stdout 和 stderr）记录到日志文件
- 自动添加时间戳

### 2. `stop.sh` - 停止服务
优雅地停止正在运行的服务。

```bash
./stop.sh
```

**功能：**
- 读取 PID 文件获取进程 ID
- 首先发送 SIGTERM 信号尝试优雅关闭
- 如果 10 秒后进程仍在运行，则强制终止（SIGKILL）
- 清理 PID 文件
- 记录停止时间到日志

### 3. `status.sh` - 查看服务状态
显示服务的运行状态和详细信息。

```bash
./status.sh
```

**显示信息：**
- 服务运行状态（运行中/已停止）
- 进程 ID (PID)
- 进程详细信息
- 运行时长
- 内存使用情况
- 最近的 10 行日志

### 4. `restart.sh` - 重启服务
停止并重新启动服务。

```bash
./restart.sh
```

**功能：**
- 调用 `stop.sh` 停止服务
- 等待 2 秒
- 调用 `start.sh` 启动服务

### 5. `rotate_logs.sh` - 日志轮转
管理日志文件大小，防止日志文件过大。

```bash
./rotate_logs.sh
```

**功能：**
- 检查日志文件大小
- 当日志文件超过 100MB 时自动轮转
- 保留最近 10 个备份文件
- 自动压缩旧日志文件（.gz 格式）

**建议：** 在 crontab 中配置定期执行，例如每天午夜执行：
```bash
# 编辑 crontab
crontab -e

# 添加以下行（请修改路径为实际路径）
0 0 * * * /home/ubuntu/fenq-super-agent/suagent-rag/rotate_logs.sh
```

## 日志管理

### 日志文件位置
所有日志都保存在 `logs/` 目录下：
- `logs/suagent-rag.log` - 主日志文件
- `logs/suagent-rag.pid` - 进程 ID 文件
- `logs/suagent-rag.log.1.gz` - 轮转后的日志备份

### 实时查看日志
```bash
# 实时跟踪日志输出
tail -f logs/suagent-rag.log

# 查看最近 100 行
tail -n 100 logs/suagent-rag.log

# 搜索特定内容
grep "ERROR" logs/suagent-rag.log

# 查看带颜色的日志（如果支持）
tail -f logs/suagent-rag.log | ccze -A
```

### 日志分析
```bash
# 统计错误数量
grep -c "ERROR" logs/suagent-rag.log

# 查看今天的日志
grep "$(date '+%Y-%m-%d')" logs/suagent-rag.log

# 查看特定时间段的日志
grep "2025-11-06 10:" logs/suagent-rag.log
```

## 典型使用流程

### 首次部署
```bash
# 1. 初始化 conda 环境（仅首次需要）
./setup_env.sh

# 2. 检查环境配置
./check_env.sh

# 3. 启动服务
./start.sh

# 4. 检查状态
./status.sh

# 5. 查看日志
tail -f logs/suagent-rag.log
```

### 后续启动
```bash
# 如果环境已配置好，直接启动即可
./start.sh

# 检查状态
./status.sh
```

### 日常维护
```bash
# 检查服务状态
./status.sh

# 重启服务（如有配置更新）
./restart.sh

# 手动轮转日志
./rotate_logs.sh
```

### 问题排查
```bash
# 1. 查看服务状态
./status.sh

# 2. 查看完整日志
less logs/suagent-rag.log

# 3. 搜索错误信息
grep -i "error\|exception\|failed" logs/suagent-rag.log

# 4. 如需重启
./restart.sh
```

## 开机自启动（可选）

### 使用 systemd 服务

1. 创建服务文件 `/etc/systemd/system/suagent-rag.service`：

```ini
[Unit]
Description=SuAgent RAG Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fenq-super-agent/suagent-rag
Environment="PATH=/home/ubuntu/miniconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/ubuntu/miniconda3/bin/conda run --no-capture-output -n suagent-rag python /home/ubuntu/fenq-super-agent/suagent-rag/main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/ubuntu/fenq-super-agent/suagent-rag/logs/suagent-rag.log
StandardError=append:/home/ubuntu/fenq-super-agent/suagent-rag/logs/suagent-rag.log

[Install]
WantedBy=multi-user.target
```

**注意：** 请根据实际情况修改以下路径：
- `User`: 您的用户名
- `WorkingDirectory`: 项目路径
- `Environment PATH`: conda 安装路径
- `ExecStart`: conda 路径和项目路径

2. 启用并启动服务：

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable suagent-rag

# 启动服务
sudo systemctl start suagent-rag

# 查看状态
sudo systemctl status suagent-rag

# 查看日志
sudo journalctl -u suagent-rag -f
```

### 使用 crontab（简单方式）

```bash
# 编辑 crontab
crontab -e

# 添加以下行
@reboot cd /home/ubuntu/fenq-super-agent/suagent-rag && ./start.sh
```

## 注意事项

1. **Conda 环境**：
   - 首次运行前必须执行 `./setup_env.sh` 创建环境
   - 环境名称固定为 `suagent-rag`，Python 版本为 3.13
   - 如果修改了 `requirements.txt`，需要重新安装依赖
   - 使用 `./check_env.sh` 验证环境配置

2. **环境变量**：
   - 确保脚本能够访问到 conda 命令
   - 如需配置环境变量，可以在项目根目录创建 `.env` 文件
   - 脚本会自动初始化 conda 环境

3. **权限问题**：
   - 确保脚本有执行权限（已通过 `chmod +x` 设置）
   - 如果遇到权限问题，运行：`chmod +x *.sh`

4. **日志大小**：
   - 定期运行 `rotate_logs.sh` 或设置 cron 任务，避免日志文件过大
   - 默认当日志超过 100MB 时会自动轮转

5. **进程管理**：
   - 使用提供的脚本而不是直接 kill 进程，以确保 PID 文件正确管理
   - 脚本使用 `conda run` 确保在正确的环境中运行

6. **重复启动**：
   - `start.sh` 会检查服务是否已在运行，避免重复启动
   - 如需重启，请使用 `./restart.sh`

7. **异常退出**：
   - 如果服务异常退出，PID 文件可能仍然存在
   - 使用 `status.sh` 检查状态，必要时手动删除 PID 文件
   - 查看日志文件排查问题原因

## 故障排查

### Conda 环境问题
```bash
# 检查 conda 是否可用
which conda
conda --version

# 检查环境是否存在
conda env list | grep suagent-rag

# 检查环境配置
./check_env.sh

# 重新创建环境
./setup_env.sh
```

### 服务无法启动
```bash
# 1. 检查环境配置
./check_env.sh

# 2. 检查 conda 环境中的 Python
conda run -n suagent-rag python --version

# 3. 检查依赖
conda run -n suagent-rag pip list

# 4. 查看详细错误
cat logs/suagent-rag.log

# 5. 手动测试启动
conda activate suagent-rag
python main.py
```

### 服务自动停止
```bash
# 查看最近的日志
tail -n 50 logs/suagent-rag.log

# 检查系统日志
dmesg | tail

# 检查是否是内存问题
free -h
```

### PID 文件问题
```bash
# 手动清理 PID 文件
rm -f logs/suagent-rag.pid

# 重新启动
./start.sh
```

## 联系支持

如有问题，请查看日志文件或联系技术支持团队。

