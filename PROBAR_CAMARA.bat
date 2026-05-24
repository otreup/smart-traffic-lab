@echo off
cd /d "%~dp0"
echo Probando ESP32-CAM en http://192.168.1.44 ...
".venv\Scripts\python.exe" scripts\check_camera.py
pause
