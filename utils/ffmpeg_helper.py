"""
DTA VideoUnify Pro - FFmpeg Helper Utilities
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Features Multi-Path Binaries Resolution, UTF-8 Escaping, Fast Stream Probing, Chapter Metadata Generation,
Smart Aspect & Resolution Uniformity Checking, and NVIDIA GPU NVENC Hardware Acceleration Detection.
"""

import os
import sys
import json
import shutil
import subprocess
from typing import Dict, List, Any, Tuple, Optional


class FFmpegHelper:
    """Utility class for finding and calling FFmpeg & FFprobe binaries safely with UTF-8 encoding."""

    _has_nvenc_cache: Optional[bool] = None

    @classmethod
    def get_binary_path(cls, name: str) -> str:
        """Finds absolute path to ffmpeg or ffprobe executable across all local directories and PATH."""
        exe_name = f"{name}.exe" if sys.platform == "win32" else name

        # Candidate paths to search
        possible_paths = []

        # 1. Check PyInstaller temp directory (_MEIPASS)
        if getattr(sys, 'frozen', False):
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            possible_paths.append(os.path.join(base_dir, exe_name))
            possible_paths.append(os.path.join(base_dir, "bin", exe_name))
            possible_paths.append(os.path.join(os.path.dirname(sys.executable), exe_name))
            possible_paths.append(os.path.join(os.path.dirname(sys.executable), "bin", exe_name))

        # 2. Check source project bin/ directory
        source_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        possible_paths.append(os.path.join(source_dir, "bin", exe_name))
        possible_paths.append(os.path.join(source_dir, exe_name))

        # 3. Check Current Working Directory
        possible_paths.append(os.path.join(os.getcwd(), "bin", exe_name))
        possible_paths.append(os.path.join(os.getcwd(), exe_name))

        # 4. Check LocalAppData App folder
        local_appdata = os.getenv("LOCALAPPDATA", "")
        if local_appdata:
            possible_paths.append(os.path.join(local_appdata, "Programs", "DTA Studio", "DTA VideoUnify Pro", "bin", exe_name))
            possible_paths.append(os.path.join(local_appdata, "DTA Studio", "ffmpeg", exe_name))

        for path in possible_paths:
            if os.path.exists(path) and os.path.isfile(path):
                return os.path.normpath(path)

        # 5. Search in System PATH using shutil.which
        path_in_env = shutil.which(name)
        if path_in_env:
            return path_in_env

        return name

    @classmethod
    def check_binaries_available(cls) -> Tuple[bool, str]:
        ffmpeg_bin = cls.get_binary_path("ffmpeg")
        ffprobe_bin = cls.get_binary_path("ffprobe")

        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            res_ff = subprocess.run([ffmpeg_bin, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", startupinfo=startupinfo)
            res_fp = subprocess.run([ffprobe_bin, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", startupinfo=startupinfo)

            if res_ff.returncode == 0 and res_fp.returncode == 0:
                return True, f"FFmpeg & FFprobe sẵn sàng! ({ffmpeg_bin})"
            return False, f"Không thể khởi chạy FFmpeg ({ffmpeg_bin}). [WinError 2] Tệp không tồn tại."
        except Exception as e:
            return False, f"Lỗi kiểm tra hệ thống FFmpeg: {str(e)}"

    @classmethod
    def has_nvenc_support(cls) -> bool:
        if cls._has_nvenc_cache is not None:
            return cls._has_nvenc_cache

        ffmpeg_bin = cls.get_binary_path("ffmpeg")
        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            res = subprocess.run(
                [ffmpeg_bin, "-hide_banner", "-encoders"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo
            )
            has_h264_nvenc = "h264_nvenc" in res.stdout
            cls._has_nvenc_cache = has_h264_nvenc
            return has_h264_nvenc
        except Exception:
            cls._has_nvenc_cache = False
            return False

    @classmethod
    def probe_file(cls, file_path: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(file_path):
            return None

        ffprobe_bin = cls.get_binary_path("ffprobe")
        cmd = [
            ffprobe_bin,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path
        ]

        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo
            )
            if result.returncode != 0 or not result.stdout:
                return None

            data = json.loads(result.stdout)
            streams = data.get("streams", [])
            format_info = data.get("format", {})

            video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
            audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

            if not video_stream:
                return None

            duration = float(format_info.get("duration", 0.0))
            if duration == 0.0 and video_stream.get("duration"):
                duration = float(video_stream.get("duration", 0.0))

            r_fps = video_stream.get("r_frame_rate", "30/1")
            try:
                num, den = map(int, r_fps.split('/'))
                fps = num / den if den != 0 else 30.0
            except Exception:
                fps = 30.0

            return {
                "file_path": file_path,
                "duration": duration,
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "v_codec": video_stream.get("codec_name", ""),
                "fps": round(fps, 2),
                "pix_fmt": video_stream.get("pix_fmt", "yuv420p"),
                "a_codec": audio_stream.get("codec_name", "") if audio_stream else "none",
                "sample_rate": audio_stream.get("sample_rate", "44100") if audio_stream else "0",
                "channels": audio_stream.get("channels", 2) if audio_stream else 0
            }
        except Exception:
            return None

    @classmethod
    def check_series_uniformity(cls, metadata_list: List[Dict[str, Any]]) -> bool:
        """
        Determines if Direct Copy can be used safely.
        For Short Dramas, matching Width, Height, and Video Codec are sufficient for Direct Copy Concat!
        Minor FPS variances (e.g. 24 FPS vs 25 FPS) do NOT break Direct Copy Concat with +genpts.
        """
        if not metadata_list or len(metadata_list) < 2:
            return True

        first = metadata_list[0]
        # Only check resolution and video codec for Direct Copy eligibility!
        keys_to_compare = ["width", "height", "v_codec"]

        for meta in metadata_list[1:]:
            for key in keys_to_compare:
                if meta.get(key) != first.get(key):
                    return False
        return True

    @classmethod
    def create_concat_demuxer_file(cls, file_paths: List[str], temp_file_path: str) -> None:
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write("ffconcat version 1.0\n")
            for p in file_paths:
                clean_p = p.replace("\\", "/")
                escaped_path = clean_p.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")

    @classmethod
    def generate_chapter_metadata(cls, episodes_meta: List[Tuple[int, str, float]], meta_file_path: str, intro_offset_sec: float = 0.0) -> None:
        with open(meta_file_path, "w", encoding="utf-8") as f:
            f.write(";FFMETADATA1\n")
            f.write("title=DTA VideoUnify Pro Merged Drama\n")
            f.write("artist=DTA Studio - Đức Trường\n\n")

            current_pts = int(intro_offset_sec * 1000)
            timebase = 1000

            if intro_offset_sec > 0:
                f.write("[CHAPTER]\n")
                f.write(f"TIMEBASE=1/{timebase}\n")
                f.write(f"START=0\n")
                f.write(f"END={current_pts}\n")
                f.write("title=Intro\n\n")

            for ep_num, name, dur in episodes_meta:
                dur_ms = int(dur * 1000)
                start_pts = current_pts
                end_pts = current_pts + dur_ms

                f.write("[CHAPTER]\n")
                f.write(f"TIMEBASE=1/{timebase}\n")
                f.write(f"START={start_pts}\n")
                f.write(f"END={end_pts}\n")
                f.write(f"title=Tập {ep_num}\n\n")

                current_pts = end_pts
