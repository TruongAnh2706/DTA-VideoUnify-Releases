@echo off
title DTA Studio - Fast Auto Update & Git Release Tag
echo ===================================================
echo   DTA STUDIO - GITHUB AUTOMATED RELEASE /UPDATE
echo ===================================================

set /p msg="Nhap mo ta ban cap nhat (Commit message): "
if "%msg%"=="" set msg="Auto update feature and logic optimization"

set /p tag="Nhap Tag phien ban moi (VD: v2.0.1): "
if "%tag%"=="" set tag="v2.0.1"

git add .
git commit -m "%msg%"
git tag %tag%
git push origin main --tags

echo.
echo ===================================================
echo [THANH CONG] Da push code va Tag %tag% len GitHub!
echo He thong CI/CD đang tu dong dong goi va Release ngam.
echo ===================================================
pause
