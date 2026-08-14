@echo off
setlocal
echo.
echo ============================================================
echo   SpectraAI - Multimodal Product Intelligence Engine
echo   Starting Backend Server (FastAPI on http://localhost:8000)
echo ============================================================
echo.

cd /d "%~dp0"

:: Check if .venv exists and activate if found
if exist ".venv\Scripts\activate.bat" (
    echo Activating Python virtual environment (.venv)...
    call ".venv\Scripts\activate.bat"
)

:: Check if python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found on your PATH.
    echo Please install Python 3.12+ and ensure 'Add Python to PATH' is checked.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if uv is available
where uv >nul 2>nul
if %errorlevel% equ 0 (
    echo Installing / verifying backend dependencies via uv...
    uv pip install -r backend\requirements.txt --quiet 2>nul
) else (
    echo Installing / verifying backend dependencies via pip...
    python -m pip install -r backend\requirements.txt --quiet 2>nul
)

cd /d "%~dp0backend"
echo Starting FastAPI server...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Backend exited with error code %errorlevel%.
)
pause
