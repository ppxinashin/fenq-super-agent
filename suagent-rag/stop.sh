#!/bin/bash

# 停止后台运行的服务

# 设置工作目录为脚本所在目录
cd "$(dirname "$0")"

# 配置变量
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/suagent-rag.log"
PID_FILE="${LOG_DIR}/suagent-rag.pid"

# 检查 PID 文件是否存在
if [ ! -f "${PID_FILE}" ]; then
    echo "未找到 PID 文件，服务可能未运行"
    exit 1
fi

# 读取 PID
PID=$(cat "${PID_FILE}")

# 检查进程是否存在
if ! ps -p "${PID}" > /dev/null 2>&1; then
    echo "进程不存在 (PID: ${PID})，清理 PID 文件..."
    rm -f "${PID_FILE}"
    exit 1
fi

# 记录到日志
echo "===========================================" >> "${LOG_FILE}"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 停止服务 (PID: ${PID})..." >> "${LOG_FILE}"
echo "===========================================" >> "${LOG_FILE}"

# 尝试优雅地停止进程 (SIGTERM)
echo "正在停止服务 (PID: ${PID})..."
kill -9 "${PID}"
# 确认进程已停止
if ps -p "${PID}" > /dev/null 2>&1; then
    echo "✗ 无法停止服务"
    exit 1
else
    echo "✓ 服务已停止"
    rm -f "${PID_FILE}"
fi

