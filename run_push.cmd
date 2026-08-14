@echo off
title DTA Studio - Release v2.3.4 Trigger Engine
cd /d "d:\DTA VideoUnify"
echo Pushing Release v2.3.4 to GitHub...
git add .
git commit -m "Release v2.3.4: Fixed SUPPORTED_VIDEO_EXTS import error in config.py"
git tag -f v2.3.4
git push origin main v2.3.4 -f
git push core main v2.3.4 -f
echo.
echo HOAN TAT! F5 TRANG GITHUB ACTIONS HOAC BAM UPDATES TREN APP DE NHAN BAN V2.3.4!
pause
