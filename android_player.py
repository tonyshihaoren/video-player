
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全能播放器 - Android版 (Kivy)
功能：视频/音频播放、AB点循环、慢进/快进
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.video import Video
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.utils import platform
import os


class ABLoopController:
    """AB循环控制器"""
    def __init__(self):
        self.point_a = None
        self.point_b = None
        self.is_a_set = False
        self.is_b_set = False
        self.enabled = False

    def set_a(self, position):
        self.point_a = position
        self.is_a_set = True
        return True

    def set_b(self, position):
        if self.point_a is not None and position > self.point_a:
            self.point_b = position
            self.is_b_set = True
            self.enabled = True
            return True
        return False

    def reset(self):
        self.point_a = None
        self.point_b = None
        self.is_a_set = False
        self.is_b_set = False
        self.enabled = False

    def check_loop(self, current_position):
        """检查是否需要循环"""
        if self.enabled and self.is_b_set and self.point_b is not None:
            if current_position >= self.point_b:
                return self.point_a
        return None

    @staticmethod
    def format_time(seconds):
        """格式化时间显示"""
        if seconds < 0:
            return "00:00"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        hours = minutes // 60
        minutes = minutes % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"


class PlayerLayout(BoxLayout):
    """播放器主布局"""

    current_file = StringProperty("")
    is_playing = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        # AB循环控制器
        self.ab_controller = ABLoopController()

        # 创建UI
        self.create_ui()

        # 定时器更新
        Clock.schedule_interval(self.update_progress, 0.1)

    def create_ui(self):
        # 标题
        title_label = Label(
            text='全能播放器',
            font_size='24sp',
            size_hint_y=None,
            height=50,
            color=(0.2, 0.6, 0.2, 1)
        )
        self.add_widget(title_label)

        # 视频显示区域
        self.video = Video(
            allow_stretch=True,
            size_hint_y=0.5
        )
        self.video.bind(position=self.on_position_change)
        self.video.bind(duration=self.on_duration_change)
        self.add_widget(self.video)

        # 文件信息
        self.file_label = Label(
            text='未选择文件',
            font_size='14sp',
            size_hint_y=None,
            height=30,
            color=(0.5, 0.5, 0.5, 1)
        )
        self.add_widget(self.file_label)

        # 时间显示
        self.time_label = Label(
            text='00:00 / 00:00',
            font_size='16sp',
            size_hint_y=None,
            height=40,
            font_name='monospace'
        )
        self.add_widget(self.time_label)

        # 进度条
        self.progress_slider = Slider(
            min=0,
            max=100,
            value=0,
            size_hint_y=None,
            height=50
        )
        self.progress_slider.bind(value=self.on_slider_change)
        self.add_widget(self.progress_slider)

        # 播放控制按钮
        control_layout = GridLayout(
            cols=4,
            size_hint_y=None,
            height=60,
            spacing=5
        )

        self.open_btn = Button(
            text='📂 打开',
            font_size='16sp',
            background_color=(0.13, 0.59, 0.95, 1)
        )
        self.open_btn.bind(on_press=self.show_file_chooser)
        control_layout.add_widget(self.open_btn)

        self.play_btn = Button(
            text='▶️ 播放',
            font_size='16sp',
            background_color=(0.3, 0.69, 0.31, 1)
        )
        self.play_btn.bind(on_press=self.play_pause)
        control_layout.add_widget(self.play_btn)

        self.stop_btn = Button(
            text='⏹️ 停止',
            font_size='16sp',
            background_color=(0.96, 0.26, 0.21, 1)
        )
        self.stop_btn.bind(on_press=self.stop)
        control_layout.add_widget(self.stop_btn)

        self.loop_btn = Button(
            text='🔁 循环',
            font_size='16sp',
            background_color=(1, 0.6, 0, 1)
        )
        self.loop_btn.bind(on_press=self.toggle_loop)
        control_layout.add_widget(self.loop_btn)

        self.add_widget(control_layout)

        # AB点控制
        ab_layout = GridLayout(
            cols=3,
            size_hint_y=None,
            height=60,
            spacing=5
        )

        self.set_a_btn = Button(
            text='设置A点',
            font_size='16sp',
            background_color=(0.3, 0.69, 0.31, 1)
        )
        self.set_a_btn.bind(on_press=self.set_point_a)
        ab_layout.add_widget(self.set_a_btn)

        self.set_b_btn = Button(
            text='设置B点',
            font_size='16sp',
            background_color=(0.96, 0.26, 0.21, 1)
        )
        self.set_b_btn.bind(on_press=self.set_point_b)
        ab_layout.add_widget(self.set_b_btn)

        self.clear_ab_btn = Button(
            text='清除AB',
            font_size='16sp',
            background_color=(0.46, 0.46, 0.46, 1)
        )
        self.clear_ab_btn.bind(on_press=self.clear_ab)
        ab_layout.add_widget(self.clear_ab_btn)

        self.add_widget(ab_layout)

        # AB状态显示
        self.ab_status_label = Label(
            text='AB循环: 未设置',
            font_size='14sp',
            size_hint_y=None,
            height=30,
            color=(0.3, 0.69, 0.31, 1)
        )
        self.add_widget(self.ab_status_label)

        # 速度控制
        speed_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            spacing=5
        )

        speed_label = Label(
            text='播放速度:',
            font_size='14sp',
            size_hint_x=None,
            width=100
        )
        speed_layout.add_widget(speed_label)

        self.speed_slider = Slider(
            min=0.1,
            max=3.0,
            value=1.0,
            step=0.1
        )
        self.speed_slider.bind(value=self.on_speed_change)
        speed_layout.add_widget(self.speed_slider)

        self.speed_label = Label(
            text='1.0x',
            font_size='14sp',
            size_hint_x=None,
            width=60
        )
        speed_layout.add_widget(self.speed_label)

        self.add_widget(speed_layout)

        # 快捷速度按钮
        quick_speed_layout = GridLayout(
            cols=4,
            size_hint_y=None,
            height=50,
            spacing=5
        )

        speeds = [
            ('慢进0.5x', 0.5),
            ('正常1.0x', 1.0),
            ('快进1.5x', 1.5),
            ('倍速2.0x', 2.0)
        ]

        for name, value in speeds:
            btn = Button(
                text=name,
                font_size='12sp',
                background_color=(1, 0.6, 0, 1)
            )
            btn.bind(on_press=lambda inst, v=value: self.set_speed(v))
            quick_speed_layout.add_widget(btn)

        self.add_widget(quick_speed_layout)

        # 快进/快退按钮
        skip_layout = GridLayout(
            cols=2,
            size_hint_y=None,
            height=50,
            spacing=5
        )

        self.back_btn = Button(
            text='⏪ 后退5秒',
            font_size='14sp',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        self.back_btn.bind(on_press=lambda x: self.skip(-5))
        skip_layout.add_widget(self.back_btn)

        self.forward_btn = Button(
            text='前进5秒 ⏩',
            font_size='14sp',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        self.forward_btn.bind(on_press=lambda x: self.skip(5))
        skip_layout.add_widget(self.forward_btn)

        self.add_widget(skip_layout)

    def show_file_chooser(self, instance):
        """显示文件选择器"""
        content = BoxLayout(orientation='vertical')

        filechooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.mp4', '*.avi', '*.mkv', '*.mov', '*.mp3', '*.wav', '*.flac']
        )
        content.add_widget(filechooser)

        btn_layout = BoxLayout(size_hint_y=None, height=50)

        select_btn = Button(text='选择')
        cancel_btn = Button(text='取消')

        popup = Popup(title='选择媒体文件', content=content, size_hint=(0.9, 0.9))

        def on_select(instance):
            if filechooser.selection:
                self.load_file(filechooser.selection[0])
                popup.dismiss()

        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup.open()

    def load_file(self, filepath):
        """加载文件"""
        if filepath and os.path.exists(filepath):
            self.current_file = filepath
            self.video.source = filepath
            self.file_label.text = f'📁 {os.path.basename(filepath)}'
            self.ab_controller.reset()
            self.update_ab_status()

    def play_pause(self, instance):
        """播放/暂停"""
        if self.is_playing:
            self.video.state = 'pause'
            self.play_btn.text = '▶️ 播放'
            self.is_playing = False
        else:
            self.video.state = 'play'
            self.play_btn.text = '⏸️ 暂停'
            self.is_playing = True

    def stop(self, instance):
        """停止"""
        self.video.state = 'stop'
        self.play_btn.text = '▶️ 播放'
        self.is_playing = False
        self.progress_slider.value = 0

    def toggle_loop(self, instance):
        """切换循环播放"""
        if hasattr(self.video, 'loop') and self.video.loop:
            self.video.loop = False
            self.loop_btn.text = '🔁 循环'
            self.loop_btn.background_color = (1, 0.6, 0, 1)
        else:
            self.video.loop = True
            self.loop_btn.text = '✓ 循环'
            self.loop_btn.background_color = (0.3, 0.69, 0.31, 1)

    def set_point_a(self, instance):
        """设置A点"""
        if self.video.loaded:
            position = self.video.position
            self.ab_controller.set_a(position)
            self.update_ab_status()
            self.set_a_btn.text = f'A: {self.ab_controller.format_time(position)}'

    def set_point_b(self, instance):
        """设置B点"""
        if self.video.loaded and self.ab_controller.is_a_set:
            position = self.video.position
            if self.ab_controller.set_b(position):
                self.update_ab_status()
                self.set_b_btn.text = f'B: {self.ab_controller.format_time(position)}'

    def clear_ab(self, instance):
        """清除AB点"""
        self.ab_controller.reset()
        self.set_a_btn.text = '设置A点'
        self.set_b_btn.text = '设置B点'
        self.update_ab_status()

    def update_ab_status(self):
        """更新AB状态显示"""
        if not self.ab_controller.is_a_set:
            self.ab_status_label.text = 'AB循环: 未设置'
            self.ab_status_label.color = (0.5, 0.5, 0.5, 1)
        elif not self.ab_controller.is_b_set:
            a_time = self.ab_controller.format_time(self.ab_controller.point_a)
            self.ab_status_label.text = f'AB循环: A点={a_time}, 请设置B点'
            self.ab_status_label.color = (1, 0.6, 0, 1)
        else:
            a_time = self.ab_controller.format_time(self.ab_controller.point_a)
            b_time = self.ab_controller.format_time(self.ab_controller.point_b)
            self.ab_status_label.text = f'AB循环: {a_time} - {b_time} ✓'
            self.ab_status_label.color = (0.3, 0.69, 0.31, 1)

    def on_position_change(self, instance, value):
        """位置变化回调"""
        if self.video.duration > 0:
            self.progress_slider.value = (value / self.video.duration) * 100

        # 检查AB循环
        if self.ab_controller.enabled:
            loop_pos = self.ab_controller.check_loop(value)
            if loop_pos is not None:
                self.video.seek(loop_pos)

        self.update_time_label()

    def on_duration_change(self, instance, value):
        """时长变化回调"""
        self.update_time_label()

    def update_time_label(self):
        """更新时间标签"""
        current = self.video.position if self.video.loaded else 0
        duration = self.video.duration if self.video.loaded else 0
        self.time_label.text = (
            f'{self.ab_controller.format_time(current)} / '
            f'{self.ab_controller.format_time(duration)}'
        )

    def on_slider_change(self, instance, value):
        """进度条拖动"""
        if self.video.loaded and self.video.duration > 0:
            position = (value / 100) * self.video.duration
            self.video.seek(position)

    def on_speed_change(self, instance, value):
        """速度变化"""
        self.speed_label.text = f'{value:.1f}x'
        # Kivy Video不支持直接设置播放速度，需要其他方式

    def set_speed(self, speed):
        """设置播放速度"""
        self.speed_slider.value = speed
        # 注意：Kivy的Video组件原生不支持速度控制
        # 实际Android版本可能需要使用其他播放器库

    def skip(self, seconds):
        """快进/快退"""
        if self.video.loaded:
            new_pos = self.video.position + seconds
            new_pos = max(0, min(new_pos, self.video.duration))
            self.video.seek(new_pos)

    def update_progress(self, dt):
        """定时更新进度"""
        if self.is_playing:
            self.update_time_label()


class VideoPlayerApp(App):
    """Kivy应用主类"""

    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        return PlayerLayout()


def main():
    """主函数"""
    # 设置窗口大小（模拟手机屏幕）
    Window.size = (400, 700)

    app = VideoPlayerApp()
    app.run()


if __name__ == '__main__':
    main()
