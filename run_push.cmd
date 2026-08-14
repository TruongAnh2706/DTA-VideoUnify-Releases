@echo off
title DTA Studio - Release v2.4.0 Trigger Engine
cd /d "d:\DTA VideoUnify"
echo Pushing Release v2.4.0 to GitHub...
git add .
git commit -m "Release v2.4.0: Universal Multi-Series Title and Episode Regex Parser for Mixed Single Folders"
git tag -f v2.4.0
git push origin main v2.4.0 -f
git push core main v2.4.0 -f
echo.
echo HOAN TAT! F5 TRANG GITHUB ACTIONS HOAC BAM UPDATES TREN APP DE NHAN BAN V2.4.0!
pause
