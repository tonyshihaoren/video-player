#!/bin/bash
# 全能播放器 APK 打包脚本 (Linux/WSL)

set -e

echo "=========================================="
echo "全能播放器 - APK打包脚本"
echo "=========================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "[1/5] 检查依赖..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未安装 Python3"
    echo "请安装: sudo apt-get install python3 python3-pip"
    exit 1
fi

# 安装系统依赖
echo "[2/5] 安装系统依赖..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3-pip \
    python3-venv \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    automake

echo "[3/5] 安装buildozer..."

# 创建虚拟环境
if [ ! -d "venv_build" ]; then
    python3 -m venv venv_build
fi

source venv_build/bin/activate

# 安装buildozer
pip install -q buildozer cython

echo "[4/5] 开始构建APK..."
echo "注意: 首次构建需要下载Android SDK，可能需要20-40分钟"
echo ""

# 构建APK
buildozer android debug

if [ -f bin/*.apk ]; then
    echo ""
    echo "=========================================="
    echo "[5/5] APK构建成功!"
    echo "=========================================="
    echo ""
    ls -lh bin/*.apk
    echo ""
    echo "安装到手机:"
    echo "  adb install bin/*.apk"
    echo ""
    echo "或者将 bin/*.apk 复制到手机安装"
else
    echo "[错误] 构建失败"
    exit 1
fi
