"""
DTA VideoUnify Pro - Cyberpunk Audio Waveform & VU Meter Widget
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Interactive LED Audio Level Meter for real-time audio visualization beside Video Preview Player.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor, QLinearGradient
import random


class AudioWaveformMeter(QWidget):
    """
    Cyberpunk Style LED / Audio Waveform Meter Bar.
    Animates audio level LEDs dynamically when video is playing.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(20)
        self.setMinimumHeight(200)
        self.is_playing = False
        self.level = 0.6  # Default fallback level

        # Timer for simulating animated audio spectrum bars when media plays
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(60)  # ~16 FPS animation
        self.anim_timer.timeout.connect(self._update_animation)

    def set_playing_state(self, playing: bool):
        self.is_playing = playing
        if playing:
            self.anim_timer.start()
        else:
            self.anim_timer.stop()
            self.level = 0.0
            self.update()

    def set_level(self, level: float):
        """Set explicit audio peak level between 0.0 and 1.0"""
        self.level = max(0.0, min(1.0, level))
        self.update()

    def _update_animation(self):
        if self.is_playing:
            # Generate organic audio VU meter fluctuations
            self.level = random.uniform(0.35, 0.95)
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Background track
        painter.fillRect(0, 0, width, height, QColor("#0B0C10"))

        # Draw LED segments (20 segments total)
        num_segments = 22
        segment_gap = 2
        segment_height = (height - (num_segments + 1) * segment_gap) / num_segments

        active_segments = int(self.level * num_segments) if self.is_playing else 0

        for i in range(num_segments):
            # Index 0 is bottom, num_segments - 1 is top
            idx_from_bottom = i
            y_pos = height - (idx_from_bottom + 1) * (segment_height + segment_gap)

            # Determine segment color (Bottom: Cyan -> Middle: Gold -> Top: Neon Red/Pink)
            ratio = idx_from_bottom / float(num_segments)

            if ratio > 0.82:
                # Peak Overload Red/Pink
                color_active = QColor("#FF0055")
                color_dim = QColor(60, 0, 20)
            elif ratio > 0.6:
                # High Gold/Yellow
                color_active = QColor("#FFD100")
                color_dim = QColor(60, 50, 0)
            else:
                # Normal Electric Cyan
                color_active = QColor("#00F2FE")
                color_dim = QColor(0, 50, 60)

            if idx_from_bottom < active_segments:
                painter.setBrush(color_active)
                painter.setPen(Qt.PenStyle.NoPen)
            else:
                painter.setBrush(color_dim)
                painter.setPen(Qt.PenStyle.NoPen)

            painter.drawRoundedRect(
                int(3), int(y_pos), int(width - 6), int(segment_height), 2, 2
            )
