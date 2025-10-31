#!/bin/bash

# 启动所有服务（PostgreSQL + Redis + API）

set -e

echo "================================"
echo "启动 Fenq Super Agent 服务"
echo "================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 启动 Docker 容器
echo "启动 PostgreSQL 和 Redis..."
docker-compose up -d

echo "等待服务就绪..."
sleep 5

# 检查服务状态
echo ""
echo "检查服务状态..."
docker-compose ps

echo ""
echo "✅ 后端服务已启动"
echo ""

# 激活虚拟环境
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 启动 API 服务
echo "启动 API 服务..."
echo ""
python main.py

