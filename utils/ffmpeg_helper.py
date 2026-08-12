"""
DTA VideoUnify Pro - FFmpeg & FFprobe Helper Utility
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Includes #ffconcat version 1.0 header & Unicode/Single-quote path escaping fix.
"""

import os
import sys
import json
import subprocess
import shutil
from typing import Dict, List, Tuple, Optional, Any


class FFmpegHelper:
    """
    Utility class for locating FFmpeg/FFprobe binaries, inspecting media stream
    metadata, checking episode uniformity, and constructing complex FFmpeg commands.
    """

    @staticmethod
    def get_binary_path(binary_name: str) -> str:
        """Find binary executable in local bin/ folder, current directory, or system PATH."""
        if sys.platform == "win32" and not binary_name.endswith(".exe"):
            binary_name += ".exe"

        # Check in local bin/ directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bin_dir_path = os.path.join(base_dir, "bin", binary_name)
        if os.path.exists(bin_dir_path):
            return bin_dir_path

        # Check in current working directory
        local_path = os.path.join(os.getcwd(), binary_name)
        if os.path.exists(local_path):
            return local_path

        # Check in system PATH
        found = shutil.which(binary_name)
        if found:
            return found

        return binary_name

    @classmethod
    def check_binaries_available(cls) -> Tuple[bool, str]:
        """Check if both ffmpeg and ffprobe are available on the system."""
        ffmpeg_bin = cls.get_binary_path("ffmpeg")
        ffprobe_bin = cls.get_binary_path("ffprobe")

        try:
            res_ff = subprocess.run([ffmpeg_bin, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            res_fp = subprocess.run([ffprobe_bin, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if res_ff.returncode == 0 and res_fp.returncode == 0:
                return True, "FFmpeg & FFprobe đã sẵn sàng."
            return False, "Không thể khởi chạy FFmpeg hoặc FFprobe."
        except Exception as e:
            return False, f"Lỗi tìm kiếm FFmpeg/FFprobe: {str(e)}"

    @classmethod
    def probe_file(cls, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Executes ffprobe to extract stream metadata (video/audio codecs, resolution, fps, duration).
        """
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

            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
            if result.returncode != 0:
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

            # FPS parsing
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
                "sample_rate": int(audio_stream.get("sample_rate", 0)) if audio_stream else 0,
                "channels": int(audio_stream.get("channels", 0)) if audio_stream else 0,
                "has_audio": audio_stream is not None
            }
        except Exception:
            return None

    @classmethod
    def check_series_uniformity(cls, metadata_list: List[Dict[str, Any]]) -> bool:
        """
        Determines if all episodes in a series have 100% identical stream properties.
        If true, Direct Copy (concat demuxer) can be used without re-encoding.
        """
        if not metadata_list or len(metadata_list) < 2:
            return True

        first = metadata_list[0]
        keys_to_compare = ["width", "height", "v_codec", "fps", "pix_fmt", "a_codec", "sample_rate", "channels"]

        for meta in metadata_list[1:]:
            for key in keys_to_compare:
                if meta.get(key) != first.get(key):
                    return False
        return True

    @classmethod
    def create_concat_demuxer_file(cls, file_paths: List[str], temp_file_path: str) -> None:
        """
        Writes concat text file formatted for FFmpeg concat demuxer with #ffconcat version 1.0.
        Fixes 'Invalid data found when processing input' error caused by apostrophes (') or Unicode characters in paths.
        """
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write("#ffconcat version 1.0\n")
            for p in file_paths:
                # Normalize slashes to forward slashes for cross-platform FFmpeg compatibility
                norm_p = p.replace("\\", "/")
                # Escape single quotes for FFmpeg concat syntax
                escaped_path = norm_p.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")

    @classmethod
    def generate_chapter_metadata(cls, episodes_meta: List[Tuple[int, str, float]], meta_file_path: str) -> None:
        """
        Generates FFMETADATA file with chapter markers for episode boundaries.
        episodes_meta: List of (ep_num, ep_name, duration_in_seconds)
        """
        with open(meta_file_path, "w", encoding="utf-8") as f:
            f.write(";FFMETADATA1\n")
            f.write("title=DTA VideoUnify Pro Merged Drama\n")
            f.write("artist=DTA Studio - Đức Trường\n\n")

            current_pts = 0
            timebase = 1000  # milliseconds

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
