"""
DTA VideoUnify Pro - Silent Auto-Update Engine (GitHub Releases)
Phát triển bởi DTA Studio - Chủ quản: Đức Trường (0962.775.506)
Email: ductruong.onl@gmail.com | Zalo/SĐT: 0962775506
Website: https://dta-studio.vercel.app/
GitHub Repo: TruongAnh2706/DTA-VideoUnify-Releases
"""

import sys
import os
import httpx
import tempfile
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Callable
from packaging import version
from PyQt6.QtCore import QThread, pyqtSignal

import config

APP_EXE_NAME = "DTA_VideoUnify_Pro.exe"

class SilentUpdater:
    """
    Module Cập Nhật Ngầm (Silent Auto-Update Engine) cho DTA VideoUnify Pro.
    Tự động kiểm tra bản phát hành mới trên Public GitHub Releases API
    và nâng cấp ngầm không gián đoạn trải nghiệm người dùng theo đúng Blueprint DTA Studio.
    """

    PUBLIC_REPO = "TruongAnh2706/DTA-VideoUnify-Releases"
    CURRENT_VERSION = config.APP_VERSION.split()[0]  # "2.0.0"

    @classmethod
    def check_for_updates(cls) -> Tuple[bool, str, Optional[str], str]:
        """Kiểm tra phiên bản mới từ GitHub Releases API"""
        try:
            url = f"https://api.github.com/repos/{cls.PUBLIC_REPO}/releases/latest"
            with httpx.Client(timeout=6.0, follow_redirects=True) as client:
                res = client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    raw_tag = data.get("tag_name", "v1.0.0")
                    latest_ver = raw_tag.lstrip("v").strip().split()[0]
                    release_notes = data.get("body", "Phiên bản nâng cấp tính năng và hiệu năng từ DTA Studio.")

                    # So sánh phiên bản với packaging.version
                    if latest_ver and version.parse(latest_ver) > version.parse(cls.CURRENT_VERSION):
                        for asset in data.get("assets", []):
                            name = asset.get("name", "").lower()
                            if name.endswith(".exe") or name.endswith(".zip"):
                                download_url = asset.get("browser_download_url")
                                return True, latest_ver, download_url, release_notes

        except Exception as e:
            print(f"[Silent Update Check Note] {e}")

        return False, cls.CURRENT_VERSION, None, ""

    @classmethod
    def perform_silent_update(cls, download_url: str, progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
        """Tải bản cài đặt mới ngầm vào %TEMP% và chạy Silent Installer khi đóng app"""
        temp_dir = os.getenv("TEMP") or os.getenv("TMP") or tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, "dta_videounify_update.exe")

        try:
            if progress_callback:
                progress_callback(10, "⚡ Đang tải bản cập nhật ngầm từ GitHub...")

            # 1. Tải bản cài đặt mới ngầm vào %TEMP%
            with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                with client.stream("GET", download_url) as response, open(installer_path, "wb") as f:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    for chunk in response.iter_bytes(chunk_size=16384):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and progress_callback:
                            pct = int((downloaded / total_size) * 80) + 10
                            mb_curr = downloaded // (1024 * 1024)
                            mb_total = total_size // (1024 * 1024)
                            progress_callback(pct, f"⚡ Đang tải bản cập nhật ({mb_curr}MB / {mb_total}MB)...")

            if progress_callback:
                progress_callback(95, "🚀 Tải hoàn tất! Đang khởi chạy nâng cấp ngầm...")

            # 2. Tạo kịch bản Batch thực thi ngầm tự động theo DTA Studio Blueprint
            bat_path = os.path.join(temp_dir, "silent_updater.bat")
            app_exe = sys.executable

            installed_exe = rf"C:\Program Files (x86)\DTA Studio\DTA VideoUnify Pro\{APP_EXE_NAME}"
            appdata_dir = os.path.join(os.getenv("LOCALAPPDATA") or r"C:\Users\Admin\AppData\Local", "Programs", "DTA Studio", "DTA VideoUnify Pro")
            appdata_exe = os.path.join(appdata_dir, APP_EXE_NAME)

            batch_script_content = f'''@echo off
chcp 65001 > nul
timeout /t 2 /nobreak > nul
taskkill /F /IM {APP_EXE_NAME} > nul 2>&1
timeout /t 2 /nobreak > nul
"{installer_path}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
timeout /t 3 /nobreak > nul
if exist "{installed_exe}" (
    start "" "{installed_exe}"
) else if exist "{appdata_exe}" (
    start "" "{appdata_exe}"
) else (
    start "" "{app_exe}"
)
del "%~f0"
'''
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(batch_script_content)

            # 3. Kích hoạt Batch script ngầm không hiển thị cửa sổ CMD
            subprocess.Popen(
                ["cmd.exe", "/c", bat_path],
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            if progress_callback:
                progress_callback(100, "🎉 Hoàn tất! Ứng dụng sẽ tự động khởi động lại!")

            # 4. Thoát ứng dụng hiện tại để Batch Silent Installer tiến hành nâng cấp
            sys.exit(0)
            return True

        except Exception as e:
            print(f"[Silent Update Fail] {e}")
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
