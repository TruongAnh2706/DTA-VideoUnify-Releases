"""
DTA VideoUnify Pro - Compact Drag and Drop Zone Widget
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
"""

import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel


class DragDropFolderZone(QFrame):
    """
    Compact Horizontal Drag-and-Drop Frame Widget to minimize vertical space usage
    and maximize space for QTreeWidget episode lists.
    """

    folder_dropped_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMaximumHeight(50)
        self._init_ui()

    def _init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #0E1017;
                border: 1.5px dashed #1F2638;
                border-radius: 8px;
                padding: 4px 8px;
            }
            QFrame:hover {
                border-color: #00F2FE;
                background-color: #131622;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        self.label_icon = QLabel("📁")
        self.label_icon.setStyleSheet("font-size: 18px; border: none; background: transparent;")

        self.label_text = QLabel("Kéo & Thả Thư Mục Vào Đây (Hoặc bấm nút phía trên)")
        self.label_text.setStyleSheet("color: #A0AEC0; font-size: 11px; font-weight: 600; border: none; background: transparent;")

        layout.addWidget(self.label_icon)
        layout.addWidget(self.label_text)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background-color: #191D2C;
                    border: 1.5px dashed #00F2FE;
                    border-radius: 8px;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background-color: #0E1017;
                border: 1.5px dashed #1F2638;
                border-radius: 8px;
            }
        """)

    def dropEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background-color: #0E1017;
                border: 1.5px dashed #1F2638;
                border-radius: 8px;
            }
        """)
        urls = event.mimeData().urls()
        if urls:
            local_path = urls[0].toLocalFile()
            if os.path.isfile(local_path):
                local_path = os.path.dirname(local_path)
            if os.path.isdir(local_path):
                self.folder_dropped_signal.emit(local_path)
