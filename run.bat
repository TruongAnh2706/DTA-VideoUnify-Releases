@echo off
title DTA VideoUnify Pro Launcher - DTA Studio
color 0A
echo ========================================================
echo     🎬 DTA VIDEOUNIFY PRO - DTA STUDIO (ĐỨC TRƯỜNG)
echo     Email: ductruong.onl@gmail.com | Zalo: 0962.775.506
echo ========================================================
echo.
echo [1/2] Đang kiểm tra môi trường Python & thư viện PyQt6...
python -c "import PyQt6" 2>NUL
if %errorlevel% neq 0 (
    echo ⚙️ Phát hiện chưa có PyQt6. Đang tự động cài đặt PyQt6...
    pip install PyQt6
)

echo.
echo [2/2] Đang khởi chạy DTA VideoUnify Pro...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Có lỗi xảy ra khi khởi chạy. Vui lòng kiểm tra lại log!
    pause
)
