"""
DTA VideoUnify Pro - Modern GenZ Cyberpunk Studio QSS Style System
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Color Palette: Electric Cyan (#00F2FE), Bright Gold (#FFD100), Neon Pink (#FF0055), Deep Midnight (#0B0C10), Obsidian Card (#131622)
"""

MAIN_QSS = """
/* =========================================================
   GLOBAL BASE & TYPOGRAPHY
   ========================================================= */
QWidget {
    background-color: #0B0C10;
    color: #F0F3F8;
    font-family: "Segoe UI", "Inter", "Quicksand", sans-serif;
    font-size: 13px;
}

/* Clear transparent backgrounds for labels and text elements */
QLabel {
    background-color: transparent;
    background: transparent;
    color: #E2E8F0;
}

QLabel#FormLabel {
    color: #00F2FE;
    font-weight: 700;
    font-size: 12px;
    margin-top: 8px;
    margin-bottom: 2px;
}

/* =========================================================
   SCROLLBARS
   ========================================================= */
QScrollBar:vertical {
    border: none;
    background: #0E1017;
    width: 7px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #202636;
    min-height: 24px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #00F2FE;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #0E1017;
    height: 7px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background: #202636;
    min-width: 24px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover {
    background: #00F2FE;
}

/* =========================================================
   SIDEBAR FRAMES & PANELS
   ========================================================= */
QFrame#SidebarFrame {
    background-color: #131622;
    border: 1px solid #1F2638;
    border-radius: 12px;
}

/* =========================================================
   GROUPBOXES (GenZ Cards)
   ========================================================= */
QGroupBox {
    background-color: #131622;
    border: 1px solid #1F2638;
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: 700;
    font-size: 13px;
    color: #00F2FE;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 2px 10px;
    background-color: #131622;
    border: 1px solid #00F2FE;
    border-radius: 6px;
    color: #00F2FE;
}

/* =========================================================
   BUTTONS
   ========================================================= */
QPushButton {
    background-color: #191D2C;
    color: #E2E8F0;
    border: 1px solid #283044;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 13px;
    font-weight: 600;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #22283D;
    border-color: #00F2FE;
    color: #00F2FE;
}
QPushButton:pressed {
    background-color: #131622;
}
QPushButton:disabled {
    background-color: #11141F;
    color: #4A5568;
    border-color: #1A202C;
}

QPushButton#BrowseButton {
    background-color: #FFD100;
    color: #0B0C10;
    border: none;
    border-radius: 6px;
    font-weight: 800;
    font-size: 13px;
}
QPushButton#BrowseButton:hover {
    background-color: #FFE055;
    color: #000000;
}

/* Aspect Ratio Mode Switch Buttons */
QPushButton#AspectButton {
    background-color: #0B0C10;
    color: #A0AEC0;
    border: 1px solid #232B3E;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
}
QPushButton#AspectButton:hover {
    border-color: #00F2FE;
    color: #00F2FE;
}
QPushButton#AspectButton[active="true"] {
    background-color: #00F2FE;
    color: #0B0C10;
    border-color: #00F2FE;
    font-weight: 800;
}

/* Primary Action Button (GenZ Neon Pink/Coral Gradient) */
QPushButton#PrimaryActionButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF0055, stop:1 #FF5E00);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.5px;
    padding: 14px 20px;
    min-height: 24px;
}
QPushButton#PrimaryActionButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF2A75, stop:1 #FF7724);
    border: 1px solid #FFD100;
}
QPushButton#PrimaryActionButton:pressed {
    background: #D40045;
}

/* Secondary Highlight Buttons */
QPushButton#SecondaryHighlightButton {
    background-color: #191D2C;
    color: #FFD100;
    border: 1px solid #FFD100;
    border-radius: 8px;
    font-weight: 700;
}
QPushButton#SecondaryHighlightButton:hover {
    background-color: #FFD100;
    color: #0B0C10;
}

/* =========================================================
   FORM CONTROLS (QLineEdit, QComboBox, QSpinBox)
   ========================================================= */
QLineEdit, QComboBox, QSpinBox {
    background-color: #0B0C10;
    color: #F0F3F8;
    border: 1px solid #232B3E;
    border-radius: 8px;
    padding: 7px 12px;
    min-height: 22px;
    font-size: 13px;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #00F2FE;
    background-color: #0F121A;
}
QComboBox::drop-down {
    border: none;
    width: 26px;
    background: transparent;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #FFD100;
    width: 0;
    height: 0;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: #131622;
    color: #F0F3F8;
    selection-background-color: #00F2FE;
    selection-color: #0B0C10;
    border: 1px solid #232B3E;
    border-radius: 6px;
    padding: 4px;
}

/* Checkboxes */
QCheckBox {
    color: #E2E8F0;
    background: transparent;
    background-color: transparent;
    spacing: 8px;
    font-weight: 600;
    margin-top: 4px;
    margin-bottom: 4px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1.5px solid #00F2FE;
    border-radius: 4px;
    background-color: #0B0C10;
}
QCheckBox::indicator:hover {
    border-color: #FFD100;
    background-color: #191D2C;
}
QCheckBox::indicator:checked {
    background-color: #00F2FE;
    border-color: #00F2FE;
    image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%230B0C10'%3E%3Cpath d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/%3E%3C/svg%3E");
}

/* =========================================================
   TREEWIDGET & LISTWIDGET (GENZ DARK THEME)
   ========================================================= */
QTreeWidget, QListWidget {
    background-color: #0B0C10;
    border: 1px solid #1F2638;
    border-radius: 10px;
    padding: 6px;
    outline: none;
}
QHeaderView::section {
    background-color: #191D2C;
    color: #00F2FE;
    font-weight: 700;
    font-size: 12px;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #00F2FE;
}
QTreeWidget::item {
    padding: 8px 6px;
    border-radius: 6px;
    margin-bottom: 2px;
}
QTreeWidget::item:hover {
    background-color: #1A2030;
}
QTreeWidget::item:selected {
    background-color: #222A40;
    color: #00F2FE;
    font-weight: bold;
    border: 1px solid #00F2FE;
}

/* =========================================================
   SLIDERS & PROGRESS BAR
   ========================================================= */
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #191D2C;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00F2FE, stop:1 #FFD100);
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #FFFFFF;
    border: 2px solid #00F2FE;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #FFD100;
    border-color: #FFD100;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

/* Watermark Specific Sliders (Clear transparent background, no borders) */
QSlider#WatermarkSlider {
    background: transparent;
    background-color: transparent;
    border: none;
    outline: none;
    padding: 2px 0px;
}
QSlider#WatermarkSlider::groove:horizontal {
    border: none;
    height: 4px;
    background: #1F2638;
    border-radius: 2px;
}
QSlider#WatermarkSlider::sub-page:horizontal {
    background: #00F2FE;
    border-radius: 2px;
}
QSlider#WatermarkSlider::handle:horizontal {
    background: #FFD100;
    border: 1.5px solid #FFFFFF;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider#WatermarkSlider::handle:horizontal:hover {
    background: #00F2FE;
    border-color: #FFD100;
}

QProgressBar {
    background-color: #0B0C10;
    border: 1px solid #1F2638;
    border-radius: 8px;
    text-align: center;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 11px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00F2FE, stop:0.5 #FFD100, stop:1 #FF0055);
    border-radius: 7px;
}

/* =========================================================
   STATUS BAR & SPECIAL LABELS
   ========================================================= */
QStatusBar {
    background-color: #0B0C10;
    color: #A0AEC0;
    border-top: 1px solid #1F2638;
}
QLabel#AppLogoTitle {
    font-size: 19px;
    font-weight: 900;
    color: #00F2FE;
    letter-spacing: 0.8px;
    background: transparent;
}
"""
