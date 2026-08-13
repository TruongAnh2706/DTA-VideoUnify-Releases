@echo off
chcp 65001 > nul
title DTA Studio - GitHub Release v2.3.1 Trigger Engine
color 0A
echo =======================================================================
echo   DTA VIDEOUNIFY PRO - GIT PUSH RELEASE v2.3.1 ENGINE
echo   Phát triển bởi DTA Studio - Chủ quản: Đức Trường
echo =======================================================================
echo.

cd /d "d:\DTA VideoUnify"

echo [1/3] Adding commit and Tag v2.3.1...
git add .
git commit -m "Release v2.3.1: Official Auto-Update Build with Portable Inno Setup Path Fix"
git tag -f v2.3.1

echo.
echo [2/3] Pushing Tag v2.3.1 to GitHub Releases repo...
git push origin main --tags -f

echo.
echo [3/3] Pushing Tag v2.3.1 to GitHub Core repo...
git push core main --tags -f

echo.
echo =======================================================================
echo   🎉 HOÀN TẤT ĐẨY TAG V2.3.1 LÊN GITHUB RELEASES!
echo   Vui lòng kiểm tra tab GitHub Actions trên trình duyệt!
echo =======================================================================
echo.
pause
