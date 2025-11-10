#!/bin/bash

# 后台运行脚本 - 启动 MinIO 事件监听器
# 所有输出将被重定向到日志文件

# 设置工作目录为脚本所在目录
cd "$(dirname "$0")"

# 配置变量
CONDA_ENV_NAME="suagent-rag"
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/suagent-rag.log"
PID_FILE="${LOG_DIR}/suagent-rag.pid"

# 创建日志目录（如果不存在）
mkdir -p "${LOG_DIR}"

# 初始化 conda
if ! command -v conda &> /dev/null; then
    echo "✗ 错误: 未找到 conda 命令"
    echo "请先安装 Miniconda 或 Anaconda"
    exit 1
fi

# 初始化 conda（确保 conda activate 命令可用）
eval "$(conda shell.bash hook)"

# 检查 conda 环境是否存在
if ! conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    echo "✗ 错误: conda 环境 '${CONDA_ENV_NAME}' 不存在"
    echo "请先运行: ./setup_env.sh"
    exit 1
fi

# 检查是否已经在运行
if [ -f "${PID_FILE}" ]; then
    OLD_PID=$(cat "${PID_FILE}")
    if ps -p "${OLD_PID}" > /dev/null 2>&1; then
        echo "程序已经在运行中 (PID: ${OLD_PID})"
        echo "如需重启，请先运行: ./stop.sh"
        exit 1
    else
        echo "清理旧的 PID 文件..."
        rm -f "${PID_FILE}"
    fi
fi

# 添加时间戳到日志
echo "===========================================" >> "${LOG_FILE}"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动服务..." >> "${LOG_FILE}"
echo "===========================================" >> "${LOG_FILE}"

# 获取 conda 环境的 Python 路径
CONDA_PYTHON=$(conda run -n "${CONDA_ENV_NAME}" which python)

if [ -z "${CONDA_PYTHON}" ]; then
    echo "✗ 错误: 无法获取 conda 环境中的 Python 路径"
    exit 1
fi

echo "使用 Python: ${CONDA_PYTHON}" >> "${LOG_FILE}"

# 启动 Python 程序并后台运行
# 使用 nohup 确保在终端关闭后继续运行
# 使用 conda run 确保在正确的环境中运行
# 将 stdout 和 stderr 都重定向到日志文件
nohup conda run --no-capture-output -n "${CONDA_ENV_NAME}" python main.py >> "${LOG_FILE}" 2>&1 &

# 保存进程 PID
PROCESS_PID=$!
echo "${PROCESS_PID}" > "${PID_FILE}"

# 等待一下确认程序启动
sleep 2

# 检查进程是否还在运行
if ps -p "${PROCESS_PID}" > /dev/null 2>&1; then
    echo "✓ 服务启动成功!"
    echo "  PID: ${PROCESS_PID}"
    echo "  日志文件: ${LOG_FILE}"
    echo ""
    echo "使用以下命令:"
    echo "  - 查看日志: tail -f ${LOG_FILE}"
else
    echo "✗ 服务启动失败，请查看日志文件: ${LOG_FILE}"
    rm -f "${PID_FILE}"
    exit 1
fi

