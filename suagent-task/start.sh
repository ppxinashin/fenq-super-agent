#!/bin/bash

# 启动长期记忆同步定时任务（后台运行）
set -euo pipefail

cd "$(dirname "$0")"

LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/memory-sync-task.log"
PID_FILE="${LOG_DIR}/memory-sync-task.pid"
CMD="python -m src.task_runner"

mkdir -p "${LOG_DIR}"

if [ -f "${PID_FILE}" ] && ps -p "$(cat "${PID_FILE}")" > /dev/null 2>&1; then
  echo "任务已经在运行 (PID: $(cat "${PID_FILE}"))"
  exit 0
fi

nohup ${CMD} >> "${LOG_FILE}" 2>&1 &
echo $! > "${PID_FILE}"

echo "已启动定时任务调度器"
echo "  日志: ${LOG_FILE}"
echo "  PID: $(cat "${PID_FILE}")"
