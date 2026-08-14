@echo off
title DTA Studio - Release v2.4.1 Auto Push
cd /d "d:\DTA VideoUnify"
echo Pushing Release v2.4.1 to GitHub...
git add .
git commit -m "Release v2.4.1: Non-blocking FFmpeg Warning and Instant Splash Screen Transition Fix"
git tag -f v2.4.1
git push origin main v2.4.1 -f
git push core main v2.4.1 -f
echo.
echo HOAN TAT DANG TAI TAG V2.4.1 LEN GITHUB!
pause
