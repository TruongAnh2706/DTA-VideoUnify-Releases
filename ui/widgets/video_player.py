"""
DTA VideoUnify Pro - Interactive Video Preview Player Widget
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Features High-Performance PyQt6 Video Preview, Cyberpunk Audio Waveform VU Meter,
Auto Aspect Ratio Detection & User Preference Memory (16:9 vs 9:16).
"""

import os
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSlider, QFrame
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from ui.widgets.audio_meter import AudioWaveformMeter


class InteractiveVideoPlayer(QWidget):
    """
    Custom Interactive Preview Player Widget powered by PyQt6 QtMultimedia.
    Features Automatic Aspect Ratio Detection & Preference Memory (16:9 vs 9:16)
    and Cyberpunk Audio Waveform VU Meter.
    """

    prev_requested = pyqtSignal()
    next_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = ""
        self.is_portrait_mode = False
        self.user_aspect_preference = None

        self._init_ui()
        self._init_player()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(6)

        # Video Header Status & Aspect Ratio Selector Box
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(2, 2, 2, 2)

        self.header_label = QLabel("🎬 Chưa chọn tập phim để xem thử")
        self.header_label.setStyleSheet("color: #00F2FE; font-weight: 700; font-size: 13px; background: transparent;")

        # Aspect Ratio Switch Buttons
        self.btn_aspect_169 = QPushButton("🖥️ Ngang (16:9)")
        self.btn_aspect_169.setObjectName("AspectButton")
        self.btn_aspect_169.setProperty("active", "true")
        self.btn_aspect_169.clicked.connect(lambda: self._user_select_aspect_ratio(False))

        self.btn_aspect_916 = QPushButton("📱 Dọc (9:16)")
        self.btn_aspect_916.setObjectName("AspectButton")
        self.btn_aspect_916.setProperty("active", "false")
        self.btn_aspect_916.clicked.connect(lambda: self._user_select_aspect_ratio(True))

        header_layout.addWidget(self.header_label, stretch=1)
        header_layout.addWidget(self.btn_aspect_169)
        header_layout.addWidget(self.btn_aspect_916)
        main_layout.addLayout(header_layout)

        # Outer Video Display Container
        self.video_container = QFrame()
        self.video_container.setStyleSheet("background-color: #050608; border-radius: 10px; border: 1px solid #1F2638;")
        container_layout = QHBoxLayout(self.video_container)
        container_layout.setContentsMargins(6, 6, 6, 6)
        container_layout.setSpacing(8)

        # Inner Center Box for Video Widget
        self.video_wrapper = QWidget()
        video_wrapper_layout = QHBoxLayout(self.video_wrapper)
        video_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        video_wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Video Display Widget
        self.video_widget = QVideoWidget(self.video_wrapper)
        self.video_widget.setStyleSheet("background-color: #000000; border-radius: 8px;")
        self.video_widget.setMinimumSize(320, 180)
        video_wrapper_layout.addWidget(self.video_widget)

        # Audio Waveform VU Meter Bar
        self.audio_meter = AudioWaveformMeter()

        container_layout.addWidget(self.video_wrapper, stretch=1)
        container_layout.addWidget(self.audio_meter)

        main_layout.addWidget(self.video_container, stretch=1)

        # Controls Panel Frame
        controls_frame = QFrame()
        controls_frame.setStyleSheet("background-color: #131622; border: 1px solid #1F2638; border-radius: 10px; padding: 4px;")
        ctrl_layout = QVBoxLayout(controls_frame)
        ctrl_layout.setContentsMargins(8, 6, 8, 6)
        ctrl_layout.setSpacing(6)

        # Timeline Seek Bar + Time Label
        seek_layout = QHBoxLayout()
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.sliderMoved.connect(self._set_position)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: #A0AEC0; font-family: monospace; font-size: 12px; background: transparent;")

        seek_layout.addWidget(self.seek_slider, stretch=1)
        seek_layout.addWidget(self.time_label)
        ctrl_layout.addLayout(seek_layout)

        # Playback Buttons & Volume
        buttons_layout = QHBoxLayout()

        self.btn_prev = QPushButton("⏮ Tập trước")
        self.btn_prev.clicked.connect(self.prev_requested.emit)

        self.btn_play = QPushButton("▶ Phát")
        self.btn_play.setStyleSheet("background-color: #00F2FE; color: #0B0C10; font-weight: 800;")
        self.btn_play.clicked.connect(self._toggle_play)

        self.btn_stop = QPushButton("⏹ Dừng")
        self.btn_stop.clicked.connect(self._stop)

        self.btn_next = QPushButton("Tập tiếp ⏭")
        self.btn_next.clicked.connect(self.next_requested.emit)

        # Volume Controls
        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedWidth(36)
        self.btn_mute.clicked.connect(self._toggle_mute)

        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_slider.setFixedWidth(90)
        self.vol_slider.valueChanged.connect(self._set_volume)

        buttons_layout.addWidget(self.btn_prev)
        buttons_layout.addWidget(self.btn_play)
        buttons_layout.addWidget(self.btn_stop)
        buttons_layout.addWidget(self.btn_next)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_mute)
        buttons_layout.addWidget(self.vol_slider)

        ctrl_layout.addLayout(buttons_layout)
        main_layout.addWidget(controls_frame)

    def _init_player(self):
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)
        self.audio_output.setVolume(0.8)

        self.player.positionChanged.connect(self._position_changed)
        self.player.durationChanged.connect(self._duration_changed)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)

    def _user_select_aspect_ratio(self, portrait: bool):
        self.user_aspect_preference = portrait
        self._set_aspect_ratio(portrait)

    def auto_detect_aspect_ratio(self, width: int, height: int):
        if self.user_aspect_preference is not None:
            self._set_aspect_ratio(self.user_aspect_preference)
            return

        if width <= 0 or height <= 0:
            return

        is_portrait = (height > width)
        self._set_aspect_ratio(is_portrait)

    def _on_playback_state_changed(self, state):
        is_playing = (state == QMediaPlayer.PlaybackState.PlayingState)
        self.audio_meter.set_playing_state(is_playing)

    def _set_aspect_ratio(self, portrait: bool):
        self.is_portrait_mode = portrait

        self.btn_aspect_169.setProperty("active", "false" if portrait else "true")
        self.btn_aspect_916.setProperty("active", "true" if portrait else "false")
        self.btn_aspect_169.style().unpolish(self.btn_aspect_169)
        self.btn_aspect_169.style().polish(self.btn_aspect_169)
        self.btn_aspect_916.style().unpolish(self.btn_aspect_916)
        self.btn_aspect_916.style().polish(self.btn_aspect_916)

        if portrait:
            self.video_widget.setMaximumWidth(280)
            self.video_widget.setMinimumWidth(180)
        else:
            self.video_widget.setMaximumWidth(16777215)
            self.video_widget.setMinimumWidth(320)

        self.video_widget.updateGeometry()

    def load_media(self, file_path: str, title_display: str = ""):
        self.current_file = file_path
        if title_display:
            self.header_label.setText(f"🎬 Đang xem thử: {title_display}")
        else:
            self.header_label.setText(f"🎬 Đang xem thử: {os.path.basename(file_path)}")

        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.btn_play.setText("▶ Phát")
        self.player.pause()
        self.audio_meter.set_playing_state(False)

    def _toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.btn_play.setText("▶ Phát")
        else:
            self.player.play()
            self.btn_play.setText("⏸ Tạm dừng")

    def _stop(self):
        self.player.stop()
        self.btn_play.setText("▶ Phát")
        self.audio_meter.set_playing_state(False)

    def _set_position(self, position):
        self.player.setPosition(position)

    def _position_changed(self, position):
        self.seek_slider.setValue(position)
        self._update_time_label(position, self.player.duration())

    def _duration_changed(self, duration):
        self.seek_slider.setRange(0, duration)
        self._update_time_label(self.player.position(), duration)

    def _update_time_label(self, current_ms, total_ms):
        c_sec = current_ms // 1000
        t_sec = total_ms // 1000
        c_str = f"{c_sec // 60:02d}:{c_sec % 60:02d}"
        t_str = f"{t_sec // 60:02d}:{t_sec % 60:02d}"
        self.time_label.setText(f"{c_str} / {t_str}")

    def _set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)

    def _toggle_mute(self):
        is_muted = self.audio_output.isMuted()
        self.audio_output.setMuted(not is_muted)
        self.btn_mute.setText("🔇" if not is_muted else "🔊")
