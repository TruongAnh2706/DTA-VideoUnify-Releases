"""
DTA VideoUnify Pro - Scanner QThread Worker
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
"""

import os
from PyQt6.QtCore import QThread, pyqtSignal
from parser.regex_engine import SeriesRegexParser
from utils.ffmpeg_helper import FFmpegHelper
from typing import Dict, Any


class FolderScannerThread(QThread):
    """
    Background QThread to scan directory, parse series/episodes,
    and auto-inspect stream metadata using FFprobe without blocking UI.
    """

    # Signals
    progress_signal = pyqtSignal(int, int, str)  # current, total, status_text
    finished_signal = pyqtSignal(dict)           # scanned series data dictionary
    error_signal = pyqtSignal(str)

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            self.progress_signal.emit(0, 100, "Đang quét danh sách file trong thư mục...")
            series_dict = SeriesRegexParser.scan_directory(self.folder_path)

            if not series_dict:
                self.finished_signal.emit({})
                return

            total_episodes = sum(len(eps) for eps in series_dict.values())
            processed_count = 0

            inspected_result: Dict[str, Any] = {}

            for series_title, ep_tuples in series_dict.items():
                if self._is_cancelled:
                    return

                episodes_data = []
                metadata_list = []
                total_duration = 0.0

                for ep_num, file_path in ep_tuples:
                    if self._is_cancelled:
                        return

                    processed_count += 1
                    file_name = os.path.basename(file_path)
                    self.progress_signal.emit(
                        processed_count,
                        total_episodes,
                        f"Đang kiểm tra FFprobe: [{series_title}] Tập {ep_num} ({file_name})"
                    )

                    meta = FFmpegHelper.probe_file(file_path)
                    if meta:
                        episodes_data.append((ep_num, file_path, meta))
                        metadata_list.append(meta)
                        total_duration += meta.get("duration", 0.0)
                    else:
                        # Fallback dummy meta if probe failed
                        dummy_meta = {
                            "file_path": file_path, "duration": 0.0, "width": 1920, "height": 1080,
                            "v_codec": "h264", "fps": 30.0, "a_codec": "aac", "sample_rate": 44100, "channels": 2
                        }
                        episodes_data.append((ep_num, file_path, dummy_meta))

                # Check if all episodes in this series share identical properties
                is_uniform = FFmpegHelper.check_series_uniformity(metadata_list)

                inspected_result[series_title] = {
                    "episodes": episodes_data,
                    "is_uniform": is_uniform,
                    "total_duration": total_duration,
                    "total_episodes": len(episodes_data)
                }

            self.progress_signal.emit(total_episodes, total_episodes, "Hoàn tất quét & kiểm tra metadata!")
            self.finished_signal.emit(inspected_result)

        except Exception as e:
            self.error_signal.emit(f"Lỗi khi quét thư mục: {str(e)}")
