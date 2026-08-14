@echo off
title DTA Studio - Release v2.4.2 Auto Push
cd /d "d:\DTA VideoUnify"
echo Pushing Stable Release v2.4.2 to GitHub...
git add .
git commit -m "Release v2.4.2: Synchronized Enterprise Build with Direct Copy, Win32 Unlocking and Mixed-Folder Multi-Series Parsing"
git tag -f v2.4.2
git push origin main v2.4.2 -f
git push core main v2.4.2 -f
echo.
echo HOAN TAT DANG TAI TAG V2.4.2 LEN GITHUB!
pause
