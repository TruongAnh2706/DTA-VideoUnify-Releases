"""
DTA VideoUnify Pro - FFmpeg Automatic Downloader Utility
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Automatically downloads & extracts static FFmpeg & FFprobe binaries if missing.
"""

import os
import sys
import zipfile
import urllib.request
from typing import Callable, Optional
from utils.ffmpeg_helper import FFmpegHelper

# Direct stable download mirrors for Windows static FFmpeg binaries
FFMPEG_WIN_ZIP_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_MIRROR_ZIP_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"


class FFmpegDownloader:
    """
    Utility class that handles automatic downloading and extraction of static
    FFmpeg and FFprobe executables for Windows.
    """

    @staticmethod
    def get_bin_dir() -> str:
        """Returns the local bin directory inside the application folder."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bin_dir = os.path.join(base_dir, "bin")
        os.makedirs(bin_dir, exist_ok=True)
        return bin_dir

    @classmethod
    def check_need_download(cls) -> bool:
        """Checks if ffmpeg or ffprobe binaries are missing from both system PATH and local bin dir."""
        bin_dir = cls.get_bin_dir()
        local_ffmpeg = os.path.join(bin_dir, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        local_ffprobe = os.path.join(bin_dir, "ffprobe.exe" if sys.platform == "win32" else "ffprobe")

        if os.path.exists(local_ffmpeg) and os.path.exists(local_ffprobe):
            return False

        available, _ = FFmpegHelper.check_binaries_available()
        return not available

    @classmethod
    def download_and_extract(cls, progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
        """
        Downloads static FFmpeg zip archive and extracts ffmpeg.exe & ffprobe.exe into bin/ folder.
        progress_callback: Callable(percent_int, status_text_str)
        """
        bin_dir = cls.get_bin_dir()
        zip_path = os.path.join(bin_dir, "ffmpeg_download.zip")

        if progress_callback:
            progress_callback(5, "Đang kết nối tới server tải về FFmpeg...")

        download_urls = [FFMPEG_WIN_ZIP_URL, FFMPEG_MIRROR_ZIP_URL]
        download_success = False

        for url in download_urls:
            try:
                def _reporthook(block_num, block_size, total_size):
                    if total_size > 0:
                        downloaded = block_num * block_size
                        pct = int(min(90, (downloaded / total_size) * 85 + 5))
                        mb_dn = downloaded / (1024 * 1024)
                        mb_tot = total_size / (1024 * 1024)
                        if progress_callback:
                            progress_callback(pct, f"Đang tải FFmpeg: {mb_dn:.1f} MB / {mb_tot:.1f} MB ({pct}%)")

                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                    total_size = int(response.info().get('Content-Length', 0))
                    block_size = 8192
                    downloaded = 0
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        out_file.write(buffer)
                        if total_size > 0 and progress_callback:
                            pct = int(min(90, (downloaded / total_size) * 85 + 5))
                            mb_dn = downloaded / (1024 * 1024)
                            mb_tot = total_size / (1024 * 1024)
                            progress_callback(pct, f"Đang tải FFmpeg: {mb_dn:.1f} MB / {mb_tot:.1f} MB ({pct}%)")

                if os.path.exists(zip_path) and os.path.getsize(zip_path) > 1000000:
                    download_success = True
                    break
            except Exception as e:
                if os.path.exists(zip_path):
                    try:
                        os.remove(zip_path)
                    except Exception:
                        pass
                continue

        if not download_success:
            if progress_callback:
                progress_callback(0, "Lỗi tải FFmpeg từ server. Vui lòng kiểm tra kết nối mạng!")
            return False

        # Extract Zip File
        try:
            if progress_callback:
                progress_callback(92, "Đang giải nén ffmpeg.exe & ffprobe.exe vào ứng dụng...")

            extracted_count = 0
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    filename = os.path.basename(member)
                    if filename.lower() in ("ffmpeg.exe", "ffprobe.exe", "ffmpeg", "ffprobe"):
                        target_file_path = os.path.join(bin_dir, filename)
                        with zip_ref.open(member) as source, open(target_file_path, "wb") as target:
                            target.write(source.read())
                        extracted_count += 1

            # Cleanup Zip file
            try:
                os.remove(zip_path)
            except Exception:
                pass

            if extracted_count >= 2:
                if progress_callback:
                    progress_callback(100, "✅ Cài đặt FFmpeg hoàn tất!")
                return True
            else:
                return False

        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Lỗi giải nén FFmpeg: {str(e)}")
            return False
