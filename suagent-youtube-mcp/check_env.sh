#!/bin/bash

# 环境检查脚本
# 验证 conda 环境和依赖是否正确安装

# 设置工作目录为脚本所在目录
cd "$(dirname "$0")"

# 配置变量
CONDA_ENV_NAME="suagent-youtube-mcp"
PYTHON_VERSION="3.13"

echo "=========================================="
echo "  SuAgent-YouTube-MCP 环境检查"
echo "=========================================="
echo ""

# 检查 conda
echo "1. 检查 conda..."
if ! command -v conda &> /dev/null; then
    echo "   ✗ 未找到 conda 命令"
    echo ""
    echo "请先安装 Miniconda 或 Anaconda"
    exit 1
else
    echo "   ✓ conda 已安装: $(which conda)"
    echo "   版本: $(conda --version)"
fi
echo ""

# 初始化 conda
eval "$(conda shell.bash hook)"

# 检查 conda 环境
echo "2. 检查 conda 环境 '${CONDA_ENV_NAME}'..."
if ! conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    echo "   ✗ 环境不存在"
    echo ""
    echo "请运行以下命令创建环境:"
    echo "  ./setup_env.sh"
    exit 1
else
    echo "   ✓ 环境已创建"
fi
echo ""

# 激活环境并检查 Python 版本
echo "3. 检查 Python 版本..."
ACTUAL_PYTHON_VERSION=$(conda run -n "${CONDA_ENV_NAME}" python --version 2>&1 | awk '{print $2}')
echo "   当前版本: ${ACTUAL_PYTHON_VERSION}"
echo "   期望版本: ${PYTHON_VERSION}.x"

if [[ "${ACTUAL_PYTHON_VERSION}" == ${PYTHON_VERSION}.* ]]; then
    echo "   ✓ Python 版本正确"
else
    echo "   ⚠ Python 版本不匹配"
fi
echo ""

# 检查关键依赖包
echo "4. 检查关键依赖包..."
REQUIRED_PACKAGES=(
    "pydantic"
    "pydantic_settings"
    "mcp"
    "googleapiclient"
    "google.auth"
    "isodate"
    "uvicorn"
    "sse_starlette"
)

MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if conda run -n "${CONDA_ENV_NAME}" python -c "import ${package//-/_}" 2>/dev/null; then
        echo "   ✓ ${package}"
    else
        echo "   ✗ ${package} (未安装或无法导入)"
        MISSING_PACKAGES+=("${package}")
    fi
done

echo ""

if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    echo "=========================================="
    echo "✓ 环境检查通过！"
    echo "=========================================="
    echo ""
    echo "可以启动服务:"
    echo "  ./start.sh"
    echo ""
else
    echo "=========================================="
    echo "⚠ 发现 ${#MISSING_PACKAGES[@]} 个问题"
    echo "=========================================="
    echo ""
    echo "缺失的包: ${MISSING_PACKAGES[*]}"
    echo ""
    echo "建议重新安装依赖:"
    echo "  conda activate ${CONDA_ENV_NAME}"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "或重新初始化环境:"
    echo "  ./setup_env.sh"
    echo ""
    exit 1
fi

