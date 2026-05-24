@echo off
cd /d "%~dp0"
echo Probando camara web del computador...
".venv\Scripts\python.exe" scripts\check_webcam.py
pause
