"""
DTA VideoUnify Pro - Collapsible Console Log Viewer Widget
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QFrame
)


class CollapsibleLogConsole(QWidget):
    """
    Collapsible Console Log Viewer for real-time inspection of FFmpeg command output.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Header Toggle Bar
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #18181C; border: 1px solid #2D2D35; border-radius: 4px;")
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(8, 4, 8, 4)

        self.btn_toggle = QPushButton("▼ Console Log Real-time (FFmpeg Debug Log)")
        self.btn_toggle.setStyleSheet("border: none; background: transparent; color: #00FFFF; font-weight: bold; text-align: left;")
        self.btn_toggle.clicked.connect(self._toggle_console)

        self.btn_clear = QPushButton("Xóa Log")
        self.btn_clear.setFixedWidth(64)
        self.btn_clear.setStyleSheet("font-size: 11px; padding: 2px 6px;")
        self.btn_clear.clicked.connect(self.clear_log)

        h_layout.addWidget(self.btn_toggle, stretch=1)
        h_layout.addWidget(self.btn_clear)
        layout.addWidget(header_frame)

        # Text Console Edit
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setMaximumHeight(140)
        self.log_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #0A0A0C;
                color: #00E676;
                font-family: Consolas, "Courier New", monospace;
                font-size: 11px;
                border: 1px solid #2D2D35;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.log_text_edit)

        self.is_expanded = True

    def _toggle_console(self):
        self.is_expanded = not self.is_expanded
        self.log_text_edit.setVisible(self.is_expanded)
        self.btn_toggle.setText("▼ Console Log Real-time (FFmpeg Debug Log)" if self.is_expanded else "► Console Log Real-time (FFmpeg Debug Log)")

    def append_log(self, text: str):
        self.log_text_edit.append(text)
        # Auto scroll to bottom
        sb = self.log_text_edit.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clear_log(self):
        self.log_text_edit.clear()
