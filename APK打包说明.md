# 全能播放器 - APK打包说明

## 📱 打包方式选择

### 方式一：使用 WSL (推荐，Windows 10/11)

#### 步骤1: 安装 WSL
```powershell
# 以管理员身份运行 PowerShell
wsl --install
```
安装完成后重启电脑，然后设置 Ubuntu 用户名密码。

#### 步骤2: 运行打包脚本
```bash
# 在 WSL 终端中
cd /mnt/c/Users/Administrator/Desktop/全能播放器/
bash build_apk.sh
```

或者直接在 Windows 中双击 `build_apk.bat`（需要已安装WSL）

---

### 方式二：使用 Docker

#### 步骤1: 安装 Docker Desktop
下载安装: https://www.docker.com/products/docker-desktop

#### 步骤2: 运行打包容器
```bash
# 在项目目录打开 PowerShell
docker run -it --rm \
  -v "${PWD}:/home/user/hostcwd" \
  -v "${PWD}/.buildozer:/home/user/.buildozer" \
  kivy/buildozer

# 在容器内执行
cd /home/user/hostcwd
buildozer android debug
```

---

### 方式三：使用 Linux 虚拟机/服务器

#### 步骤1: 准备 Ubuntu 20.04+
```bash
# 安装依赖
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv git zip unzip openjdk-17-jdk
```

#### 步骤2: 上传文件并打包
```bash
# 上传 main.py 和 buildozer.spec 到服务器
# 然后执行:
cd /path/to/project
bash build_apk.sh
```

---

## ⚠️ 重要提示

### 首次构建
- **耗时**: 首次构建需要下载 Android SDK、NDK，约 **20-40分钟**
- **空间**: 需要约 **10GB** 磁盘空间
- **网络**: 需要稳定的网络连接（下载Google仓库）

### 常见错误及解决

#### 1. Java版本错误
```bash
# 安装OpenJDK 17
sudo apt-get install openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

#### 2. 内存不足
```bash
# 增加交换空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 3. 网络超时（中国大陆）
在 `buildozer.spec` 中修改：
```
android.gradle_dependencies = \
    com.android.support:support-compat:28.0.0

# 使用国内镜像
p4a.url = https://gitee.com/mirrors/python-for-android.git
```

#### 4. 权限错误
```bash
# 确保文件权限正确
chmod +x build_apk.sh
```

---

## 📦 打包后的文件

打包完成后，APK文件位于：
```
bin/videoplayer-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

安装到手机：
```bash
# 通过adb安装
adb install bin/*.apk

# 或者复制到手机，在文件管理器中点击安装
```

---

## 🔧 自定义配置

### 修改应用名称
编辑 `buildozer.spec`：
```
title = 你的应用名称
```

### 修改包名
```
package.name = yourapp
package.domain = com.yourcompany
```

### 添加图标
1. 准备图标文件 `icon.png` (512x512)
2. 放在项目目录
3. 在 `buildozer.spec` 中：
```
icon.filename = %(source.dir)s/icon.png
```

### 修改权限
```
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WAKE_LOCK
```

---

## 🚀 发布版本

### 生成发布版APK
```bash
# 修改版本号
# 编辑 buildozer.spec:
# version = 1.0.0

# 构建发布版
buildozer android release
```

### 签名APK（发布到应用商店需要）
```bash
# 生成密钥
keytool -genkey -v -keystore my.keystore -alias myalias -keyalg RSA -keysize 2048 -validity 10000

# 签名APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my.keystore bin/*.apk myalias
```

---

## 📞 问题排查

如果打包失败，检查：
1. 查看详细日志: `buildozer android debug 2>&1 | tee build.log`
2. 确保所有依赖已安装
3. 检查 `.buildozer` 目录权限
4. 清除缓存重试: `buildozer android clean`

---

## 📱 安装后的权限设置

首次安装后，需要在手机设置中：
1. 允许安装未知来源应用
2. 授予文件读取权限（用于选择视频）
3. 允许存储权限（用于保存截图等）

---

**制作日期**: 2026-02-21
