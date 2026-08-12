"""
DTA VideoUnify Pro - Silent Auto-Update Engine (GitHub Releases)
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Email: ductruong.onl@gmail.com | Zalo/SĐT: 0962775506
Website: https://dta-studio.vercel.app/
GitHub Repo: TruongAnh2706/DTA-VideoUnify-Releases
"""

import sys
import os
import requests
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Callable
from packaging import version
from PyQt6.QtCore import QThread, pyqtSignal

import config


class SilentUpdater:
    """
    Module Cập Nhật Ngầm (Silent Auto-Update Engine) cho DTA VideoUnify Pro.
    Tự động kiểm tra bản phát hành mới trên Public GitHub Releases API
    và nâng cấp ngầm không gián đoạn trải nghiệm người dùng.
    """

    PUBLIC_REPO = "TruongAnh2706/DTA-VideoUnify-Releases"
    CURRENT_VERSION = config.APP_VERSION  # "2.0.0"

    @classmethod
    def check_for_updates(cls) -> Tuple[bool, str, Optional[str], str]:
        """
        Kiểm tra phiên bản mới từ GitHub Releases API.
        Returns: (has_update, latest_version, download_url, release_notes)
        """
        try:
            url = f"https://api.github.com/repos/{cls.PUBLIC_REPO}/releases/latest"
            headers = {"User-Agent": f"DTA-VideoUnify-Pro-AutoUpdater/v{cls.CURRENT_VERSION}"}
            res = requests.get(url, headers=headers, timeout=6)

            if res.status_code == 200:
                data = res.json()
                raw_tag = data.get("tag_name", "v1.0.0")
                latest_ver = raw_tag.lstrip("v").strip()
                release_notes = data.get("body", "Phiên bản nâng cấp tính năng và hiệu năng từ DTA Studio.")

                # So sánh phiên bản với packaging.version
                if version.parse(latest_ver) > version.parse(cls.CURRENT_VERSION):
                    for asset in data.get("assets", []):
                        name = asset.get("name", "").lower()
                        if name.endswith(".exe") or name.endswith(".zip"):
                            download_url = asset.get("browser_download_url")
                            return True, latest_ver, download_url, release_notes

        except Exception as e:
            print(f"[DTA AutoUpdate Warning] Lỗi kiểm tra cập nhật: {e}")

        return False, cls.CURRENT_VERSION, None, ""

    @classmethod
    def perform_silent_update(cls, download_url: str, progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
        """
        Tải bản cài đặt mới ngầm vào thư mục %TEMP% và chạy Inno Setup Silent Installer khi đóng app.
        """
        try:
            temp_dir = Path(os.getenv("TEMP", tempfile.gettempdir()))
            installer_path = temp_dir / "DTA_VideoUnify_Pro_Update_Setup.exe"

            if progress_callback:
                progress_callback(10, "⚡ Đang tải bản cập nhật ngầm từ GitHub...")

            res = requests.get(download_url, stream=True, timeout=30)
            res.raise_for_status()

            total_size = int(res.headers.get('content-length', 0))
            downloaded = 0

            with open(installer_path, "wb") as f:
                for chunk in res.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and progress_callback:
                            pct = int((downloaded / total_size) * 80) + 10
                            mb_curr = downloaded // (1024 * 1024)
                            mb_total = total_size // (1024 * 1024)
                            progress_callback(pct, f"⚡ Đang tải bản cập nhật ({mb_curr}MB / {mb_total}MB)...")

            if progress_callback:
                progress_callback(95, "🚀 Tải hoàn tất! Đang khởi chạy nâng cấp ngầm...")

            # Tạo kịch bản Batch thực thi ngầm tự động sau khi ứng dụng hiện tại thoát
            bat_path = temp_dir / "silent_unify_updater.bat"
            app_exe = sys.executable

            batch_script_content = f"""@echo off
timeout /t 2 /nobreak > nul
"{installer_path}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
start "" "{app_exe}"
del "%~f0"
"""
            with open(bat_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(batch_script_content)

            # Kích hoạt Batch script ngầm không hiển thị cửa sổ CMD
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.Popen(
                ["cmd.exe", "/c", str(bat_path)],
                startupinfo=startupinfo
            )

            if progress_callback:
                progress_callback(100, "🎉 Hoàn tất! Ứng dụng sẽ khởi động lại với bản mới nhất!")

            # Thoát ứng dụng hiện tại để Inno Setup Silent Installer tiến hành đè bản mới
            sys.exit(0)
            return True

        except Exception as e:
            print(f"[DTA AutoUpdate Error] Lỗi tải và cài đặt cập nhật: {e}")
            return False


class UpdateCheckThread(QThread):
    """QThread Worker kiểm tra Cập nhật ngầm không gây đơ lag UI."""
    update_found_signal = pyqtSignal(str, str, str)  # latest_ver, download_url, release_notes
    no_update_signal = pyqtSignal(str)

    def run(self):
        has_update, latest_ver, download_url, notes = SilentUpdater.check_for_updates()
        if has_update and download_url:
            self.update_found_signal.emit(latest_ver, download_url, notes)
        else:
            self.no_update_signal.emit(latest_ver)


class UpdateDownloadThread(QThread):
    """QThread Worker tải bản cài đặt ngầm và chạy silent installer."""
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, download_url: str):
        super().__init__()
        self.download_url = download_url

    def run(self):
        def _cb(pct, status_text):
            self.progress_signal.emit(pct, status_text)

        success = SilentUpdater.perform_silent_update(self.download_url, progress_callback=_cb)
        self.finished_signal.emit(success)
