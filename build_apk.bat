@echo off
chcp 65001 >nul
echo ==========================================
echo 全能播放器 - APK打包脚本
echo ==========================================
echo.
echo 注意：需要安装 WSL (Windows Subsystem for Linux)
echo.

:: 检查WSL是否安装
wsl --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装 WSL
    echo 请先安装 WSL: https://docs.microsoft.com/zh-cn/windows/wsl/install
    pause
    exit /b 1
)

echo [1/5] 正在复制文件到WSL...

:: 获取当前目录
set "CURRENT_DIR=%CD%"
set "PROJECT_NAME=videoplayer"

:: 在WSL中创建项目目录
wsl bash -c "mkdir -p ~/buildozer_projects/%PROJECT_NAME%"

:: 复制必要文件到WSL
xcopy /Y "main.py" "\\wsl$\Ubuntu\home\%USERNAME%\buildozer_projects\%PROJECT_NAME%\" >nul
xcopy /Y "buildozer.spec" "\\wsl$\Ubuntu\home\%USERNAME%\buildozer_projects\%PROJECT_NAME%\" >nul

echo [2/5] 正在安装buildozer (如果未安装)...

wsl bash -c "
cd ~/buildozer_projects/%PROJECT_NAME%

# 安装依赖
sudo apt-get update -qq
sudo apt-get install -y -qq python3-pip python3-venv git zip unzip openjdk-17-jdk

# 安装buildozer
pip3 install --user buildozer cython

# 添加local bin到PATH
export PATH=\$HOME/.local/bin:\$PATH

echo '[3/5] 正在初始化buildozer...'

# 如果.buildozer不存在，初始化
if [ ! -d .buildozer ]; then
    buildozer init 2>/dev/null || true
fi

echo '[4/5] 开始构建APK (这可能需要20-30分钟，首次构建需要下载Android SDK)...'
echo '请耐心等待...'

# 构建debug APK
buildozer android debug 2>&1 | tee build.log

if [ -f bin/*.apk ]; then
    echo '[5/5] APK构建成功!'
    ls -lh bin/*.apk
else
    echo '[错误] 构建失败，请查看 build.log'
    exit 1
fi
"

if errorlevel 1 (
    echo.
    echo [错误] 构建失败
    echo 请检查WSL中的错误信息
    pause
    exit /b 1
)

echo.
echo [5/5] 正在复制APK到Windows...

:: 复制生成的APK回Windows
wsl bash -c "cp ~/buildozer_projects/%PROJECT_NAME%/bin/*.apk /mnt/c/Users/%USERNAME%/Desktop/全能播放器/" 2>nul

echo.
echo ==========================================
echo APK打包完成!
echo 文件位置: %CD%\*.apk
echo ==========================================
pause
