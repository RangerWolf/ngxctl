#!/bin/bash

# 确保脚本在项目根目录下运行
if [ ! -f "setup.py" ]; then
    echo "Error: setup.py not found. Please run this script in the project's root directory."
    exit 1
fi

# 确保使用 Python 3 和 pip3
PYTHON_CMD="python3"
PIP_CMD="pip3"

# 设置 PyPI 镜像源
# 通过访问baidu检测是否在中国大陆，超时时间=1s
if curl -s --max-time 1 https://www.baidu.com > /dev/null; then
    # 大陆环境
    echo "Using Tencent Cloud PyPI mirror for China..."
    PIP_ARGS="--index-url https://mirrors.cloud.tencent.com/pypi/simple --trusted-host mirrors.cloud.tencent.com"
else
    # 海外环境
    echo "Using default PyPI mirror..."
    PIP_ARGS=""
fi

# 安装或升级 setuptools 和 wheel
echo "Installing/upgrading setuptools and wheel..."
$PIP_CMD install $PIP_ARGS --upgrade setuptools wheel

# 创建源分发包和轮子分发包
echo "Creating source distribution and wheel distribution..."
$PYTHON_CMD setup.py sdist bdist_wheel

# 安装到 Python 环境中（开发模式）
echo "Installing the project in development mode..."
$PIP_CMD install $PIP_ARGS -e .

# 验证安装（可选）
echo "Verifying installation..."
if command -v ngxctl &> /dev/null; then
    echo "Installation successful. 'ngxctl' command is available."
    ngxctl --help
else
    echo "Installation failed or 'ngxctl' command is not found."
    exit 1
fi

echo "Script completed."
