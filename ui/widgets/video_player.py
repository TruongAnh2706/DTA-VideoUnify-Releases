"""
DTA VideoUnify Pro - Interactive Video Preview Player Widget
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Features 16:9 / 9:16 Preview, Cyberpunk Audio VU Meter, & 4-Corner Handles Resizable/Draggable Watermark Logo Overlay!
"""

import os
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QPoint, QRect, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSlider, QFrame
)
from PyQt6.QtGui import QPixmap, QCursor, QMouseEvent, QPainter, QColor, QPen, QBrush
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from ui.widgets.audio_meter import AudioWaveformMeter


class DraggableWatermarkLabel(QWidget):
    """
    Interactive Watermark Overlay Widget featuring 4 Corner Resize Handles.
    Supports Dragging to reposition and dragging any of the 4 corner handles to scale logo.
    Auto-saves relative position and scale on mouse release!
    """

    position_changed_signal = pyqtSignal(float, float, float)  # rel_x, rel_y, rel_scale

    HANDLE_NONE = 0
    HANDLE_TOP_LEFT = 1
    HANDLE_TOP_RIGHT = 2
    HANDLE_BOTTOM_LEFT = 3
    HANDLE_BOTTOM_RIGHT = 4
    HANDLE_MOVE = 5

    HANDLE_SIZE = 10  # 10x10 px corner handles

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.pixmap: QPixmap = None
        self.active_handle = self.HANDLE_NONE
        self.drag_start_pos = QPoint()
        self.drag_start_rect = QRect()
        self.aspect_ratio = 1.0

        self.setVisible(False)

    def set_logo_pixmap(self, pixmap: QPixmap):
        self.pixmap = pixmap
        if pixmap and not pixmap.isNull() and pixmap.width() > 0:
            self.aspect_ratio = float(pixmap.height()) / float(pixmap.width())
        self.update()

    def _get_handle_at(self, pos: QPoint) -> int:
        w = self.width()
        h = self.height()
        hs = self.HANDLE_SIZE

        # Corner handle rectangles
        rect_tl = QRect(0, 0, hs, hs)
        rect_tr = QRect(w - hs, 0, hs, hs)
        rect_bl = QRect(0, h - hs, hs, hs)
        rect_br = QRect(w - hs, h - hs, hs, hs)

        if rect_tl.contains(pos):
            return self.HANDLE_TOP_LEFT
        if rect_tr.contains(pos):
            return self.HANDLE_TOP_RIGHT
        if rect_bl.contains(pos):
            return self.HANDLE_BOTTOM_LEFT
        if rect_br.contains(pos):
            return self.HANDLE_BOTTOM_RIGHT

        if QRect(hs, hs, w - 2 * hs, h - 2 * hs).contains(pos) or QRect(0, 0, w, h).contains(pos):
            return self.HANDLE_MOVE

        return self.HANDLE_NONE

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.active_handle = self._get_handle_at(event.pos())
            self.drag_start_pos = event.globalPosition().toPoint()
            self.drag_start_rect = self.geometry()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.active_handle == self.HANDLE_NONE:
            handle = self._get_handle_at(event.pos())
            if handle in (self.HANDLE_TOP_LEFT, self.HANDLE_BOTTOM_RIGHT):
                self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            elif handle in (self.HANDLE_TOP_RIGHT, self.HANDLE_BOTTOM_LEFT):
                self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            elif handle == self.HANDLE_MOVE:
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        elif self.active_handle == self.HANDLE_MOVE:
            parent = self.parentWidget()
            if parent:
                delta = event.globalPosition().toPoint() - self.drag_start_pos
                new_x = self.drag_start_rect.x() + delta.x()
                new_y = self.drag_start_rect.y() + delta.y()

                max_x = parent.width() - self.width()
                max_y = parent.height() - self.height()
                clamped_x = max(0, min(new_x, max_x))
                clamped_y = max(0, min(new_y, max_y))

                self.move(clamped_x, clamped_y)
            event.accept()

        elif self.active_handle in (self.HANDLE_TOP_LEFT, self.HANDLE_TOP_RIGHT, self.HANDLE_BOTTOM_LEFT, self.HANDLE_BOTTOM_RIGHT):
            delta = event.globalPosition().toPoint() - self.drag_start_pos
            orig = self.drag_start_rect

            new_w = orig.width()
            new_x = orig.x()
            new_y = orig.y()

            if self.active_handle == self.HANDLE_BOTTOM_RIGHT:
                new_w = max(40, orig.width() + delta.x())
            elif self.active_handle == self.HANDLE_BOTTOM_LEFT:
                new_w = max(40, orig.width() - delta.x())
                new_x = orig.x() + (orig.width() - new_w)
            elif self.active_handle == self.HANDLE_TOP_RIGHT:
                new_w = max(40, orig.width() + delta.x())
                new_h = int(new_w * self.aspect_ratio)
                new_y = orig.y() + (orig.height() - new_h)
            elif self.active_handle == self.HANDLE_TOP_LEFT:
                new_w = max(40, orig.width() - delta.x())
                new_h = int(new_w * self.aspect_ratio)
                new_x = orig.x() + (orig.width() - new_w)
                new_y = orig.y() + (orig.height() - new_h)

            new_h = int(new_w * self.aspect_ratio)
            self.setGeometry(new_x, new_y, new_w, new_h)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.active_handle = self.HANDLE_NONE
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            # Auto save position & size on mouse release!
            self._emit_position_changed()
            event.accept()

    def _emit_position_changed(self):
        parent = self.parentWidget()
        if parent and parent.width() > 0 and parent.height() > 0:
            rel_x = float(self.x()) / parent.width()
            rel_y = float(self.y()) / parent.height()
            rel_scale = float(self.width()) / parent.width()
            self.position_changed_signal.emit(rel_x, rel_y, rel_scale)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Draw Logo Pixmap
        if self.pixmap and not self.pixmap.isNull():
            painter.drawPixmap(0, 0, w, h, self.pixmap)

        # Draw Bounding Dashed Border
        pen_border = QPen(QColor("#00F2FE"), 1.5, Qt.PenStyle.DashLine)
        painter.setPen(pen_border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(0, 0, w - 1, h - 1)

        # Draw 4 Corner Handles (Cyan Square Boxes with Glow)
        hs = self.HANDLE_SIZE
        painter.setPen(QPen(QColor("#FFD100"), 1.5))
        painter.setBrush(QBrush(QColor("#00F2FE")))

        # Top-Left, Top-Right, Bottom-Left, Bottom-Right handle boxes
        painter.drawRect(0, 0, hs, hs)
        painter.drawRect(w - hs, 0, hs, hs)
        painter.drawRect(0, h - hs, hs, hs)
        painter.drawRect(w - hs, h - hs, hs, hs)


class InteractiveVideoPlayer(QWidget):
    """
    Custom Interactive Preview Player Widget powered by PyQt6 QtMultimedia.
    Features 4-Corner Handle Resizable & Draggable Watermark Overlay.
    """

    prev_requested = pyqtSignal()
    next_requested = pyqtSignal()
    watermark_params_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = ""
        self.is_portrait_mode = False

        # Watermark parameters
        self.wm_enabled = False
        self.wm_path = ""
        self.wm_opacity = 0.85
        self.wm_rel_x = 0.75
        self.wm_rel_y = 0.05
        self.wm_rel_scale = 0.18

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
        self.btn_aspect_169.clicked.connect(lambda: self._set_aspect_ratio(False))

        self.btn_aspect_916 = QPushButton("📱 Dọc (9:16)")
        self.btn_aspect_916.setObjectName("AspectButton")
        self.btn_aspect_916.setProperty("active", "false")
        self.btn_aspect_916.clicked.connect(lambda: self._set_aspect_ratio(True))

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

        # Inner Center Box for Video Widget & Overlays
        self.video_wrapper = QWidget()
        video_wrapper_layout = QHBoxLayout(self.video_wrapper)
        video_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        video_wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Video Display Widget
        self.video_widget = QVideoWidget(self.video_wrapper)
        self.video_widget.setStyleSheet("background-color: #000000; border-radius: 8px;")
        self.video_widget.setMinimumSize(320, 180)
        video_wrapper_layout.addWidget(self.video_widget)

        # 4-Corner Handles Draggable Watermark Overlay Widget
        self.watermark_overlay = DraggableWatermarkLabel(self.video_widget)
        self.watermark_overlay.position_changed_signal.connect(self._on_wm_overlay_moved)

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

    def set_watermark(self, enabled: bool, logo_path: str = ""):
        """Enable or update interactive watermark overlay on top of video widget."""
        self.wm_enabled = enabled

        if enabled and logo_path and os.path.exists(logo_path):
            self.wm_path = logo_path
            pixmap = QPixmap(logo_path)
            self.watermark_overlay.set_logo_pixmap(pixmap)
            self.watermark_overlay.setVisible(True)
            self._update_overlay_position_and_size()
        else:
            self.watermark_overlay.setVisible(False)

    def _update_overlay_position_and_size(self):
        vw = self.video_widget.width()
        vh = self.video_widget.height()
        if vw <= 0 or vh <= 0:
            return

        w = int(vw * self.wm_rel_scale)
        w = max(40, min(vw, w))
        h = int(w * self.watermark_overlay.aspect_ratio)

        x = int(vw * self.wm_rel_x)
        y = int(vh * self.wm_rel_y)

        x = max(0, min(vw - w, x))
        y = max(0, min(vh - h, y))

        self.watermark_overlay.setGeometry(x, y, w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.wm_enabled:
            self._update_overlay_position_and_size()

    def _on_wm_overlay_moved(self, rel_x: float, rel_y: float, rel_scale: float):
        self.wm_rel_x = rel_x
        self.wm_rel_y = rel_y
        self.wm_rel_scale = rel_scale
        self._emit_wm_params()

    def _emit_wm_params(self):
        params = {
            "enabled": self.wm_enabled,
            "path": self.wm_path,
            "opacity": self.wm_opacity,
            "rel_x": self.wm_rel_x,
            "rel_y": self.wm_rel_y,
            "scale": self.wm_rel_scale
        }
        self.watermark_params_changed.emit(params)

    def get_watermark_params(self) -> dict:
        return {
            "enabled": self.wm_enabled,
            "path": self.wm_path,
            "opacity": self.wm_opacity,
            "rel_x": self.wm_rel_x,
            "rel_y": self.wm_rel_y,
            "scale": self.wm_rel_scale
        }

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
            self.video_widget.setMaximumWidth(260)
            self.video_widget.setMinimumWidth(180)
        else:
            self.video_widget.setMaximumWidth(16777215)
            self.video_widget.setMinimumWidth(320)

        self.video_widget.updateGeometry()
        if self.wm_enabled:
            self._update_overlay_position_and_size()

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
