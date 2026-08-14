@echo off
title DTA Studio - Release v2.4.2 Auto Push
cd /d "d:\DTA VideoUnify"
echo Pushing Release v2.4.2 to GitHub...
git add .
git commit -m "Release v2.4.2: Fixed PyQt6 Splash Screen Handoff to prevent premature app termination"
git tag -f v2.4.2
git push origin main v2.4.2 -f
git push core main v2.4.2 -f
echo.
echo HOAN TAT DANG TAI TAG V2.4.2 LEN GITHUB!
pause
