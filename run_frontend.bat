@echo off
setlocal
echo.
echo ============================================================
echo   SpectraAI - Multimodal Product Intelligence Engine
echo   Starting Frontend Dashboard (Vite on http://localhost:5173)
echo ============================================================
echo.

cd /d "%~dp0frontend"

:: Check if npm is available on PATH
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] npm / Node.js was not found on your PATH.
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo Installing / verifying frontend dependencies...
call npm.cmd install --silent 2>nul

echo Starting Vite development server...
call npm.cmd run dev

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Frontend exited with error code %errorlevel%.
)
pause
