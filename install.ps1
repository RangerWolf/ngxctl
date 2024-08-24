# 确保脚本在项目根目录下运行
if (-not (Test-Path "setup.py")) {
    Write-Host "Error: setup.py not found. Please run this script in the project's root directory."
    exit 1
}

# 确保使用 Python 3 和 pip3
$PYTHON_CMD = "python"
$PIP_CMD = "pip"

# 设置 PyPI 镜像源
# 检测是否在中国大陆
$timeout = 1
try {
    $response = Invoke-WebRequest -Uri "https://www.baidu.com" -TimeoutSec $timeout -UseBasicP
    if ($response.StatusCode -eq 200) {
        # 大陆环境
        Write-Host "Using Tencent Cloud PyPI mirror for China..."
        $PIP_ARGS = "--index-url https://mirrors.cloud.tencent.com/pypi/simple --trusted-host mirrors.cloud.tencent.com"
    }
} catch {
    # 海外环境
    Write-Host "Using default PyPI mirror..."
    $PIP_ARGS = ""
}

# 安装或升级 setuptools 和 wheel
Write-Host "Installing/upgrading setuptools and wheel..."
& $PIP_CMD install $PIP_ARGS --upgrade setuptools wheel

# 创建源分发包和轮子分发包
Write-Host "Creating source distribution and wheel distribution..."
& $PYTHON_CMD setup.py sdist bdist_wheel

# 安装到 Python 环境中（开发模式）
Write-Host "Installing the project in development mode..."
& $PIP_CMD install $PIP_ARGS -e .

# 验证安装（可选）
Write-Host "Verifying installation..."
if (Get-Command ngxctl -ErrorAction SilentlyContinue) {
    Write-Host "Installation successful. 'ngxctl' command is available."
    & ngxctl --help
} else {
    Write-Host "Installation failed or 'ngxctl' command is not found."
    exit 1
}

Write-Host "Script completed."
