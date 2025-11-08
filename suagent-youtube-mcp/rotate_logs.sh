#!/bin/bash

# 日志轮转脚本 - 防止日志文件过大
# 建议在 crontab 中定期运行此脚本
# 例如: 0 0 * * * /path/to/rotate_logs.sh

# 设置工作目录为脚本所在目录
cd "$(dirname "$0")"

# 配置变量
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/suagent-youtube-mcp.log"
MAX_SIZE_MB=100  # 当日志文件超过此大小时进行轮转
MAX_BACKUPS=10   # 保留的备份文件数量

# 检查日志文件是否存在
if [ ! -f "${LOG_FILE}" ]; then
    echo "日志文件不存在: ${LOG_FILE}"
    exit 0
fi

# 获取文件大小（MB）
FILE_SIZE=$(du -m "${LOG_FILE}" | cut -f1)

# 如果文件大小超过限制，进行轮转
if [ "${FILE_SIZE}" -gt "${MAX_SIZE_MB}" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日志文件大小: ${FILE_SIZE}MB，开始轮转..."
    
    # 删除最旧的备份
    if [ -f "${LOG_FILE}.${MAX_BACKUPS}" ]; then
        rm -f "${LOG_FILE}.${MAX_BACKUPS}"
    fi
    
    # 轮转备份文件
    for i in $(seq $((MAX_BACKUPS - 1)) -1 1); do
        if [ -f "${LOG_FILE}.${i}" ]; then
            mv "${LOG_FILE}.${i}" "${LOG_FILE}.$((i + 1))"
        fi
    done
    
    # 压缩并移动当前日志文件
    cp "${LOG_FILE}" "${LOG_FILE}.1"
    gzip "${LOG_FILE}.1"
    
    # 清空当前日志文件（保持文件打开）
    > "${LOG_FILE}"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日志轮转完成" >> "${LOG_FILE}"
    echo "日志轮转完成"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日志文件大小: ${FILE_SIZE}MB，无需轮转"
fi

