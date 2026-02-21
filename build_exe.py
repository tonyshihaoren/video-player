#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包Windows版全能播放器为exe
"""

import PyInstaller.__main__
import os
import sys

def build():
    print("=" * 50)
    print("🎬 全能播放器 - Windows EXE打包")
    print("=" * 50)

    # 检查PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
    except ImportError:
        print("❌ 需要安装PyInstaller")
        print("运行: pip install pyinstaller")
        sys.exit(1)

    # 打包参数
    args = [
        'windows_player.py',
        '--name=全能播放器',
        '--onefile',
        '--windowed',
        '--icon=NONE',
        '--add-data=README.md;.',
        '--clean',
        '--noconfirm',
        # 隐藏控制台
        '--console' if '--debug' in sys.argv else '--noconsole',
    ]

    print("\n📦 开始打包...")
    print("这可能需要几分钟时间...\n")

    PyInstaller.__main__.run(args)

    print("\n" + "=" * 50)
    print("✅ 打包完成!")
    print("=" * 50)
    print("\n📁 输出文件:")
    print("  dist/全能播放器.exe")
    print("\n🚀 使用方法:")
    print("  双击 '全能播放器.exe' 即可运行")
    print("=" * 50)

if __name__ == '__main__':
    build()
