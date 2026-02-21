#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全能播放器 - Web版
手机浏览器访问电脑的 IP:5000 即可使用
支持AB循环、慢进/快进
"""

from flask import Flask, render_template_string, request, jsonify
import os
import urllib.parse

app = Flask(__name__)

# 支持的媒体格式
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma'}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>全能播放器 - Web版</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: #1a1a2e;
            color: #fff;
            min-height: 100vh;
            padding: 10px;
        }
        .header {
            text-align: center;
            padding: 15px 0;
            border-bottom: 1px solid #333;
            margin-bottom: 15px;
        }
        .header h1 {
            font-size: 20px;
            color: #4CAF50;
        }
        .header p {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
        .video-container {
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 15px;
            position: relative;
        }
        video, audio {
            width: 100%;
            display: block;
        }
        .controls {
            background: #16213e;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .progress-container {
            margin-bottom: 15px;
        }
        .time-display {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #888;
            margin-bottom: 5px;
        }
        input[type="range"] {
            width: 100%;
            height: 6px;
            background: #333;
            border-radius: 3px;
            outline: none;
            -webkit-appearance: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            background: #4CAF50;
            border-radius: 50%;
            cursor: pointer;
        }
        .btn-row {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        button {
            flex: 1;
            min-width: 60px;
            padding: 12px 8px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-green {
            background: #4CAF50;
            color: white;
        }
        .btn-green:hover {
            background: #45a049;
        }
        .btn-red {
            background: #f44336;
            color: white;
        }
        .btn-red:hover {
            background: #da190b;
        }
        .btn-orange {
            background: #FF9800;
            color: white;
        }
        .btn-orange:hover {
            background: #e68900;
        }
        .btn-gray {
            background: #607D8B;
            color: white;
        }
        .btn-gray:hover {
            background: #546E7A;
        }
        .speed-control {
            background: #0f3460;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .speed-control h3 {
            font-size: 14px;
            margin-bottom: 10px;
            color: #4CAF50;
        }
        .speed-buttons {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .speed-btn {
            flex: 1;
            min-width: 50px;
            padding: 8px;
            background: #1a1a2e;
            border: 1px solid #4CAF50;
            color: #4CAF50;
            border-radius: 5px;
        }
        .speed-btn.active {
            background: #4CAF50;
            color: white;
        }
        .ab-status {
            background: #0f3460;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        .ab-status h3 {
            font-size: 14px;
            margin-bottom: 10px;
        }
        .ab-status .status-text {
            font-size: 16px;
            font-weight: bold;
            color: #4CAF50;
        }
        .file-section {
            background: #16213e;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .file-section h3 {
            font-size: 14px;
            margin-bottom: 10px;
            color: #4CAF50;
        }
        select {
            width: 100%;
            padding: 10px;
            background: #0f3460;
            border: 1px solid #4CAF50;
            color: white;
            border-radius: 5px;
            font-size: 14px;
        }
        .help-text {
            background: #16213e;
            border-radius: 10px;
            padding: 15px;
            font-size: 12px;
            color: #888;
            line-height: 1.6;
        }
        .help-text h3 {
            color: #4CAF50;
            margin-bottom: 10px;
        }
        .loop-indicator {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(76, 175, 80, 0.9);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            font-weight: bold;
            display: none;
        }
        .loop-indicator.active {
            display: block;
        }
        @media (max-width: 480px) {
            button {
                font-size: 12px;
                padding: 10px 5px;
            }
            .speed-btn {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 全能播放器</h1>
        <p>支持AB循环 | 慢进/快进</p>
    </div>

    <div class="video-container">
        <div class="loop-indicator" id="loopIndicator">🔁 AB循环中</div>
        <video id="mediaPlayer" controls></video>
    </div>

    <div class="controls">
        <div class="progress-container">
            <div class="time-display">
                <span id="currentTime">00:00</span>
                <span id="duration">00:00</span>
            </div>
            <input type="range" id="progressBar" min="0" max="100" value="0" step="0.1">
        </div>

        <div class="btn-row">
            <button class="btn-green" onclick="setPointA()">设置A点</button>
            <button class="btn-red" onclick="setPointB()">设置B点</button>
            <button class="btn-gray" onclick="clearAB()">清除</button>
        </div>

        <div class="btn-row">
            <button class="btn-orange" onclick="skip(-5)">⏪ 5秒</button>
            <button class="btn-green" onclick="togglePlay()" id="playBtn">▶️ 播放</button>
            <button class="btn-orange" onclick="skip(5)">5秒 ⏩</button>
        </div>
    </div>

    <div class="speed-control">
        <h3>⚡ 播放速度</h3>
        <div class="speed-buttons">
            <button class="speed-btn" onclick="setSpeed(0.5)">0.5x</button>
            <button class="speed-btn active" onclick="setSpeed(1.0)">1.0x</button>
            <button class="speed-btn" onclick="setSpeed(1.5)">1.5x</button>
            <button class="speed-btn" onclick="setSpeed(2.0)">2.0x</button>
        </div>
    </div>

    <div class="file-section">
        <h3>📁 选择文件</h3>
        <select id="fileSelect" onchange="loadFile(this.value)">
            <option value="">-- 请选择媒体文件 --</option>
            {% for file in files %}
            <option value="{{ file }}">{{ file }}</option>
            {% endfor %}
        </select>
    </div>

    <div class="ab-status">
        <h3>🔁 AB循环状态</h3>
        <div class="status-text" id="abStatus">未设置</div>
    </div>

    <div class="help-text" style="margin-top: 15px;">
        <h3>📖 使用说明</h3>
        <p>1. 从下拉菜单选择视频/音频文件</p>
        <p>2. 播放到起点位置，点击"设置A点"</p>
        <p>3. 播放到终点位置，点击"设置B点"</p>
        <p>4. 自动开始AB循环播放</p>
        <p>5. 点击下方速度按钮调节播放速度</p>
    </div>

    <script>
        const player = document.getElementById('mediaPlayer');
        const progressBar = document.getElementById('progressBar');
        const currentTimeEl = document.getElementById('currentTime');
        const durationEl = document.getElementById('duration');
        const playBtn = document.getElementById('playBtn');
        const abStatus = document.getElementById('abStatus');
        const loopIndicator = document.getElementById('loopIndicator');

        let pointA = null;
        let pointB = null;
        let isLooping = false;

        // 格式化时间
        function formatTime(seconds) {
            if (isNaN(seconds)) return '00:00';
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }

        // 加载文件
        function loadFile(filename) {
            if (!filename) return;
            const encodedFile = encodeURIComponent(filename);
            player.src = `/media/${encodedFile}`;
            player.load();
            clearAB();
        }

        // 播放控制
        function togglePlay() {
            if (player.paused) {
                player.play();
                playBtn.textContent = '⏸️ 暂停';
            } else {
                player.pause();
                playBtn.textContent = '▶️ 播放';
            }
        }

        // 快进/快退
        function skip(seconds) {
            player.currentTime += seconds;
        }

        // 设置A点
        function setPointA() {
            pointA = player.currentTime;
            updateABStatus();
        }

        // 设置B点
        function setPointB() {
            if (pointA === null) {
                alert('请先设置A点！');
                return;
            }
            if (player.currentTime <= pointA) {
                alert('B点必须在A点之后！');
                return;
            }
            pointB = player.currentTime;
            isLooping = true;
            updateABStatus();
            loopIndicator.classList.add('active');
        }

        // 清除AB点
        function clearAB() {
            pointA = null;
            pointB = null;
            isLooping = false;
            updateABStatus();
            loopIndicator.classList.remove('active');
        }

        // 更新AB状态显示
        function updateABStatus() {
            if (pointA === null) {
                abStatus.textContent = '未设置';
                abStatus.style.color = '#888';
            } else if (pointB === null) {
                abStatus.textContent = `A点: ${formatTime(pointA)} | 请设置B点`;
                abStatus.style.color = '#FF9800';
            } else {
                abStatus.textContent = `循环: ${formatTime(pointA)} - ${formatTime(pointB)}`;
                abStatus.style.color = '#4CAF50';
            }
        }

        // 设置播放速度
        function setSpeed(speed) {
            player.playbackRate = speed;
            document.querySelectorAll('.speed-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent === speed + 'x') {
                    btn.classList.add('active');
                }
            });
        }

        // 监听播放进度
        player.addEventListener('timeupdate', () => {
            // 更新进度条
            const progress = (player.currentTime / player.duration) * 100;
            progressBar.value = progress || 0;
            currentTimeEl.textContent = formatTime(player.currentTime);
            durationEl.textContent = formatTime(player.duration);

            // AB循环检查
            if (isLooping && pointB !== null && player.currentTime >= pointB) {
                player.currentTime = pointA;
            }
        });

        // 进度条拖动
        progressBar.addEventListener('input', () => {
            const time = (progressBar.value / 100) * player.duration;
            player.currentTime = time;
        });

        // 播放状态监听
        player.addEventListener('play', () => {
            playBtn.textContent = '⏸️ 暂停';
        });

        player.addEventListener('pause', () => {
            playBtn.textContent = '▶️ 播放';
        });

        player.addEventListener('ended', () => {
            playBtn.textContent = '▶️ 播放';
        });

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                togglePlay();
            } else if (e.code === 'ArrowLeft') {
                skip(-5);
            } else if (e.code === 'ArrowRight') {
                skip(5);
            } else if (e.code === 'KeyA') {
                setPointA();
            } else if (e.code === 'KeyB') {
                setPointB();
            }
        });
    </script>
</body>
</html>
'''

def get_media_files(directory='.'):
    """获取目录下的所有媒体文件"""
    files = []
    for filename in os.listdir(directory):
        ext = os.path.splitext(filename)[1].lower()
        if ext in VIDEO_EXTENSIONS or ext in AUDIO_EXTENSIONS:
            files.append(filename)
    return sorted(files)

@app.route('/')
def index():
    files = get_media_files()
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/media/<path:filename>')
def serve_media(filename):
    """提供媒体文件"""
    decoded_filename = urllib.parse.unquote(filename)
    return app.send_static_file(decoded_filename)

def get_local_ip():
    """获取本地IP地址"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == '__main__':
    # 获取本地IP
    local_ip = get_local_ip()
    port = 5000

    print("=" * 50)
    print("🎬 全能播放器 - Web版")
    print("=" * 50)
    print(f"\n📱 电脑访问: http://localhost:{port}")
    print(f"📱 手机访问: http://{local_ip}:{port}")
    print("\n📖 使用说明:")
    print("   1. 将视频/音频文件放在此目录下")
    print("   2. 刷新页面即可选择文件播放")
    print("   3. 支持AB循环、慢进/快进")
    print("   4. 按空格键播放/暂停")
    print("\n⚠️  确保电脑和手机在同一WiFi网络下")
    print("=" * 50)

    # 创建静态文件目录
    if not os.path.exists('static'):
        os.makedirs('static')

    # 运行服务器（允许外部访问）
    app.run(host='0.0.0.0', port=port, debug=False)
