@echo off
title DTA Studio - Release v2.3.3 Trigger Engine
cd /d "d:\DTA VideoUnify"
echo Pushing Release v2.3.3 to GitHub...
git add .
git commit -m "Release v2.3.3: Fixed Inno Setup Action via Choco for 100% CI/CD Build Success"
git tag -f v2.3.3
git push origin main v2.3.3 -f
git push core main v2.3.3 -f
echo.
echo HOAN TAT! F5 TRANG GITHUB ACTIONS HOAC BAM UPDATES TREN APP DE NHAN BAN V2.3.3!
pause
