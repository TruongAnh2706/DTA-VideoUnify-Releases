"""
DTA VideoUnify Pro - Cyberpunk Splash Screen & Auto-Update/Downloader UI
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Features Animated Gradient Glowing Border, Centered Glow Logo, Silent GitHub Auto-Update, & Auto FFmpeg Downloader QThread.
"""

import os
import sys
import requests
import subprocess
from typing import Tuple, Optional
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QPixmap, QColor, QPainter, QLinearGradient, QPen
import config
from utils.ffmpeg_downloader import FFmpegDownloader

# Silent Auto-Update GitHub Settings
PUBLIC_REPO = "TruongAnh2706/DTA-VideoUnify-Releases"


class SplashInitWorker(QThread):
    """
    QThread worker to run initial system checks, check Silent GitHub Auto-Updates,
    and download FFmpeg automatically if missing.
    """

    progress_signal = pyqtSignal(int, str)   # percent, status_text
    finished_signal = pyqtSignal(bool, str)  # success, message

    def _check_github_update(self) -> Tuple[bool, str, Optional[str]]:
        try:
            url = f"https://api.github.com/repos/{PUBLIC_REPO}/releases/latest"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                latest_ver = data.get("tag_name", "").lstrip("v")
                
                # Compare versions
                from packaging import version
                if latest_ver and version.parse(latest_ver) > version.parse(config.APP_VERSION):
                    for asset in data.get("assets", []):
                        if asset.get("name", "").endswith(".exe"):
                            return True, latest_ver, asset.get("browser_download_url")
        except Exception:
            pass
        return False, config.APP_VERSION, None

    def run(self):
        try:
            self.progress_signal.emit(10, "Đang kiểm tra môi trường hệ thống & Cập nhật GitHub...")
            QThread.msleep(300)

            # Check Silent Auto-Update from GitHub Releases
            has_update, latest_ver, download_url = self._check_github_update()
            if has_update and download_url:
                self.progress_signal.emit(30, f"Phát hiện bản cập nhật mới v{latest_ver}! Đang tải ngầm...")
                temp_dir = os.getenv("TEMP", ".")
                installer_path = os.path.join(temp_dir, "update_installer.exe")
                
                res = requests.get(download_url, stream=True)
                with open(installer_path, "wb") as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
                bat_path = os.path.join(temp_dir, "silent_updater.bat")
                batch_script_content = f'''@echo off
timeout /t 2 /nobreak > nul
"{installer_path}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
start "" "{sys.executable}"
del "%~f0"
'''
                with open(bat_path, "w", encoding="utf-8") as f:
                    f.write(batch_script_content)
                
                subprocess.Popen(["cmd.exe", "/c", bat_path], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
                self.finished_signal.emit(False, "Đang cập nhật phiên bản mới...")
                return

            need_download = FFmpegDownloader.check_need_download()

            if need_download:
                self.progress_signal.emit(40, "Phát hiện thiếu FFmpeg! Bắt đầu tải bản tĩnh FFmpeg...")
                
                def _on_download_progress(pct, status):
                    self.progress_signal.emit(pct, status)

                success = FFmpegDownloader.download_and_extract(_on_download_progress)
                if success:
                    self.progress_signal.emit(100, "✅ Đã tải và cài đặt FFmpeg thành công! Đang khởi chạy...")
                    QThread.msleep(500)
                    self.finished_signal.emit(True, "Sẵn sàng")
                else:
                    self.finished_signal.emit(False, "Không thể tải tự động FFmpeg. Bạn vẫn có thể mở app xem thử.")
            else:
                self.progress_signal.emit(80, "✅ FFmpeg & FFprobe đã sẵn sàng trong hệ thống!")
                QThread.msleep(400)
                self.progress_signal.emit(100, "Đang mở DTA VideoUnify Pro...")
                QThread.msleep(200)
                self.finished_signal.emit(True, "Sẵn sàng")

        except Exception as e:
            self.finished_signal.emit(False, f"Lỗi kiểm tra môi trường: {str(e)}")


class DTASplashScreen(QWidget):
    """
    Custom Frameless Glassmorphic Cyberpunk Splash Screen Window with Animated Gradient Glowing Border
    and Centered Neon Glowing Logo.
    """

    app_ready_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(520, 420)

        # Gradient Animation Phase Angle
        self.anim_angle = 0.0

        self._init_ui()
        self._start_border_animation()
        self._start_checker()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Inner Glassmorphic Container
        self.container = QFrame()
        self.container.setObjectName("SplashContainer")
        self.container.setStyleSheet("""
            QFrame#SplashContainer {
                background-color: #0B0C10;
                border-radius: 16px;
            }
            QLabel {
                border: none;
                background: transparent;
                background-color: transparent;
            }
        """)

        # Container Shadow Effect
        self.container_shadow = QGraphicsDropShadowEffect(self)
        self.container_shadow.setBlurRadius(35)
        self.container_shadow.setColor(QColor(0, 242, 254, 150))
        self.container_shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(self.container_shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(28, 28, 28, 24)
        container_layout.setSpacing(10)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Centered Large Logo with Neon Glow
        self.logo_label = QLabel()
        if os.path.exists(config.LOGO_PNG_PATH):
            pixmap = QPixmap(config.LOGO_PNG_PATH).scaled(
                105, 105, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("🎬")
            self.logo_label.setStyleSheet("font-size: 64px;")

        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo Neon Glow Effect
        logo_glow = QGraphicsDropShadowEffect(self)
        logo_glow.setBlurRadius(25)
        logo_glow.setColor(QColor(0, 242, 254, 220))
        logo_glow.setOffset(0, 0)
        self.logo_label.setGraphicsEffect(logo_glow)

        container_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 2. App Title directly below Logo
        app_title = QLabel(config.APP_NAME)
        app_title.setStyleSheet("font-size: 25px; font-weight: 900; color: #00F2FE; letter-spacing: 1px;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(app_title)

        # 3. Version Label
        app_ver = QLabel(f"Version {config.APP_VERSION} - Enterprise Edition")
        app_ver.setStyleSheet("font-size: 12px; color: #A0AEC0; font-weight: 600;")
        app_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(app_ver)

        # 4. Author Branding
        author_label = QLabel(config.COPYRIGHT_TEXT)
        author_label.setStyleSheet("color: #FFD100; font-size: 12px; font-weight: 700; padding-top: 2px;")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(author_label)

        container_layout.addSpacing(10)

        # 5. Real-time Status Label
        self.status_label = QLabel("Đang khởi tạo môi trường DTA Studio...")
        self.status_label.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: 600;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.status_label)

        # 6. Neon Gradient Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #131622;
                border: 1px solid #1F2638;
                border-radius: 6px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00F2FE, stop:0.5 #FFD100, stop:1 #FF0055);
                border-radius: 5px;
            }
        """)
        container_layout.addWidget(self.progress_bar)

        # 7. Footer Subtitle
        footer_label = QLabel("System Checker & Silent Auto-Updater Engine v2.0")
        footer_label.setStyleSheet("color: #4A5568; font-size: 10px; font-weight: 600;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(footer_label)

        main_layout.addWidget(self.container)

        # Center Window on Screen
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _start_border_animation(self):
        """Timer for animating gradient glow border colors."""
        self.border_timer = QTimer(self)
        self.border_timer.setInterval(35)  # ~30 FPS animation
        self.border_timer.timeout.connect(self._animate_border)
        self.border_timer.start()

    def _animate_border(self):
        self.anim_angle = (self.anim_angle + 0.04) % (2 * 3.14159)
        self.update()

    def paintEvent(self, event):
        """Custom paint event to draw smooth animated gradient border around container."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.container.geometry()

        # Dynamic Gradient Colors shifting with anim_angle
        import math
        c1_factor = (math.sin(self.anim_angle) + 1) / 2.0

        gradient = QLinearGradient(rect.topLeft().toPointF(), rect.bottomRight().toPointF())
        gradient.setColorAt(0.0, QColor(0, 242, 254))                             # Cyan
        gradient.setColorAt(0.5, QColor(int(255 * c1_factor), 209, int(255 * (1 - c1_factor)))) # Gold / Pink Shift
        gradient.setColorAt(1.0, QColor(255, 0, 85))                             # Neon Pink

        pen = QPen(gradient, 2.5)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Draw smooth glowing border line matching container border-radius
        painter.drawRoundedRect(rect, 16, 16)

    def _start_checker(self):
        self.worker = SplashInitWorker()
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, pct: int, status_text: str):
        self.progress_bar.setValue(pct)
        self.status_label.setText(status_text)

    def _on_finished(self, success: bool, msg: str):
        self.border_timer.stop()
        if success:
            self.app_ready_signal.emit()
            self.close()
