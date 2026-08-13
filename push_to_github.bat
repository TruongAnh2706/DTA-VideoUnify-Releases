@echo off
chcp 65001 > nul
echo =========================================================
echo  DTA VIDEOUNIFY PRO - PUSH TAG V2.3.0 TO GITHUB REMOTES
echo  Phát triển bởi DTA Studio - Đức Trường
echo =========================================================
echo.

cd /d "d:\DTA VideoUnify"

echo [1/4] Git Add & Commit...
git add .
git commit -m "Release v2.3.0: Ultra-fast UTF-8 Concat Demuxer Engine, Win32 File Unlocking Fix, Fullscreen Studio UI, Intro/Outro Stitching, Auto Chapters"

echo [2/4] Tagging v2.3.0...
git tag -f v2.3.0

echo [3/4] Pushing commits and tags to origin (Releases)...
git push origin main --tags -f

echo [4/4] Pushing commits and tags to core (Core)...
git push core main --tags -f

echo.
echo =========================================================
echo  HOÀN TẤT PUSH TAG V2.3.0 LÊN GITHUB RELEASES!
echo  GitHub Actions sẽ tự động đóng gói file .exe ngay lập tức.
echo =========================================================
timeout /t 5
