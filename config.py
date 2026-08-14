"""
DTA VideoUnify Pro - Application Configuration & Branding Constants
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Email: ductruong.onl@gmail.com | Zalo/SĐT: 0962775506
Website: https://dta-studio.vercel.app/
GitHub: https://github.com/TruongAnh2706/DTA-VideoUnify-Releases
"""

import os
import sys

# Application Identity
APP_NAME = "DTA VideoUnify Pro"
APP_VERSION = "2.4.2"
AUTHOR_NAME = "Đức Trường AI"
COMPANY_NAME = "DTA Studio"
PHONE_ZALO = "0962.775.506"
EMAIL = "ductruong.onl@gmail.com"
WEBSITE = "https://dta-studio.vercel.app/"
COPYRIGHT_TEXT = "Phát triển bởi DTA Studio - Chủ quản: Đức Trường"

# GitHub Auto-Update Endpoint Config
GITHUB_REPO_OWNER = "TruongAnh2706"
GITHUB_REPO_NAME = "DTA-VideoUnify-Releases"
GITHUB_RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"

# File Assets Resolution
def get_asset_path(filename: str) -> str:
    """Returns absolute path to asset file, compatible with PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)

LOGO_PNG_PATH = get_asset_path("logo.png")
LOGO_ICO_PATH = get_asset_path("logo.ico")

# Render Config Options
OUTPUT_FORMATS = [".mp4", ".mkv", ".mov", ".avi"]
DEFAULT_OUTPUT_FORMAT = ".mp4"

RESOLUTIONS = [
    "Gốc (Original Source)",
    "Full HD (1080p / 1920x1080)",
    "HD (720p / 1280x720)",
    "4K Ultra HD (2160p / 3840x2160)"
]

QUALITY_PRESETS = [
    "⚡ Gộp Siêu Nhanh (Gốc - Không Giảm Chất Lượng)",
    "🚀 Nhanh (NVIDIA GPU NVENC Hardware Acceleration)",
    "⚖️ Cân Bằng (Tốc Độ & Dung Lượng Đẹp)",
    "💻 Chuẩn CPU (Tương thích 100% mọi máy tính)",
    "📦 Dung Lượng Nhẹ (Tối Ưu Lưu Trữ Cloud)"
]

ASPECT_RATIOS = ["Ngang (16:9)", "Dọc (9:16)", "Vuông (1:1)"]

# Subprocess & Parsing Regex Settings
SUPPORTED_VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm", ".m4v"}
VIDEO_EXTENSIONS = SUPPORTED_VIDEO_EXTS
SCANNED_DIR_BLACKLIST = {"output", "dist", "build", "temp", "tmp", ".git"}
