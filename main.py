"""
DTA VideoUnify Pro - Entry Point
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Email: ductruong.onl@gmail.com | Zalo/SĐT: 0962775506
Website: https://dta-studio.vercel.app/
Smooth Splash Screen to Main Window Transition Engine
"""

import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import config
from ui.splash_screen import DTASplashScreen
from ui.main_window import DTAVideoUnifyMainWindow


def main():
    # Set explicit AppUserModelID on Windows so Windows Taskbar uses DTA Logo instead of Python icon
    if sys.platform == "win32":
        try:
            myappid = "dtastudio.videounify.pro.enterprise.2.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setOrganizationName(config.COMPANY_NAME)
    app.setQuitOnLastWindowClosed(True)

    if os.path.exists(config.LOGO_ICO_PATH):
        app.setWindowIcon(QIcon(config.LOGO_ICO_PATH))
    elif os.path.exists(config.LOGO_PNG_PATH):
        app.setWindowIcon(QIcon(config.LOGO_PNG_PATH))

    # Launch SplashScreen first
    splash = DTASplashScreen()
    main_window = None

    def launch_main_app():
        nonlocal main_window
        main_window = DTAVideoUnifyMainWindow()
        main_window.show()
        # Official PyQt6 way to handoff from splash to main window smoothly without quitting app
        splash.finish(main_window)

    splash.app_ready_signal.connect(launch_main_app)
    splash.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
