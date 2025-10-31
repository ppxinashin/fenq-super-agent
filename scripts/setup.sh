#!/bin/bash

# Fenq Super Agent 安装脚本

set -e

echo "================================"
echo "Fenq Super Agent 安装向导"
echo "================================"
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ 错误: 需要 Python >= 3.10，当前版本: $python_version"
    exit 1
fi

echo "✅ Python 版本检查通过: $python_version"
echo ""

# 创建虚拟环境
echo "创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "⚠️  虚拟环境已存在，跳过创建"
fi
echo ""

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip
echo ""

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt
echo "✅ 依赖安装完成"
echo ""

# 安装 Playwright 浏览器
echo "安装 Playwright 浏览器..."
playwright install chromium
echo "✅ Playwright 浏览器安装完成"
echo ""

# 创建 .env 文件
if [ ! -f ".env" ]; then
    echo "创建 .env 配置文件..."
    cp .env.example .env
    echo "✅ .env 文件已创建"
    echo ""
    echo "⚠️  请编辑 .env 文件，配置以下必需项："
    echo "   - OPENAI_API_KEY"
    echo "   - POSTGRES_* (如果使用 RAG)"
    echo "   - REDIS_* (如果使用记忆功能)"
else
    echo "⚠️  .env 文件已存在，跳过创建"
fi
echo ""

echo "================================"
echo "✅ 安装完成！"
echo "================================"
echo ""
echo "下一步："
echo "  1. 编辑 .env 文件配置 API Key"
echo "  2. 启动 PostgreSQL 和 Redis (可选):"
echo "     make docker-up"
echo "  3. 运行示例:"
echo "     python examples/simple_chat.py"
echo "  4. 启动 API 服务:"
echo "     python main.py"
echo ""

