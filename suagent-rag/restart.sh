#!/bin/bash

# 重启服务脚本

# 设置工作目录为脚本所在目录
cd "$(dirname "$0")"

echo "重启服务..."
echo ""

# 停止服务
if [ -f "logs/suagent-rag.pid" ]; then
    ./stop.sh
    echo ""
    echo "等待 2 秒..."
    sleep 2
fi

# 启动服务
./start.sh

