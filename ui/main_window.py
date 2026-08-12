"""
DTA VideoUnify Pro - Main Application Window
3-Column Modern GenZ Studio Layout (Cyberpunk Dark Obsidian Theme)
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Email: ductruong.onl@gmail.com | Zalo/SĐT: 0962775506
Website: https://dta-studio.vercel.app/
Includes Project Removal & Silent Auto-Update Engine (GitHub Releases API)!
"""

import os
import sys
import subprocess
from typing import Dict, Any, List, Tuple
from PyQt6.QtCore import Qt, pyqtSlot, QPoint
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTreeWidget, QTreeWidgetItem, QFileDialog, QGroupBox, QComboBox,
    QCheckBox, QProgressBar, QMessageBox, QFrame, QLineEdit, QSplitter,
    QMenu, QDialog
)
from PyQt6.QtGui import QIcon, QColor, QPixmap, QKeySequence, QShortcut

import config
from ui.styles import MAIN_QSS
from ui.widgets.video_player import InteractiveVideoPlayer
from ui.widgets.drop_zone import DragDropFolderZone
from ui.widgets.log_console import CollapsibleLogConsole
from workers.scanner_worker import FolderScannerThread
from workers.render_worker import BatchRenderThread
from utils.ffmpeg_helper import FFmpegHelper
from utils.updater import UpdateCheckThread, UpdateDownloadThread


class DTAVideoUnifyMainWindow(QMainWindow):
    """
    Main Studio Window of DTA VideoUnify Pro featuring 3-column Layout,
    Interactive 4-Corner Resizable & Draggable Watermark Overlay,
    Cyberpunk Audio Waveform VU Meter, Async FFmpeg Batch Render Engine,
    Item/Series Deletion from Merge Queue, and Silent Auto-Update System.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{config.APP_NAME} - Enterprise v{config.APP_VERSION}")
        self.resize(1420, 900)
        self.setMinimumSize(1200, 780)

        # Set Window Icon
        if os.path.exists(config.LOGO_ICO_PATH):
            self.setWindowIcon(QIcon(config.LOGO_ICO_PATH))
        elif os.path.exists(config.LOGO_PNG_PATH):
            self.setWindowIcon(QIcon(config.LOGO_PNG_PATH))

        # Internal Data Structures
        self.current_source_folder = ""
        self.output_folder = ""
        self.scanned_series_data: Dict[str, Any] = {}
        self.selected_series_title = ""
        self.selected_ep_index = 0
        self.last_rendered_file = ""

        # Threads
        self.scanner_thread: FolderScannerThread = None
        self.render_thread: BatchRenderThread = None
        self.update_check_thread: UpdateCheckThread = None
        self.update_download_thread: UpdateDownloadThread = None

        self._apply_theme()
        self._init_ui()
        self._check_environment()
        self._auto_check_updates_background()

    def _apply_theme(self):
        self.setStyleSheet(MAIN_QSS)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        # Splitter for 3 Columns
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # ==========================================
        # CỘT 1: SIDEBAR TRÁI (MEDIA POOL & GROUPING)
        # ==========================================
        col1_widget = QFrame()
        col1_widget.setObjectName("SidebarFrame")
        col1_layout = QVBoxLayout(col1_widget)
        col1_layout.setContentsMargins(12, 14, 12, 14)
        col1_layout.setSpacing(10)

        # Header Branding Logo & Auto-Update Check Button
        header_box = QHBoxLayout()
        header_box.setSpacing(10)
        logo_img_label = QLabel()
        if os.path.exists(config.LOGO_PNG_PATH):
            pixmap = QPixmap(config.LOGO_PNG_PATH).scaled(
                42, 42, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            logo_img_label.setPixmap(pixmap)
            logo_img_label.setStyleSheet("border-radius: 8px; padding: 2px; border: 1.5px solid #00F2FE;")
        else:
            logo_img_label.setText("🎬")
            logo_img_label.setStyleSheet("font-size: 24px;")
        
        logo_title = QLabel(config.APP_NAME)
        logo_title.setObjectName("AppLogoTitle")

        header_box.addWidget(logo_img_label)
        header_box.addWidget(logo_title)
        header_box.addStretch()

        # Update Check Button
        self.btn_check_update = QPushButton("🔄 Updates")
        self.btn_check_update.setStyleSheet(
            "background-color: #131622; color: #00F2FE; font-weight: 700; font-size: 11px; border: 1px solid #00F2FE; border-radius: 6px; padding: 4px 8px;"
        )
        self.btn_check_update.setToolTip("Kiểm tra bản cập nhật mới từ DTA Studio GitHub Releases")
        self.btn_check_update.clicked.connect(self._manual_check_updates)
        header_box.addWidget(self.btn_check_update)

        col1_layout.addLayout(header_box)

        sub_author = QLabel(config.COPYRIGHT_TEXT)
        sub_author.setStyleSheet("color: #FFD100; font-size: 11px; font-weight: 600; padding-left: 2px;")
        sub_author.setWordWrap(True)
        col1_layout.addWidget(sub_author)

        # Source Selection Button & Compact Drop Zone
        self.btn_select_source = QPushButton("📁 Chọn Thư Mục Nguồn (Select Folder)")
        self.btn_select_source.setObjectName("SecondaryHighlightButton")
        self.btn_select_source.clicked.connect(self._browse_source_folder)
        col1_layout.addWidget(self.btn_select_source)

        # Compact Drop Zone (Max 50px height to maximize tree view space)
        self.drop_zone = DragDropFolderZone()
        self.drop_zone.folder_dropped_signal.connect(self._on_folder_selected)
        col1_layout.addWidget(self.drop_zone)

        # Tree View Header with Delete Button
        tree_header_box = QHBoxLayout()
        label_tree = QLabel("📋 Danh Sách Phim & Tập:")
        label_tree.setStyleSheet("font-weight: 700; color: #00F2FE; font-size: 13px;")

        self.btn_delete_item = QPushButton("🗑️ Xóa Mục Chọn")
        self.btn_delete_item.setStyleSheet(
            "background-color: #FF0055; color: #FFFFFF; font-weight: 700; font-size: 11px; border-radius: 6px; padding: 3px 8px;"
        )
        self.btn_delete_item.setToolTip("Xóa bộ phim hoặc tập phim đang chọn khỏi danh sách gộp")
        self.btn_delete_item.clicked.connect(self._delete_selected_tree_item)

        tree_header_box.addWidget(label_tree, stretch=1)
        tree_header_box.addWidget(self.btn_delete_item)
        col1_layout.addLayout(tree_header_box)

        # Tree View Widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Tên Phim / Tập Phim", "Thông Số / Trạng Thái"])
        self.tree_widget.setColumnWidth(0, 240)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_tree_context_menu)
        self.tree_widget.itemClicked.connect(self._on_tree_item_clicked)
        col1_layout.addWidget(self.tree_widget, stretch=1)

        # Keyboard Delete shortcut for tree widget
        self.shortcut_delete = QShortcut(QKeySequence.StandardKey.Delete, self.tree_widget)
        self.shortcut_delete.activated.connect(self._delete_selected_tree_item)

        # Main Action Button: START BATCH MERGE
        self.btn_start_merge = QPushButton("⚡ BẮT ĐẦU GỘP BỘ (BATCH MERGE)")
        self.btn_start_merge.setObjectName("PrimaryActionButton")
        self.btn_start_merge.clicked.connect(self._start_batch_merge)
        col1_layout.addWidget(self.btn_start_merge)

        # Add Col 1 to Splitter
        main_splitter.addWidget(col1_widget)

        # ==========================================
        # CỘT 2: CENTER AREA (INTERACTIVE PREVIEW PLAYER)
        # ==========================================
        col2_widget = QWidget()
        col2_layout = QVBoxLayout(col2_widget)
        col2_layout.setContentsMargins(4, 0, 4, 0)
        col2_layout.setSpacing(10)

        # Video Player Widget with Audio Waveform VU Meter & 4-Corner Handles Watermark Overlay
        self.player_widget = InteractiveVideoPlayer()
        self.player_widget.prev_requested.connect(self._play_prev_episode)
        self.player_widget.next_requested.connect(self._play_next_episode)
        col2_layout.addWidget(self.player_widget, stretch=1)

        # Selected File Metadata Info Card
        self.info_card = QGroupBox("ℹ️ Thông Tin Tập Phim Đang Chọn")
        self.info_card.setMinimumHeight(115)
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(12, 22, 12, 12)

        self.label_file_info = QLabel("Vui lòng chọn tập phim trong danh sách bên trái để xem thông tin chi tiết.")
        self.label_file_info.setStyleSheet("color: #E2E8F0; font-family: Consolas, monospace; font-size: 12px; line-height: 1.4;")
        self.label_file_info.setWordWrap(True)
        info_layout.addWidget(self.label_file_info)
        col2_layout.addWidget(self.info_card)

        # Add Col 2 to Splitter
        main_splitter.addWidget(col2_widget)

        # ==========================================
        # CỘT 3: SIDEBAR PHẢI (OUTPUT & ENHANCEMENTS)
        # ==========================================
        col3_widget = QFrame()
        col3_widget.setObjectName("SidebarFrame")
        col3_layout = QVBoxLayout(col3_widget)
        col3_layout.setContentsMargins(12, 14, 12, 14)
        col3_layout.setSpacing(14)

        # CARD 1: ⚙️ Cấu Hình Đầu Ra (Output Settings)
        group_output = QGroupBox("⚙️ Cấu Hình Đầu Ra (Output Settings)")
        out_layout = QVBoxLayout(group_output)
        out_layout.setContentsMargins(14, 26, 14, 16)
        out_layout.setSpacing(8)

        # 1. Format
        lbl_fmt = QLabel("Định dạng lưu Video:")
        lbl_fmt.setObjectName("FormLabel")
        out_layout.addWidget(lbl_fmt)

        self.combo_format = QComboBox()
        self.combo_format.addItems(config.OUTPUT_FORMATS)
        self.combo_format.setCurrentText(config.DEFAULT_OUTPUT_FORMAT)
        out_layout.addWidget(self.combo_format)

        # 2. Resolution
        lbl_res = QLabel("Độ phân giải (Resolution):")
        lbl_res.setObjectName("FormLabel")
        out_layout.addWidget(lbl_res)

        self.combo_resolution = QComboBox()
        self.combo_resolution.addItems(config.RESOLUTIONS)
        out_layout.addWidget(self.combo_resolution)

        # 3. Preset Encoder
        lbl_preset = QLabel("Chất lượng Preset (Encoder):")
        lbl_preset.setObjectName("FormLabel")
        out_layout.addWidget(lbl_preset)

        self.combo_preset = QComboBox()
        self.combo_preset.addItems(config.QUALITY_PRESETS)
        out_layout.addWidget(self.combo_preset)

        # 4. Output Directory
        lbl_outdir = QLabel("Thư mục lưu kết quả:")
        lbl_outdir.setObjectName("FormLabel")
        out_layout.addWidget(lbl_outdir)

        dir_box = QHBoxLayout()
        dir_box.setSpacing(6)
        self.txt_out_dir = QLineEdit()
        self.txt_out_dir.setPlaceholderText("Mặc định: Cùng thư mục nguồn")
        self.btn_browse_out = QPushButton("...")
        self.btn_browse_out.setObjectName("BrowseButton")
        self.btn_browse_out.setFixedWidth(42)
        self.btn_browse_out.clicked.connect(self._browse_output_folder)
        dir_box.addWidget(self.txt_out_dir)
        dir_box.addWidget(self.btn_browse_out)
        out_layout.addLayout(dir_box)

        col3_layout.addWidget(group_output, stretch=1)

        # CARD 2: 🎨 Đóng Dấu & Nâng Cao (Clean Enhancements)
        group_advanced = QGroupBox("🎨 Đóng Dấu & Nâng Cao (Enhancements)")
        adv_layout = QVBoxLayout(group_advanced)
        adv_layout.setContentsMargins(14, 26, 14, 16)
        adv_layout.setSpacing(12)

        # Watermark File Picker
        self.chk_watermark = QCheckBox("Bật đóng dấu Logo PNG (Watermark)")
        self.chk_watermark.toggled.connect(self._on_watermark_toggled)
        adv_layout.addWidget(self.chk_watermark)

        wm_file_box = QHBoxLayout()
        wm_file_box.setSpacing(6)
        self.txt_wm_path = QLineEdit()
        self.txt_wm_path.setPlaceholderText("Chọn file logo.png...")
        self.txt_wm_path.textChanged.connect(self._on_watermark_path_changed)
        self.btn_browse_wm = QPushButton("...")
        self.btn_browse_wm.setObjectName("BrowseButton")
        self.btn_browse_wm.setFixedWidth(42)
        self.btn_browse_wm.clicked.connect(self._browse_watermark_file)
        wm_file_box.addWidget(self.txt_wm_path)
        wm_file_box.addWidget(self.btn_browse_wm)
        adv_layout.addLayout(wm_file_box)

        adv_layout.addSpacing(8)

        # Intro/Outro & Chapter Section
        self.chk_intro = QCheckBox("Ghép Video Intro/Outro đầu & cuối phim")
        adv_layout.addWidget(self.chk_intro)

        self.chk_chapters = QCheckBox("Tự động tiêm Chapter Marker MP4/MKV")
        self.chk_chapters.setChecked(True)
        adv_layout.addWidget(self.chk_chapters)

        adv_layout.addStretch()

        col3_layout.addWidget(group_advanced, stretch=1)

        # Add Col 3 to Splitter
        main_splitter.addWidget(col3_widget)

        # Set Splitter Proportions (30% Col1, 44% Col2, 26% Col3)
        main_splitter.setSizes([400, 560, 360])
        root_layout.addWidget(main_splitter, stretch=1)

        # ==========================================
        # BOTTOM STATUS & LOG CONSOLE PANEL
        # ==========================================
        bottom_panel = QWidget()
        bottom_layout = QVBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(6)

        # Global Multi-Task Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        bottom_layout.addWidget(self.progress_bar)

        # Status Bar Info
        self.status_bar_label = QLabel("Sẵn sàng. Vui lòng chọn thư mục chứa video.")
        self.status_bar_label.setStyleSheet("color: #00F2FE; font-weight: 700; font-size: 13px; padding: 2px 4px;")
        bottom_layout.addWidget(self.status_bar_label)

        # Collapsible FFmpeg Log Console
        self.log_console = CollapsibleLogConsole()
        bottom_layout.addWidget(self.log_console)

        root_layout.addWidget(bottom_panel)

    def _check_environment(self):
        """Check if local system has FFmpeg and FFprobe installed."""
        available, msg = FFmpegHelper.check_binaries_available()
        if not available:
            QMessageBox.warning(
                self, "Cảnh báo FFmpeg / FFprobe",
                f"{msg}\n\nỨng dụng yêu cầu FFmpeg & FFprobe để gộp video. Bạn vẫn có thể duyệt giao diện và xem thử video."
            )
            self.log_console.append_log(f"⚠️ [CẢNH BÁO] {msg}")
        else:
            self.log_console.append_log("✅ Hệ thống FFmpeg và FFprobe đã sẵn sàng hoạt động!")

    # ==========================================
    # SILENT AUTO-UPDATE ENGINE INTEGRATION
    # ==========================================

    def _auto_check_updates_background(self):
        """Khởi chạy QThread kiểm tra bản cập nhật ngầm không lag UI khi mở app."""
        self.update_check_thread = UpdateCheckThread()
        self.update_check_thread.update_found_signal.connect(self._on_update_found)
        self.update_check_thread.start()

    def _manual_check_updates(self):
        """Nút bấm kiểm tra cập nhật thủ công."""
        self.btn_check_update.setText("⏳ Đang kiểm tra...")
        self.btn_check_update.setEnabled(False)
        self.log_console.append_log("🔄 Đang kiểm tra bản cập nhật mới trên DTA Studio GitHub Releases...")

        self.update_check_thread = UpdateCheckThread()
        self.update_check_thread.update_found_signal.connect(self._on_update_found)
        self.update_check_thread.no_update_signal.connect(self._on_no_update_found)
        self.update_check_thread.start()

    @pyqtSlot(str, str, str)
    def _on_update_found(self, latest_ver: str, download_url: str, release_notes: str):
        self.btn_check_update.setText("🔴 Có Bản Mới!")
        self.btn_check_update.setStyleSheet(
            "background-color: #FF0055; color: #FFFFFF; font-weight: 800; font-size: 11px; border-radius: 6px; padding: 4px 8px;"
        )
        self.btn_check_update.setEnabled(True)
        self.log_console.append_log(f"🚀 [AUTO-UPDATE] Phát hiện phiên bản mới v{latest_ver}!")

        # Dialog Cập Nhật Ngầm Chuẩn Cyberpunk Dark Studio
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"🎉 Phát Hiện Bản Cập Nhật Mới v{latest_ver} - DTA Studio")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(f"<b>DTA VideoUnify Pro v{latest_ver} đã sẵn sàng!</b>")

        clean_notes = release_notes.replace("\n", "<br>")
        msg_box.setInformativeText(
            f"Phiên bản hiện tại: <b>v{config.APP_VERSION}</b> ➔ Phiên bản mới: <font color='#00F2FE'><b>v{latest_ver}</b></font><br><br>"
            f"<b>Chi tiết cập nhật từ Đức Trường DTA:</b><br>{clean_notes}<br><br>"
            f"<i>Bạn có muốn tải ngầm và tự động nâng cấp ứng dụng ngay không?</i>"
        )

        btn_update_now = msg_box.addButton("🚀 CẬP NHẬT NGAY (SILENT UPDATE)", QMessageBox.ButtonRole.AcceptRole)
        btn_later = msg_box.addButton("Để Sau", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == btn_update_now:
            self._start_silent_update_download(download_url)

    @pyqtSlot(str)
    def _on_no_update_found(self, current_ver: str):
        self.btn_check_update.setText("🔄 Updates")
        self.btn_check_update.setStyleSheet(
            "background-color: #131622; color: #00F2FE; font-weight: 700; font-size: 11px; border: 1px solid #00F2FE; border-radius: 6px; padding: 4px 8px;"
        )
        self.btn_check_update.setEnabled(True)
        self.log_console.append_log(f"✅ Bạn đang sử dụng phiên bản mới nhất v{config.APP_VERSION}.")
        QMessageBox.information(self, "Thông báo Cập Nhật", f"Ứng dụng DTA VideoUnify Pro (v{config.APP_VERSION}) đã ở phiên bản mới nhất!")

    def _start_silent_update_download(self, download_url: str):
        """Kích hoạt QThread tải bản cập nhật ngầm và tự động cài đặt."""
        self.log_console.append_log("⚡ Đang tải bản cập nhật ngầm vào %TEMP%...")
        self.status_bar_label.setText("⚡ Đang tải bản cập nhật ngầm...")
        self.progress_bar.setValue(10)

        self.update_download_thread = UpdateDownloadThread(download_url)
        self.update_download_thread.progress_signal.connect(self._on_update_download_progress)
        self.update_download_thread.finished_signal.connect(self._on_update_download_finished)
        self.update_download_thread.start()

    @pyqtSlot(int, str)
    def _on_update_download_progress(self, pct: int, status_text: str):
        self.progress_bar.setValue(pct)
        self.status_bar_label.setText(status_text)
        if pct % 20 == 0:
            self.log_console.append_log(status_text)

    @pyqtSlot(bool)
    def _on_update_download_finished(self, success: bool):
        if not success:
            self.status_bar_label.setText("❌ Không thể tải bản cập nhật.")
            QMessageBox.critical(self, "Lỗi Cập Nhật", "Không thể tải bản cập nhật từ GitHub. Vui lòng thử lại sau.")

    # ==========================================
    # SLOTS & EVENT HANDLERS
    # ==========================================

    def _browse_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Chứa Video Phim")
        if folder:
            self._on_folder_selected(folder)

    def _browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Lưu Video Kết Quả")
        if folder:
            self.txt_out_dir.setText(folder)
            self.output_folder = folder

    def _browse_watermark_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn File Logo PNG Watermark", "", "Image Files (*.png)")
        if file_path:
            self.txt_wm_path.setText(file_path)
            self.chk_watermark.setChecked(True)
            self._update_player_watermark()

    def _on_watermark_toggled(self, checked: bool):
        self._update_player_watermark()

    def _on_watermark_path_changed(self, text: str):
        if text and os.path.exists(text):
            self.chk_watermark.setChecked(True)
        self._update_player_watermark()

    def _update_player_watermark(self):
        enabled = self.chk_watermark.isChecked()
        path = self.txt_wm_path.text().strip()
        self.player_widget.set_watermark(enabled, path)

    def _on_folder_selected(self, folder_path: str):
        self.current_source_folder = folder_path
        self.btn_select_source.setText(f"📁 Source: {os.path.basename(folder_path)}")
        self.log_console.append_log(f"🔍 Bắt đầu quét thư mục nguồn: '{folder_path}'")

        self.tree_widget.clear()
        self.btn_start_merge.setEnabled(False)

        self.scanner_thread = FolderScannerThread(folder_path)
        self.scanner_thread.progress_signal.connect(self._on_scan_progress)
        self.scanner_thread.finished_signal.connect(self._on_scan_finished)
        self.scanner_thread.error_signal.connect(self._on_scan_error)
        self.scanner_thread.start()

    @pyqtSlot(int, int, str)
    def _on_scan_progress(self, current: int, total: int, status_text: str):
        pct = int((current / max(1, total)) * 100)
        self.progress_bar.setValue(pct)
        self.status_bar_label.setText(f"🔎 {status_text} ({pct}%)")

    @pyqtSlot(dict)
    def _on_scan_finished(self, scanned_data: Dict[str, Any]):
        self.scanned_series_data = scanned_data
        self.progress_bar.setValue(100)
        self.btn_start_merge.setEnabled(True)

        if not scanned_data:
            self.status_bar_label.setText("Không tìm thấy file video hợp lệ trong thư mục này.")
            QMessageBox.information(self, "Thông báo", "Không tìm thấy file video chuẩn trong thư mục được chọn.")
            return

        self._refresh_tree_display()

        # Auto select first episode for preview
        first_series = list(scanned_data.keys())[0]
        if scanned_data[first_series]["episodes"]:
            first_ep = scanned_data[first_series]["episodes"][0]
            self._preview_episode(first_series, 0, first_ep[1], first_ep[2])

    def _refresh_tree_display(self):
        """Re-populates tree widget from self.scanned_series_data."""
        self.tree_widget.clear()

        if not self.scanned_series_data:
            self.status_bar_label.setText("Danh sách gộp trống.")
            self.btn_start_merge.setEnabled(False)
            return

        total_series = len(self.scanned_series_data)
        total_eps = sum(d["total_episodes"] for d in self.scanned_series_data.values())
        self.status_bar_label.setText(f"✅ Hiện có {total_series} bộ phim ({total_eps} tập phim) trong danh sách gộp.")

        for series_title, s_info in self.scanned_series_data.items():
            episodes = s_info.get("episodes", [])
            if not episodes:
                continue

            is_uniform = s_info.get("is_uniform", False)
            total_dur = s_info.get("total_duration", 0.0)

            dur_str = f"{int(total_dur // 3600):02d}:{int((total_dur % 3600) // 60):02d}:{int(total_dur % 60):02d}"
            badge_text = "🟢 Direct Copy Ready" if is_uniform else "🟡 Smart Re-encode Needed"

            # Top-level Series Item
            series_item = QTreeWidgetItem([f"🎬 {series_title} ({len(episodes)} tập)", f"{badge_text} | ⏱ {dur_str}"])
            series_item.setData(0, Qt.ItemDataRole.UserRole, ("series", series_title))
            series_item.setForeground(0, QColor("#00F2FE"))

            for idx, ep_data in enumerate(episodes):
                ep_num = ep_data[0]
                file_path = ep_data[1]
                meta = ep_data[2]

                res_str = f"{meta.get('width')}x{meta.get('height')}"
                fps_str = f"{meta.get('fps')} FPS"
                codec_str = meta.get('v_codec', 'h264')
                file_name = os.path.basename(file_path)

                child_item = QTreeWidgetItem([f"  └ Tập {ep_num}: {file_name}", f"🎥 {res_str} | {fps_str} | {codec_str}"])
                child_item.setData(0, Qt.ItemDataRole.UserRole, ("episode", series_title, idx, file_path, meta))
                series_item.addChild(child_item)

            self.tree_widget.addTopLevelItem(series_item)

        self.tree_widget.expandAll()
        self.btn_start_merge.setEnabled(len(self.scanned_series_data) > 0)

    # ==========================================
    # ITEM/SERIES DELETION FROM QUEUE
    # ==========================================

    def _show_tree_context_menu(self, pos: QPoint):
        item = self.tree_widget.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        menu.setStyleSheet("background-color: #131622; color: #FFFFFF; font-size: 12px;")

        action_delete = menu.addAction("🗑️ Xóa khỏi danh sách gộp (Delete)")
        action_delete.triggered.connect(self._delete_selected_tree_item)

        menu.exec(self.tree_widget.mapToGlobal(pos))

    def _delete_selected_tree_item(self):
        """Deletes selected Series or Episode from the scanned_series_data queue."""
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if not data:
                continue

            item_type = data[0]

            if item_type == "series":
                series_title = data[1]
                if series_title in self.scanned_series_data:
                    del self.scanned_series_data[series_title]
                    self.log_console.append_log(f"🗑️ Đã xóa bộ phim '{series_title}' khỏi danh sách gộp.")

            elif item_type == "episode":
                _, series_title, ep_idx, file_path, _ = data
                if series_title in self.scanned_series_data:
                    s_info = self.scanned_series_data[series_title]
                    episodes = s_info.get("episodes", [])

                    # Find and remove target episode by filepath
                    new_episodes = [ep for ep in episodes if ep[1] != file_path]
                    s_info["episodes"] = new_episodes
                    s_info["total_episodes"] = len(new_episodes)
                    s_info["total_duration"] = sum(ep[2].get("duration", 0.0) for ep in new_episodes)

                    self.log_console.append_log(f"🗑️ Đã xóa tập phim '{os.path.basename(file_path)}' khỏi bộ '{series_title}'.")

                    # If no episodes left, remove series completely
                    if not new_episodes:
                        del self.scanned_series_data[series_title]
                        self.log_console.append_log(f"🗑️ Bộ phim '{series_title}' không còn tập nào và đã được tự động ẩn.")

        self._refresh_tree_display()

    @pyqtSlot(str)
    def _on_scan_error(self, err_msg: str):
        self.status_bar_label.setText(f"❌ {err_msg}")
        QMessageBox.critical(self, "Lỗi quét thư mục", err_msg)

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        if data[0] == "episode":
            _, series_title, ep_idx, file_path, meta = data
            self._preview_episode(series_title, ep_idx, file_path, meta)
        elif data[0] == "series":
            series_title = data[1]
            if series_title in self.scanned_series_data and self.scanned_series_data[series_title]["episodes"]:
                first_ep = self.scanned_series_data[series_title]["episodes"][0]
                self._preview_episode(series_title, 0, first_ep[1], first_ep[2])

    def _preview_episode(self, series_title: str, ep_idx: int, file_path: str, meta: Dict[str, Any]):
        self.selected_series_title = series_title
        self.selected_ep_index = ep_idx

        ep_num = meta.get("ep_num", ep_idx + 1)
        title_disp = f"[{series_title}] Tập {ep_num} - {os.path.basename(file_path)}"
        self.player_widget.load_media(file_path, title_disp)

        # Update metadata info card
        info_text = (
            f"📁 Đường dẫn: {file_path}\n"
            f"🎥 Độ phân giải: {meta.get('width')} x {meta.get('height')} px | Tốc độ khung hình: {meta.get('fps')} FPS\n"
            f"🎞️ Codec Video: {meta.get('v_codec')} ({meta.get('pix_fmt')}) | Codec Audio: {meta.get('a_codec')} ({meta.get('sample_rate')} Hz, {meta.get('channels')} channels)\n"
            f"⏱️ Thời lượng tập: {int(meta.get('duration', 0) // 60):02d}:{int(meta.get('duration', 0) % 60):02d} giây"
        )
        self.label_file_info.setText(info_text)

    def _play_prev_episode(self):
        if not self.selected_series_title or self.selected_series_title not in self.scanned_series_data:
            return
        episodes = self.scanned_series_data[self.selected_series_title]["episodes"]
        if self.selected_ep_index > 0:
            prev_idx = self.selected_ep_index - 1
            ep = episodes[prev_idx]
            self._preview_episode(self.selected_series_title, prev_idx, ep[1], ep[2])

    def _play_next_episode(self):
        if not self.selected_series_title or self.selected_series_title not in self.scanned_series_data:
            return
        episodes = self.scanned_series_data[self.selected_series_title]["episodes"]
        if self.selected_ep_index < len(episodes) - 1:
            next_idx = self.selected_ep_index + 1
            ep = episodes[next_idx]
            self._preview_episode(self.selected_series_title, next_idx, ep[1], ep[2])

    # ==========================================
    # BATCH RENDER EXECUTION & INTERACTIVE WATERMARK
    # ==========================================

    def _start_batch_merge(self):
        if not self.scanned_series_data:
            QMessageBox.warning(self, "Chưa có dữ liệu", "Vui lòng chọn thư mục và quét danh sách tập phim trước!")
            return

        # Prepare Output Directory
        out_dir = self.txt_out_dir.text().strip()
        if not out_dir:
            out_dir = self.current_source_folder

        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi tạo thư mục", f"Không thể tạo thư mục đầu ra: {str(e)}")
                return

        self.output_folder = out_dir

        # Fetch Interactive Draggable Watermark Parameters from Player Widget
        wm_params = self.player_widget.get_watermark_params()

        # Gather Render Options
        selected_ext = self.combo_format.currentText()
        render_options = {
            "output_format": selected_ext,
            "resolution": self.combo_resolution.currentText(),
            "preset": self.combo_preset.currentText(),
            "watermark": wm_params,
            "intro": {
                "enabled": self.chk_intro.isChecked()
            },
            "chapters": self.chk_chapters.isChecked()
        }

        # Build Render Jobs List
        render_jobs: List[Tuple[str, Dict[str, Any], str]] = []
        for title, s_info in self.scanned_series_data.items():
            # Sanitize filename
            clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip()
            out_file_name = f"{clean_title}_FULL{selected_ext}"
            out_filepath = os.path.normpath(os.path.abspath(os.path.join(out_dir, out_file_name)))
            render_jobs.append((title, s_info, out_filepath))

        wm_status_str = f"Có (Tọa độ X:{int(wm_params['rel_x']*100)}%, Y:{int(wm_params['rel_y']*100)}%, Size:{int(wm_params['scale']*100)}%)" if wm_params['enabled'] else "Không"

        confirm_msg = (
            f"Bạn có chắc muốn bắt đầu gộp hàng loạt {len(render_jobs)} bộ phim?\n\n"
            f"• Định dạng lưu: {selected_ext}\n"
            f"• Thư mục lưu: {out_dir}\n"
            f"• Preset: {render_options['preset']}\n"
            f"• Đóng dấu Logo PNG: {wm_status_str}\n"
            f"• Tiêm Chapter Metadata: {'Có' if render_options['chapters'] else 'Không'}"
        )
        reply = QMessageBox.question(self, "Xác nhận Batch Merge", confirm_msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Disable Controls during render
        self.btn_start_merge.setEnabled(False)
        self.btn_select_source.setEnabled(False)

        # Launch Render QThread Worker
        self.render_thread = BatchRenderThread(render_jobs, render_options)
        self.render_thread.render_progress_signal.connect(self._on_render_progress)
        self.render_thread.log_signal.connect(self.log_console.append_log)
        self.render_thread.series_finished_signal.connect(self._on_series_rendered)
        self.render_thread.batch_finished_signal.connect(self._on_batch_render_finished)
        self.render_thread.start()

    @pyqtSlot(int, int, str, float, str, str)
    def _on_render_progress(self, overall_pct: int, series_pct: int, title: str, fps: float, speed_str: str, eta_str: str):
        self.progress_bar.setValue(overall_pct)
        status_msg = f"⚡ Đang gộp phim: '{title}' ({series_pct}%) | Tốc độ: {speed_str} | {fps:.1f} FPS | ETA: {eta_str}"
        self.status_bar_label.setText(status_msg)

    @pyqtSlot(str, str)
    def _on_series_rendered(self, title: str, out_file: str):
        self.last_rendered_file = out_file
        self.log_console.append_log(f"✨ [THÀNH CÔNG] Đã tạo file gộp hoàn chỉnh: {out_file}")

    @pyqtSlot(int, int)
    def _on_batch_render_finished(self, success_count: int, fail_count: int):
        self.progress_bar.setValue(100)
        self.btn_start_merge.setEnabled(True)
        self.btn_select_source.setEnabled(True)

        status_txt = f"🎉 HOÀN TẤT BATCH MERGE! Thành công: {success_count} bộ phim | Thất bại: {fail_count}"
        self.status_bar_label.setText(status_txt)
        self.status_bar_label.setStyleSheet("color: #00E676; font-weight: 800; font-size: 14px; padding: 2px 4px;")

        # Rich Finished Notification Box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("🎉 Render Hoàn Tất - DTA VideoUnify Pro")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(f"<b>Tiến trình Batch Merge đã hoàn thành xuất sắc!</b>")
        msg_box.setInformativeText(
            f"• <b>Thành công:</b> <font color='#00E676'>{success_count}</font> bộ phim<br>"
            f"• <b>Thất bại:</b> <font color='#FF0055'>{fail_count}</font> bộ phim<br><br>"
            f"<b>Thư mục chứa kết quả:</b><br>{self.output_folder}"
        )

        btn_open_folder = msg_box.addButton("📁 Mở Thư Mục Kết Quả", QMessageBox.ButtonRole.ActionRole)
        btn_play_video = None
        if self.last_rendered_file and os.path.exists(self.last_rendered_file):
            btn_play_video = msg_box.addButton("🎬 Xem Video Vừa Gộp", QMessageBox.ButtonRole.ActionRole)
        
        btn_close = msg_box.addButton("Đóng", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == btn_open_folder:
            self._open_output_directory(self.output_folder)
        elif btn_play_video and msg_box.clickedButton() == btn_play_video:
            if self.last_rendered_file and os.path.exists(self.last_rendered_file):
                self.player_widget.load_media(self.last_rendered_file, os.path.basename(self.last_rendered_file))

    def _open_output_directory(self, path: str):
        """Open Windows File Explorer to the target output directory."""
        if not path or not os.path.exists(path):
            return
        try:
            if sys.platform == "win32":
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            self.log_console.append_log(f"⚠️ Không thể mở thư mục Explorer: {str(e)}")
