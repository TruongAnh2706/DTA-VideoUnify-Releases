@echo off
title DTA Studio - Release v2.4.3 Auto Push
cd /d "d:\DTA VideoUnify"
echo Pushing Enterprise Release v2.4.3 to GitHub...
git add .
git commit -m "Release v2.4.3: Enterprise Build with Multi-Path FFmpeg Resolution, Auto Downloader, Multi-Series Parsing, and Direct Copy Concat Engine"
git tag -f v2.4.3
git push origin main v2.4.3 -f
git push core main v2.4.3 -f
echo.
echo HOAN TAT DANG TAI TAG V2.4.3 LEN GITHUB!
pause
