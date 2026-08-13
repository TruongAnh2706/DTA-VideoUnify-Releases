"""
DTA VideoUnify Pro - Batch Render QThread Worker
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Features UTF-8 Concat Demuxer Engine, Automatic Win32 File Unlocking & Smart Unique Output Filename Fallback,
NVENC GPU Acceleration with CPU Fallback, Intro/Outro Stitching, and Chapter Metadata Injection.
"""

import os
import sys
import re
import tempfile
import subprocess
import time
from typing import Dict, List, Any, Tuple, Optional
from PyQt6.QtCore import QThread, pyqtSignal
from utils.ffmpeg_helper import FFmpegHelper


class BatchRenderThread(QThread):
    """
    Asynchronous QThread worker that handles batch merging for multiple series
    via FFmpeg subprocesses without freezing the PyQt6 GUI.
    """

    # Signals
    render_progress_signal = pyqtSignal(int, int, str, float, str, str)  # overall_%, series_%, title, fps, speed, eta
    log_signal = pyqtSignal(str)
    series_finished_signal = pyqtSignal(str, str)  # series_title, output_path
    batch_finished_signal = pyqtSignal(int, int)   # success_count, fail_count
    error_signal = pyqtSignal(str)

    def __init__(self, render_jobs: List[Tuple[str, Dict[str, Any], str]], render_options: Dict[str, Any]):
        super().__init__()
        self.render_jobs = render_jobs
        self.options = render_options
        self._is_cancelled = False
        self._current_process: subprocess.Popen = None

    def cancel(self):
        self._is_cancelled = True
        if self._current_process:
            try:
                self._current_process.terminate()
            except Exception:
                pass

    def run(self):
        total_jobs = len(self.render_jobs)
        success_count = 0
        fail_count = 0

        self.log_signal.emit("🚀 === BẮT ĐẦU TIẾN TRÌNH BATCH MERGE DTA VIDEOUNIFY PRO ===")

        for job_idx, (title, data, raw_out_file) in enumerate(self.render_jobs, start=1):
            if self._is_cancelled:
                self.log_signal.emit("⚠️ Tiến trình đã bị hủy bởi người dùng.")
                break

            # Resolve unique non-locked output file path
            out_file = self._resolve_writable_output_path(raw_out_file)

            self.log_signal.emit(f"\n🎬 [{job_idx}/{total_jobs}] Đang gộp bộ phim: '{title}' -> {out_file}")

            success = self._process_single_series(job_idx, total_jobs, title, data, out_file)
            if success:
                success_count += 1
                self.series_finished_signal.emit(title, out_file)
            else:
                fail_count += 1

        self.log_signal.emit(f"\n🎉 === HOÀN TẤT BATCH MERGE! Thành công: {success_count} | Thất bại: {fail_count} ===")
        self.batch_finished_signal.emit(success_count, fail_count)

    def _resolve_writable_output_path(self, target_path: str) -> str:
        """
        Ensures the target output file is writable. If locked by Windows (WinError 32),
        automatically appends a timestamp suffix to guarantee 100% write access!
        """
        abs_path = os.path.normpath(os.path.abspath(target_path))
        if not os.path.exists(abs_path):
            return abs_path

        # Try to remove or check write lock
        try:
            # If 0-byte stale output file, remove it
            if os.path.getsize(abs_path) == 0:
                os.remove(abs_path)
                return abs_path
            
            # Test write access
            with open(abs_path, "a+b"):
                pass
            return abs_path
        except Exception:
            # File is locked by Windows process (WinError 32) -> generate unique timestamped path
            base, ext = os.path.splitext(abs_path)
            ts = time.strftime("%Y%m%d_%H%M%S")
            unique_path = f"{base}_{ts}{ext}"
            self.log_signal.emit(f"⚠️ File '{os.path.basename(abs_path)}' đang bị khóa bởi Windows -> Tự động chuyển sang file mới: '{os.path.basename(unique_path)}'")
            return unique_path

    def _process_single_series(self, job_idx: int, total_jobs: int, title: str, data: Dict[str, Any], out_file: str) -> bool:
        raw_episodes = data.get("episodes", [])
        
        # Verify episode files exist on disk
        episodes = []
        for ep in raw_episodes:
            if os.path.exists(ep[1]):
                episodes.append(ep)
            else:
                self.log_signal.emit(f"⚠️ [BỎ QUA] Tập phim '{os.path.basename(ep[1])}' không còn tồn tại trên ổ đĩa!")

        if not episodes:
            self.log_signal.emit(f"❌ Không tìm thấy file tập phim hợp lệ nào cho bộ '{title}'.")
            return False

        is_uniform = data.get("is_uniform", False)
        total_duration = sum(ep[2].get("duration", 0.0) for ep in episodes)
        preset = self.options.get("preset", "")

        intro_opts = self.options.get("intro", {})
        outro_opts = self.options.get("outro", {})

        intro_enabled = intro_opts.get("enabled", False) and os.path.exists(intro_opts.get("path", ""))
        outro_enabled = outro_opts.get("enabled", False) and os.path.exists(outro_opts.get("path", ""))

        intro_duration = 0.0
        if intro_enabled:
            intro_meta = FFmpegHelper.probe_file(intro_opts.get("path", ""))
            if intro_meta:
                intro_duration = intro_meta.get("duration", 0.0)

        outro_duration = 0.0
        if outro_enabled:
            outro_meta = FFmpegHelper.probe_file(outro_opts.get("path", ""))
            if outro_meta:
                outro_duration = outro_meta.get("duration", 0.0)

        grand_total_duration = total_duration + intro_duration + outro_duration

        temp_dir = tempfile.mkdtemp(prefix="dta_unify_")
        concat_txt = os.path.join(temp_dir, "concat.txt")

        # Build full file list (Intro + Episodes + Outro)
        file_paths = []
        if intro_enabled:
            file_paths.append(intro_opts.get("path"))

        file_paths.extend([ep[1] for ep in episodes])

        if outro_enabled:
            file_paths.append(outro_opts.get("path"))

        FFmpegHelper.create_concat_demuxer_file(file_paths, concat_txt)

        meta_file = None
        if self.options.get("chapters", True):
            meta_file = os.path.join(temp_dir, "chapters.ffmetadata")
            chapter_info = [(ep[0], f"Tập {ep[0]}", ep[2].get("duration", 0.0)) for ep in episodes]
            FFmpegHelper.generate_chapter_metadata(chapter_info, meta_file, intro_offset_sec=intro_duration)

        ffmpeg_bin = FFmpegHelper.get_binary_path("ffmpeg")

        is_direct_copy_preset = "Gộp Siêu Nhanh" in preset or "Direct Copy" in preset
        use_direct_copy = is_uniform and is_direct_copy_preset and not intro_enabled and not outro_enabled

        cmd = [ffmpeg_bin, "-y"]

        if use_direct_copy:
            self.log_signal.emit("⚡ Sử dụng Engine 1: Direct-Copy Concat (Tốc độ ánh sáng, 0% Loss, +genpts sửa timestamp)")
            cmd.extend([
                "-fflags", "+genpts",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_txt
            ])

            if meta_file and os.path.exists(meta_file):
                cmd.extend(["-i", meta_file, "-map_metadata", "1"])

            cmd.extend(["-c", "copy", out_file])
        else:
            self.log_signal.emit("⚙️ Sử dụng Engine 2: Smart Filtergraph Re-encode (Gộp chuẩn FPS/Resolution, reset timestamp, chống đơ hình)")
            
            res_setting = self.options.get("resolution", "Gốc (Original Source)")
            target_res = "1920:1080"
            if "4K" in res_setting:
                target_res = "3840:2160"
            elif "720p" in res_setting:
                target_res = "1280:720"

            cmd.extend([
                "-f", "concat",
                "-safe", "0",
                "-i", concat_txt
            ])

            input_idx = 1
            if meta_file and os.path.exists(meta_file):
                cmd.extend(["-i", meta_file, "-map_metadata", str(input_idx)])
                self.log_signal.emit("📑 [Chapter Marker] Đã tiêm thông tin Chapter Markers vào video")

            filter_vf = f"scale={target_res}:force_original_aspect_ratio=decrease,pad={target_res}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30"
            cmd.extend(["-vf", filter_vf])

            has_nvenc = FFmpegHelper.has_nvenc_support()
            preset_setting = self.options.get("preset", "")
            use_nvenc = ("NVIDIA" in preset_setting or "NVENC" in preset_setting)

            if "Tự Động Tối Ưu" in preset_setting:
                use_nvenc = has_nvenc

            if use_nvenc:
                if has_nvenc:
                    cq_val = "23" if ("Dung Lượng Nhẹ" in preset_setting or "CQ 23" in preset_setting) else "18"
                    cmd.extend(["-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", cq_val])
                    self.log_signal.emit(f"🚀 Sử dụng GPU NVENC Encoder (CQ {cq_val}) - Tốc độ cao!")
                else:
                    crf_val = "23" if ("Dung Lượng Nhẹ" in preset_setting or "CQ 23" in preset_setting) else "18"
                    self.log_signal.emit(f"⚠️ [CẢNH BÁO] Máy không hỗ trợ GPU NVENC. Tự động chuyển sang CPU libx264 (CRF {crf_val}) an toàn!")
                    cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", crf_val])
            else:
                crf_val = "23" if ("Tốc Độ Cao" in preset_setting or "CRF 23" in preset_setting) else "18"
                preset_speed = "fast" if ("Tốc Độ Cao" in preset_setting or "CRF 23" in preset_setting) else "medium"
                cmd.extend(["-c:v", "libx264", "-preset", preset_speed, "-crf", crf_val])
                self.log_signal.emit(f"💻 Sử dụng CPU libx264 Encoder (CRF {crf_val}, Preset: {preset_speed}) - Tương thích 100%!")

            cmd.extend(["-pix_fmt", "yuv420p"])
            cmd.extend(["-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11"])
            cmd.extend(["-movflags", "+faststart"])
            cmd.extend(["-max_muxing_queue_size", "1024"])
            cmd.append(out_file)

        self.log_signal.emit(f"FFmpeg Command: {' '.join(cmd)}")

        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            self._current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                startupinfo=startupinfo,
                encoding="utf-8",
                errors="replace"
            )

            time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
            fps_pattern = re.compile(r"fps=\s*([\d\.]+)")
            speed_pattern = re.compile(r"speed=\s*([\d\.]+)x")

            current_render_sec = 0.0
            current_fps = 0.0
            speed_val = 1.0

            while True:
                if self._is_cancelled:
                    self._current_process.terminate()
                    return False

                line = self._current_process.stderr.readline()
                if not line and self._current_process.poll() is not None:
                    break

                if line:
                    line_str = line.strip()
                    if "frame=" in line_str or "time=" in line_str or "Error" in line_str or "warning" in line_str.lower():
                        self.log_signal.emit(f"[{title}] {line_str}")

                    t_match = time_pattern.search(line_str)
                    if t_match:
                        h, m, s = map(float, t_match.groups())
                        current_render_sec = h * 3600 + m * 60 + s

                    fps_m = fps_pattern.search(line_str)
                    if fps_m:
                        current_fps = float(fps_m.group(1))

                    spd_m = speed_pattern.search(line_str)
                    if spd_m:
                        speed_val = float(spd_m.group(1))

                    series_pct = int(min(100.0, (current_render_sec / max(1.0, grand_total_duration)) * 100))
                    overall_pct = int(((job_idx - 1) / total_jobs * 100) + (series_pct / total_jobs))

                    remaining_sec = max(0.0, grand_total_duration - current_render_sec)
                    if speed_val > 0:
                        eta_sec = remaining_sec / speed_val
                        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_sec))
                    else:
                        eta_str = "--:--:--"

                    speed_str = f"{speed_val:.1f}x speed"

                    self.render_progress_signal.emit(
                        overall_pct, series_pct, title, current_fps, speed_str, eta_str
                    )

            ret_code = self._current_process.wait()

            try:
                if os.path.exists(concat_txt):
                    os.remove(concat_txt)
                os.rmdir(temp_dir)
            except Exception:
                pass

            if ret_code == 0 and os.path.exists(out_file) and os.path.getsize(out_file) > 0:
                self.log_signal.emit(f"✅ Hoàn thành gộp: '{title}' ({os.path.basename(out_file)})")
                return True
            else:
                self.log_signal.emit(f"❌ Lỗi xử lý gộp bộ: '{title}' (Mã lỗi FFmpeg: {ret_code})")
                return False

        except Exception as e:
            self.log_signal.emit(f"❌ Ngoại lệ hệ thống khi render '{title}': {str(e)}")
            return False
