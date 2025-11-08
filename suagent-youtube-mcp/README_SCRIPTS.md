# 🚀 脚本使用快速参考

## 📋 概述

本项目提供了完整的后台运行管理脚本，支持 conda 环境管理、服务启停、日志监控等功能。

## 🎯 快速开始

### 第一次使用（完整流程）

```bash
# 1. 初始化环境（创建 conda 环境并安装依赖）
./setup_env.sh

# 2. 检查环境是否正确配置
./check_env.sh

# 3. 启动服务
./start.sh

# 4. 查看服务状态
./status.sh

# 5. 实时查看日志
tail -f logs/suagent-youtube-mcp.log
```

### 后续使用（环境已配置）

```bash
# 启动服务
./start.sh

# 查看状态
./status.sh

# 停止服务
./stop.sh

# 重启服务
./restart.sh
```

## 📚 脚本说明

### 环境管理

| 脚本 | 功能 | 使用时机 |
|------|------|----------|
| `setup_env.sh` | 创建 conda 环境并安装依赖 | 首次部署或重建环境 |
| `check_env.sh` | 检查环境配置是否正确 | 排查环境问题 |

### 服务管理

| 脚本 | 功能 | 说明 |
|------|------|------|
| `start.sh` | 启动服务 | 后台运行，自动激活 conda 环境 |
| `stop.sh` | 停止服务 | 优雅关闭（SIGTERM → SIGKILL） |
| `restart.sh` | 重启服务 | 先停止再启动 |
| `status.sh` | 查看状态 | 显示运行状态、PID、内存等 |

### 日志管理

| 脚本 | 功能 | 说明 |
|------|------|------|
| `rotate_logs.sh` | 日志轮转 | 日志超过 100MB 时自动轮转 |

## 🔧 环境要求

- **Conda**: Miniconda 或 Anaconda
- **Python**: 3.13
- **操作系统**: Linux (推荐 Ubuntu)

## 📁 文件结构

```
suagent-youtube-mcp/
├── setup_env.sh          # 环境初始化
├── check_env.sh          # 环境检查
├── start.sh              # 启动服务
├── stop.sh               # 停止服务
├── restart.sh            # 重启服务
├── status.sh             # 查看状态
├── rotate_logs.sh        # 日志轮转
├── main.py               # 主程序
├── requirements.txt      # Python 依赖
├── logs/                 # 日志目录
│   ├── suagent-youtube-mcp.log   # 主日志文件
│   └── suagent-youtube-mcp.pid   # 进程 PID 文件
└── README_SCRIPTS.md     # 本文档
```

## 📊 日志查看

```bash
# 实时跟踪日志
tail -f logs/suagent-youtube-mcp.log

# 查看最近 100 行
tail -n 100 logs/suagent-youtube-mcp.log

# 搜索错误
grep -i "error" logs/suagent-youtube-mcp.log

# 查看今天的日志
grep "$(date '+%Y-%m-%d')" logs/suagent-youtube-mcp.log
```

## ⚙️ 常见操作

### 更新依赖

```bash
# 方法 1: 激活环境后安装
conda activate suagent-youtube-mcp
pip install -r requirements.txt

# 方法 2: 使用 conda run
conda run -n suagent-youtube-mcp pip install -r requirements.txt

# 方法 3: 重新创建环境
./setup_env.sh
```

### 查看运行中的进程

```bash
# 使用提供的脚本
./status.sh

# 手动查看
ps aux | grep "python main.py"

# 查看进程树
pstree -p $(cat logs/suagent-youtube-mcp.pid)
```

### 清理日志

```bash
# 手动轮转日志
./rotate_logs.sh

# 清空日志（谨慎使用）
> logs/suagent-youtube-mcp.log

# 删除旧的备份
rm -f logs/suagent-youtube-mcp.log.*.gz
```

## 🐛 故障排查

### 问题：服务无法启动

```bash
# 1. 检查环境
./check_env.sh

# 2. 查看日志
cat logs/suagent-youtube-mcp.log

# 3. 手动测试
conda activate suagent-youtube-mcp
python main.py
```

### 问题：conda 环境不存在

```bash
# 重新创建环境
./setup_env.sh
```

### 问题：依赖包缺失

```bash
# 重新安装依赖
conda activate suagent-youtube-mcp
pip install -r requirements.txt
```

### 问题：PID 文件错误

```bash
# 检查状态
./status.sh

# 手动清理
rm -f logs/suagent-youtube-mcp.pid

# 重新启动
./start.sh
```

## 🔐 权限问题

如果脚本无法执行：

```bash
# 给所有脚本添加执行权限
chmod +x *.sh

# 或单独添加
chmod +x setup_env.sh check_env.sh start.sh stop.sh restart.sh status.sh rotate_logs.sh
```

## 🌟 最佳实践

1. **首次部署**：按照"快速开始"的完整流程操作
2. **定期检查**：使用 `./status.sh` 定期检查服务状态
3. **日志管理**：定期运行 `./rotate_logs.sh` 或设置 cron 任务
4. **环境隔离**：使用独立的 conda 环境，避免依赖冲突
5. **备份配置**：如有配置文件（.env），记得备份

## 🔄 自动化日志轮转（可选）

设置 cron 任务，每天自动运行日志轮转：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天凌晨执行）
0 0 * * * /home/ubuntu/fenq-super-agent/suagent-youtube-mcp/rotate_logs.sh
```

## 📞 获取帮助

- **查看日志**: `tail -f logs/suagent-youtube-mcp.log`
- **检查环境**: `./check_env.sh`
- **查看状态**: `./status.sh`

---

💡 **提示**: 所有脚本都会自动处理 conda 环境激活，无需手动激活环境后再运行脚本。

