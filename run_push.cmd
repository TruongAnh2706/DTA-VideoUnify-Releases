@echo off
title DTA Studio - Release v2.3.2 Trigger Engine
cd /d "d:\DTA VideoUnify"
echo Pushing Release v2.3.2 to GitHub...
git add .
git commit -m "Release v2.3.2: Ultra-Fast Direct Copy Concat Engine and Fixed GitHub Release Action"
git tag -f v2.3.2
git push origin main v2.3.2 -f
git push core main v2.3.2 -f
echo.
echo HOAN TAT! F5 TRANG GITHUB ACTIONS HOAC BAM UPDATES TREN APP DE NHAN BAN V2.3.2!
pause
