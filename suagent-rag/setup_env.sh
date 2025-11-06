#!/bin/bash

# 环境初始化脚本
# 创建 conda 环境并安装依赖

# 设置工作目录为脚本所在目录
cd "$(dirname "$0")"

# 配置变量
CONDA_ENV_NAME="suagent-rag"
PYTHON_VERSION="3.13"

echo "=========================================="
echo "  SuAgent-RAG 环境初始化"
echo "=========================================="
echo ""

# 检查 conda 是否可用
if ! command -v conda &> /dev/null; then
    echo "✗ 错误: 未找到 conda 命令"
    echo "请先安装 Miniconda 或 Anaconda"
    exit 1
fi

echo "✓ 检测到 conda: $(which conda)"
echo ""

# 初始化 conda（确保 conda activate 命令可用）
echo "初始化 conda..."
eval "$(conda shell.bash hook)"

# 检查环境是否已存在
if conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    echo "⚠ conda 环境 '${CONDA_ENV_NAME}' 已存在"
    read -p "是否删除并重新创建？(y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除现有环境..."
        conda deactivate 2>/dev/null || true
        conda env remove -n "${CONDA_ENV_NAME}" -y
    else
        echo "跳过环境创建，直接安装依赖..."
        conda activate "${CONDA_ENV_NAME}"
        pip install -r requirements.txt
        echo ""
        echo "=========================================="
        echo "✓ 依赖安装完成！"
        echo "=========================================="
        exit 0
    fi
fi

# 创建新的 conda 环境
echo "创建 conda 环境: ${CONDA_ENV_NAME} (Python ${PYTHON_VERSION})..."
conda create -n "${CONDA_ENV_NAME}" python="${PYTHON_VERSION}" -y

if [ $? -ne 0 ]; then
    echo "✗ conda 环境创建失败"
    exit 1
fi

echo "✓ conda 环境创建成功"
echo ""

# 激活环境
echo "激活 conda 环境..."
conda activate "${CONDA_ENV_NAME}"

if [ $? -ne 0 ]; then
    echo "✗ 激活环境失败"
    exit 1
fi

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "安装项目依赖 (requirements.txt)..."
echo "这可能需要几分钟时间，请耐心等待..."
echo ""

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ 依赖安装失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ 环境初始化完成！"
echo "=========================================="
echo ""
echo "conda 环境名称: ${CONDA_ENV_NAME}"
echo "Python 版本: $(python --version)"
echo ""
echo "手动激活环境命令:"
echo "  conda activate ${CONDA_ENV_NAME}"
echo ""
echo "启动服务:"
echo "  ./start.sh"
echo ""
echo "=========================================="

