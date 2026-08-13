@echo off
chcp 65001 > nul
title DTA Studio - GitHub Auto Push Engine v2.3.0
color 0A
echo =======================================================================
echo   DTA VIDEOUNIFY PRO - GIT PUSH ENGINE v2.3.0
echo   Phat trien boi DTA Studio - Duc Truong
echo =======================================================================
echo.

cd /d "d:\DTA VideoUnify"

echo [1/3] Git Add, Commit and Tag v2.3.0...
git add .
git commit -m "Release v2.3.0: High-Performance UTF-8 Concat Demuxer Engine and Direct-Copy Speedup"
git tag -f v2.3.0

echo.
echo [2/3] Pushing main branch and v2.3.0 tag to GitHub Releases...
git push origin main --tags -f

echo.
echo [3/3] Pushing main branch and v2.3.0 tag to GitHub Core...
git push core main --tags -f

echo.
echo =======================================================================
echo   HOAN TAT DANG TAI TAG V2.3.0 LEN GITHUB!
echo =======================================================================
echo.
pause
