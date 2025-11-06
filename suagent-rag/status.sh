#!/bin/bash

# 查看服务运行状态

# 设置工作目录为脚本所在目录
cd "$(dirname "$0")"

# 配置变量
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/suagent-rag.log"
PID_FILE="${LOG_DIR}/suagent-rag.pid"

echo "=========================================="
echo "  SuAgent-RAG 服务状态"
echo "=========================================="
echo ""

# 检查 PID 文件是否存在
if [ ! -f "${PID_FILE}" ]; then
    echo "状态: ✗ 未运行"
    echo "PID 文件不存在"
    exit 0
fi

# 读取 PID
PID=$(cat "${PID_FILE}")

# 检查进程是否存在
if ps -p "${PID}" > /dev/null 2>&1; then
    echo "状态: ✓ 运行中"
    echo "PID: ${PID}"
    
    # 显示进程信息
    echo ""
    echo "进程信息:"
    ps -f -p "${PID}"
    
    # 显示运行时长
    echo ""
    echo "运行时长:"
    ps -o etime= -p "${PID}" | sed 's/^[[:space:]]*//'
    
    # 显示内存使用
    echo ""
    echo "内存使用:"
    ps -o rss= -p "${PID}" | awk '{printf "%.2f MB\n", $1/1024}'
    
    # 显示最近的日志
    if [ -f "${LOG_FILE}" ]; then
        echo ""
        echo "最近日志 (最后 10 行):"
        echo "----------------------------------------"
        tail -n 10 "${LOG_FILE}"
    fi
else
    echo "状态: ✗ 未运行"
    echo "PID 文件存在但进程不存在 (PID: ${PID})"
    echo "建议运行: rm -f ${PID_FILE}"
fi

echo ""
echo "=========================================="
echo "日志文件: ${LOG_FILE}"
echo "查看完整日志: tail -f ${LOG_FILE}"
echo "=========================================="

