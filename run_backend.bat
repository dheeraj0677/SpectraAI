@echo off
echo.
echo  SpectraAI - Multimodal Product Intelligence Engine
echo  Starting Backend Server...
echo.
cd /d "%~dp0backend"
"C:\Users\Dheer\AppData\Local\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt --quiet 2>nul
"C:\Users\Dheer\AppData\Local\Programs\Python\Python312\python.exe" main.py
pause
