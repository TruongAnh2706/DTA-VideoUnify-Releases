"""
DTA VideoUnify Pro - Batch Render QThread Worker
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Fixed Output File Path Normalization (os.path.normpath) to eliminate Invalid Argument error on Windows.
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

            # Strictly normalize output file path to avoid Windows mix slashes (D:/Test\file.mp4)
            out_file = os.path.normpath(os.path.abspath(raw_out_file))

            self.log_signal.emit(f"\n🎬 [{job_idx}/{total_jobs}] Đang gộp bộ phim: '{title}' -> {out_file}")
            
            success = self._process_single_series(job_idx, total_jobs, title, data, out_file)
            if success:
                success_count += 1
                self.series_finished_signal.emit(title, out_file)
            else:
                fail_count += 1

        self.log_signal.emit(f"\n🎉 === HOÀN TẤT BATCH MERGE! Thành công: {success_count} | Thất bại: {fail_count} ===")
        self.batch_finished_signal.emit(success_count, fail_count)

    def _process_single_series(self, job_idx: int, total_jobs: int, title: str, data: Dict[str, Any], out_file: str) -> bool:
        episodes = data.get("episodes", [])
        is_uniform = data.get("is_uniform", False)
        total_duration = data.get("total_duration", 1.0)
        preset = self.options.get("preset", "Direct Copy (0% Loss - Siêu Nhanh)")

        # Create temporary working folder
        temp_dir = tempfile.mkdtemp(prefix="dta_unify_")
        concat_txt = os.path.join(temp_dir, "concat.txt")
        file_paths = [ep[1] for ep in episodes]
        
        # Writes escaped #ffconcat format
        FFmpegHelper.create_concat_demuxer_file(file_paths, concat_txt)

        # Check Chapter Metadata option
        meta_file = None
        if self.options.get("chapters", False):
            meta_file = os.path.join(temp_dir, "chapters.ffmetadata")
            chapter_info = [(ep[0], f"Tập {ep[0]}", ep[2].get("duration", 0.0)) for ep in episodes]
            FFmpegHelper.generate_chapter_metadata(chapter_info, meta_file)

        ffmpeg_bin = FFmpegHelper.get_binary_path("ffmpeg")

        # Determine if Direct Copy engine can be used safely
        use_direct_copy = is_uniform and ("Direct Copy" in preset) and not self.options.get("watermark", {}).get("enabled") and not self.options.get("intro", {}).get("enabled")

        cmd = []

        if use_direct_copy:
            self.log_signal.emit("⚡ Sử dụng Engine 1: Direct-Copy Concat (Tốc độ ánh sáng, +genpts sửa lỗi timestamp)")
            cmd = [
                ffmpeg_bin, "-y",
                "-fflags", "+genpts",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_txt
            ]

            if meta_file and os.path.exists(meta_file):
                cmd.extend(["-i", meta_file, "-map_metadata", "1"])

            cmd.extend(["-c", "copy", out_file])
        else:
            self.log_signal.emit("⚙️ Sử dụng Engine 2: Smart Filtergraph Re-encode (Gộp từng input, setpts reset timestamp chống đơ hình)")
            cmd = self._build_robust_reencode_command(ffmpeg_bin, file_paths, out_file, meta_file)

        # Log command line execution
        self.log_signal.emit(f"FFmpeg Command: {' '.join(cmd)}")

        # Execute FFmpeg Subprocess
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

            # Regex for parsing ffmpeg progress
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
                    if "frame=" in line_str or "time=" in line_str or "Error" in line_str:
                        self.log_signal.emit(f"[{title}] {line_str}")

                    # Parse frame progress
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

                    # Calculate progress percentages
                    series_pct = int(min(100.0, (current_render_sec / max(1.0, total_duration)) * 100))
                    overall_pct = int(((job_idx - 1) / total_jobs * 100) + (series_pct / total_jobs))

                    # Calculate ETA
                    remaining_sec = max(0.0, total_duration - current_render_sec)
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

            # Cleanup temp files
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

    def _build_robust_reencode_command(self, ffmpeg_bin: str, file_paths: List[str], out_file: str, meta_file: Optional[str]) -> List[str]:
        """
        Constructs a robust FFmpeg filtergraph re-encoding command.
        """
        res_setting = self.options.get("resolution", "Gốc (Original Source)")
        preset_setting = self.options.get("preset", "High Quality NVENC (CQ 18 - Khuyên Dùng)")
        watermark = self.options.get("watermark", {})

        cmd = [ffmpeg_bin, "-y"]

        # Add all episode input files individually
        for path in file_paths:
            cmd.extend(["-i", path])

        num_inputs = len(file_paths)
        inputs_count = num_inputs

        # Add watermark input if enabled
        wm_enabled = watermark.get("enabled", False) and os.path.exists(watermark.get("path", ""))
        wm_input_index = -1
        if wm_enabled:
            cmd.extend(["-i", watermark.get("path")])
            wm_input_index = inputs_count
            inputs_count += 1

        # Add chapter metadata input
        if meta_file and os.path.exists(meta_file):
            cmd.extend(["-i", meta_file, "-map_metadata", str(inputs_count)])

        # Target resolution calculation
        target_res = "1920:1080"
        if "4K" in res_setting:
            target_res = "3840:2160"
        elif "720p" in res_setting:
            target_res = "1280:720"

        scale_filter = f"scale={target_res}:force_original_aspect_ratio=decrease,pad={target_res}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30,setpts=PTS-STARTPTS"

        filter_chains = []
        concat_inputs = ""

        # Process each episode input to unify resolution, FPS, and reset timestamps
        for i in range(num_inputs):
            v_in = f"[{i}:v]"
            a_in = f"[{i}:a]"
            v_out = f"[v{i}]"
            a_out = f"[a{i}]"

            filter_chains.append(f"{v_in}{scale_filter}{v_out}")
            filter_chains.append(f"{a_in}aresample=async=1,asetpts=PTS-STARTPTS{a_out}")
            concat_inputs += f"{v_out}{a_out}"

        # Concat all normalized streams together
        filter_chains.append(f"{concat_inputs}concat=n={num_inputs}:v=1:a=1[v_merged][a_merged]")

        final_v_label = "[v_merged]"

        # Apply interactive Watermark Overlay if enabled
        if wm_enabled:
            rel_x = watermark.get("rel_x", 0.75)
            rel_y = watermark.get("rel_y", 0.05)
            scale = watermark.get("scale", 0.18)
            opacity = watermark.get("opacity", 0.8)

            wm_filter = f"[{wm_input_index}:v]scale=main_w*{scale}:-1,format=rgba,colorchannelmixer=aa={opacity}[wm_scaled];[v_merged][wm_scaled]overlay=main_w*{rel_x}:main_h*{rel_y}[v_wm]"
            filter_chains.append(wm_filter)
            final_v_label = "[v_wm]"

        filter_complex_str = ";".join(filter_chains)

        cmd.extend(["-filter_complex", filter_complex_str, "-map", final_v_label, "-map", "[a_merged]"])

        # Encoder selection (NVENC GPU vs CPU)
        if "NVENC" in preset_setting:
            cmd.extend(["-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "18"])
        else:
            cmd.extend(["-c:v", "libx264", "-preset", "medium", "-crf", "18"])

        # Audio normalization & encoding
        cmd.extend(["-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11"])

        cmd.append(out_file)
        return cmd
