@echo off
echo.
echo  SpectraAI - Multimodal Product Intelligence Engine
echo  Starting Frontend Dashboard...
echo.
cd /d "%~dp0frontend"
call npm.cmd install --silent 2>nul
call npm.cmd run dev
pause
