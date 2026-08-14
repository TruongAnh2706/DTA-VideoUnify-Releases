@echo off
title DTA Studio - Release v2.3.4 Auto Push
cd /d "d:\DTA VideoUnify"
echo Pushing Stable Release v2.3.4 to GitHub...
git add .
git commit -m "Release v2.3.4: Stable Enterprise Build with Ultra-Fast Direct Copy, Win32 Unlocking and Mixed-Folder Multi-Series Parsing"
git tag -f v2.3.4
git push origin main v2.3.4 -f
git push core main v2.3.4 -f
echo.
echo HOAN TAT DANG TAI TAG V2.3.4 LEN GITHUB!
pause
