"""
DTA VideoUnify Pro - Config & Constants
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Email: ductruong.onl@gmail.com | Zalo/SĐT: 0962775506
Website: https://dta-studio.vercel.app/
Facebook: https://www.facebook.com/phamductruong17/
GitHub: https://github.com/TruongAnh2706
"""

import os
import sys

# Branding Information
APP_NAME = "DTA VideoUnify Pro"
APP_VERSION = "2.1.0"
AUTHOR_NAME = "Đức Trường AI"
COMPANY_NAME = "DTA Studio"
CONTACT_EMAIL = "ductruong.onl@gmail.com"
CONTACT_ZALO = "0962.775.506"
WEBSITE_URL = "https://dta-studio.vercel.app/"
FACEBOOK_URL = "https://www.facebook.com/phamductruong17/"

COPYRIGHT_TEXT = f"Phát triển bởi {COMPANY_NAME} - Chủ quản: Đức Trường | SĐT/Zalo: {CONTACT_ZALO}"

# Logo Asset Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_ICO_PATH = os.path.join(BASE_DIR, "logo.ico")
LOGO_PNG_PATH = os.path.join(BASE_DIR, "logo.png")

# Supported Video Extensions
SUPPORTED_VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm", ".ts", ".m4v"}

# Theme Colors (Dark Cyberpunk / Glassmorphic DTA Theme)
COLOR_BG_PRIMARY = "#121214"
COLOR_BG_SURFACE = "#1E1E22"
COLOR_BG_CARD = "#25252B"
COLOR_BORDER = "#2D2D35"
COLOR_BORDER_FOCUS = "#00FFFF"

COLOR_ACCENT_NEON_BLUE = "#00FFFF"   # Primary Accent (#00FFFF)
COLOR_ACCENT_NEON_RED = "#FF0000"    # High-contrast action (#FF0000)
COLOR_ACCENT_ORANGE = "#FF5722"      # Action Accent
COLOR_ACCENT_GREEN = "#00E676"       # Fast Direct Copy Ready
COLOR_ACCENT_YELLOW = "#FFD600"      # Smart Re-encode Needed

COLOR_TEXT_PRIMARY = "#EEEEEE"
COLOR_TEXT_SECONDARY = "#AAAAAA"
COLOR_TEXT_MUTED = "#666666"

# Default Output Formats
OUTPUT_FORMATS = [".mp4", ".mkv", ".mov", ".avi"]
DEFAULT_OUTPUT_FORMAT = ".mp4"

# Quality Presets
QUALITY_PRESETS = [
    "Direct Copy (0% Loss - Siêu Nhanh)",
    "High Quality NVENC (CQ 18 - Khuyên Dùng)",
    "Fast NVENC (CQ 23)",
    "CPU High Quality (libx264 - CRF 18)",
    "CPU Fast (libx264 - CRF 23)"
]

# Resolutions
RESOLUTIONS = [
    "Gốc (Original Source)",
    "1080p Full HD (1920x1080)",
    "4K Ultra HD (3840x2160)",
    "720p HD (1280x720)"
]

# Watermark Positions
WATERMARK_POSITIONS = [
    "Top-Right",
    "Bottom-Right",
    "Top-Left",
    "Bottom-Left"
]
