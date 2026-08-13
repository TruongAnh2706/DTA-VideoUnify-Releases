@echo off
chcp 65001 > nul
echo =========================================================
echo  DTA VIDEOUNIFY PRO - PUSH TAG V2.3.0 TO GITHUB REMOTES
echo  Phát triển bởi DTA Studio - Đức Trường
echo =========================================================
echo.

cd /d "d:\DTA VideoUnify"

echo [1/3] Git Add & Commit...
git add .
git commit -m "release: v2.3.0 - Auto Aspect Ratio Detection & Interactive Watermark Overlay with Opacity Sliders"

echo [2/3] Tagging v2.3.0...
git tag -f v2.3.0

echo [3/3] Pushing to GitHub Remotes...
git push origin main --tags -f
git push core main --tags -f

echo.
echo =========================================================
echo  HOÀN TẤT PUSH TAG V2.3.0 LÊN GITHUB!
echo =========================================================
pause
