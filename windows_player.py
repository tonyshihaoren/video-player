#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全能播放器 - Windows版
功能：视频/音频播放、AB点循环、慢进/快进、截图
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QSlider, QLabel,
                             QFileDialog, QStyle, QFrame, QSpinBox,
                             QDoubleSpinBox, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal, QSize
from PyQt6.QtGui import QKeySequence, QFont, QIcon, QDragEnterEvent, QDropEvent, QShortcut
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget


class ABLoopButton(QPushButton):
    """AB点循环按钮"""
    def __init__(self, parent=None):
        super().__init__("设置A点", parent)
        self.setCheckable(True)
        self.point_a = None
        self.point_b = None
        self.is_a_set = False
        self.is_b_set = False
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:checked:hover {
                background-color: #da190b;
            }
        """)

    def reset(self):
        self.point_a = None
        self.point_b = None
        self.is_a_set = False
        self.is_b_set = False
        self.setChecked(False)
        self.setText("设置A点")

    def set_point_a(self, pos):
        self.point_a = pos
        self.is_a_set = True
        self.setText("设置B点")
        return True

    def set_point_b(self, pos):
        if self.point_a is not None and pos > self.point_a:
            self.point_b = pos
            self.is_b_set = True
            self.setChecked(True)
            self.setText(f"AB循环: {self.format_time(self.point_a)}-{self.format_time(self.point_b)}")
            return True
        return False

    @staticmethod
    def format_time(ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("全能播放器 - Windows版")
        self.setGeometry(100, 100, 1000, 700)
        self.setAcceptDrops(True)

        # 媒体播放器
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # 视频显示组件
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        # 初始化UI
        self.init_ui()
        self.init_shortcuts()

        # 定时器更新进度
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_position)
        self.timer.start()

        # AB循环状态
        self.ab_loop_enabled = False

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 视频显示区域
        self.video_widget.setStyleSheet("background-color: black;")
        self.video_widget.setMinimumSize(800, 450)
        layout.addWidget(self.video_widget, stretch=1)

        # 信息栏
        info_layout = QHBoxLayout()
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(self.file_label)
        info_layout.addStretch()

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("font-family: monospace; font-size: 14px;")
        info_layout.addWidget(self.time_label)
        layout.addLayout(info_layout)

        # 进度条
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #ddd;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        layout.addWidget(self.progress_slider)

        # 控制按钮区
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        # 打开文件按钮
        self.open_btn = QPushButton("📂 打开文件")
        self.open_btn.setStyleSheet(self.get_button_style("#2196F3"))
        self.open_btn.clicked.connect(self.open_file)
        controls_layout.addWidget(self.open_btn)

        controls_layout.addSpacing(20)

        # 播放控制按钮
        self.play_btn = QPushButton("▶️ 播放")
        self.play_btn.setStyleSheet(self.get_button_style("#4CAF50"))
        self.play_btn.clicked.connect(self.play_pause)
        controls_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setStyleSheet(self.get_button_style("#f44336"))
        self.stop_btn.clicked.connect(self.stop)
        controls_layout.addWidget(self.stop_btn)

        controls_layout.addSpacing(20)

        # AB循环按钮
        self.ab_btn = ABLoopButton()
        self.ab_btn.clicked.connect(self.toggle_ab_loop)
        controls_layout.addWidget(self.ab_btn)

        self.clear_ab_btn = QPushButton("清除AB点")
        self.clear_ab_btn.setStyleSheet(self.get_button_style("#757575"))
        self.clear_ab_btn.clicked.connect(self.clear_ab_loop)
        controls_layout.addWidget(self.clear_ab_btn)

        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # 高级控制区
        advanced_group = QGroupBox("高级控制")
        advanced_layout = QGridLayout(advanced_group)

        # 播放速度控制
        speed_label = QLabel("播放速度:")
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.1, 4.0)
        self.speed_spin.setValue(1.0)
        self.speed_spin.setSingleStep(0.1)
        self.speed_spin.setSuffix("x")
        self.speed_spin.valueChanged.connect(self.change_speed)
        self.speed_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 5px;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        advanced_layout.addWidget(speed_label, 0, 0)
        advanced_layout.addWidget(self.speed_spin, 0, 1)

        # 常用速度按钮
        speeds = [("慢进(0.5x)", 0.5), ("正常(1.0x)", 1.0), ("快进(1.5x)", 1.5), ("倍速(2.0x)", 2.0)]
        speed_btn_layout = QHBoxLayout()
        for name, value in speeds:
            btn = QPushButton(name)
            btn.setStyleSheet(self.get_button_style("#FF9800", small=True))
            btn.clicked.connect(lambda checked, v=value: self.set_speed(v))
            speed_btn_layout.addWidget(btn)
        advanced_layout.addLayout(speed_btn_layout, 0, 2, 1, 3)

        # 音量控制
        volume_label = QLabel("音量:")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)
        advanced_layout.addWidget(volume_label, 1, 0)
        advanced_layout.addWidget(self.volume_slider, 1, 1, 1, 4)

        # 截图按钮
        self.screenshot_btn = QPushButton("📷 截图")
        self.screenshot_btn.setStyleSheet(self.get_button_style("#9C27B0"))
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        advanced_layout.addWidget(self.screenshot_btn, 2, 0)

        # 全屏按钮
        self.fullscreen_btn = QPushButton("⛶ 全屏")
        self.fullscreen_btn.setStyleSheet(self.get_button_style("#607D8B"))
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        advanced_layout.addWidget(self.fullscreen_btn, 2, 1)

        layout.addWidget(advanced_group)

        # 状态栏
        self.statusBar().showMessage("就绪 - 支持拖拽文件到窗口播放")

        # 连接媒体播放器信号
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.playbackStateChanged.connect(self.state_changed)

    def get_button_style(self, color, small=False):
        padding = "6px 12px" if small else "8px 16px"
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: {padding};
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """

    def init_shortcuts(self):
        # 空格键：播放/暂停
        QShortcut(QKeySequence("Space"), self, self.play_pause)
        # ESC：退出全屏
        QShortcut(QKeySequence("Esc"), self, self.exit_fullscreen)
        # Ctrl+O：打开文件
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_file)
        # 方向键：快进/快退
        QShortcut(QKeySequence("Right"), self, lambda: self.skip(5000))
        QShortcut(QKeySequence("Left"), self, lambda: self.skip(-5000))
        # A键：设置A点
        QShortcut(QKeySequence("A"), self, lambda: self.set_ab_point('a'))
        # B键：设置B点
        QShortcut(QKeySequence("B"), self, lambda: self.set_ab_point('b'))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path:
                self.load_file(file_path)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择媒体文件", "",
            "媒体文件 (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.mp3 *.wav *.flac *.aac *.m4a);;"
            "视频文件 (*.mp4 *.avi *.mkv *.mov *.wmv *.flv);;"
            "音频文件 (*.mp3 *.wav *.flac *.aac *.m4a);;"
            "所有文件 (*.*)"
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.file_label.setText(f"📁 {os.path.basename(file_path)}")
        self.statusBar().showMessage(f"已加载: {file_path}")
        self.ab_btn.reset()
        self.ab_loop_enabled = False

    def play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_btn.setText("▶️ 播放")
        else:
            self.media_player.play()
            self.play_btn.setText("⏸️ 暂停")

    def stop(self):
        self.media_player.stop()
        self.play_btn.setText("▶️ 播放")
        self.progress_slider.setValue(0)

    def state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setText("⏸️ 暂停")
        else:
            self.play_btn.setText("▶️ 播放")

    def position_changed(self, position):
        self.progress_slider.setValue(position)
        self.update_time_label()

        # AB循环检查
        if self.ab_loop_enabled and self.ab_btn.is_b_set:
            if position >= self.ab_btn.point_b:
                self.media_player.setPosition(self.ab_btn.point_a)

    def duration_changed(self, duration):
        self.progress_slider.setRange(0, duration)
        self.update_time_label()

    def update_time_label(self):
        current = self.media_player.position()
        total = self.media_player.duration()
        self.time_label.setText(
            f"{self.format_time(current)} / {self.format_time(total)}"
        )

    def set_position(self, position):
        self.media_player.setPosition(position)

    def update_position(self):
        pass  # 由 positionChanged 信号处理

    def skip(self, milliseconds):
        new_position = self.media_player.position() + milliseconds
        new_position = max(0, min(new_position, self.media_player.duration()))
        self.media_player.setPosition(new_position)

    def change_speed(self, speed):
        self.media_player.setPlaybackRate(speed)

    def set_speed(self, speed):
        self.speed_spin.setValue(speed)
        self.change_speed(speed)

    def change_volume(self, volume):
        self.audio_output.setVolume(volume / 100)

    def toggle_ab_loop(self):
        if not self.ab_btn.is_a_set:
            self.set_ab_point('a')
        elif not self.ab_btn.is_b_set:
            self.set_ab_point('b')
        else:
            self.ab_loop_enabled = self.ab_btn.isChecked()
            if self.ab_loop_enabled:
                self.statusBar().showMessage(
                    f"AB循环已开启: {self.format_time(self.ab_btn.point_a)} - {self.format_time(self.ab_btn.point_b)}"
                )
                self.media_player.setPosition(self.ab_btn.point_a)
            else:
                self.statusBar().showMessage("AB循环已关闭")

    def set_ab_point(self, point):
        current_pos = self.media_player.position()
        if point == 'a':
            if self.ab_btn.set_point_a(current_pos):
                self.statusBar().showMessage(f"A点已设置: {self.format_time(current_pos)}")
        elif point == 'b':
            if self.ab_btn.set_point_b(current_pos):
                self.ab_loop_enabled = True
                self.statusBar().showMessage(
                    f"B点已设置: {self.format_time(current_pos)} - AB循环已启动"
                )

    def clear_ab_loop(self):
        self.ab_btn.reset()
        self.ab_loop_enabled = False
        self.statusBar().showMessage("AB点已清除")

    def take_screenshot(self):
        """截图功能"""
        from PyQt6.QtGui import QPixmap
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)

        # 截图视频区域
        pixmap = self.video_widget.grab()
        pixmap.save(filepath)

        self.statusBar().showMessage(f"截图已保存: {filepath}")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def exit_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()

    @staticmethod
    def format_time(ms):
        if ms < 0:
            return "00:00"
        seconds = ms // 1000
        minutes = seconds // 60
        hours = minutes // 60
        seconds = seconds % 60
        minutes = minutes % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 设置应用字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    player = VideoPlayer()
    player.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
