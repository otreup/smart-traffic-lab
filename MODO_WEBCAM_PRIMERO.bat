@echo off
cd /d "%~dp0"
echo Activando camara del computador como principal...
".venv\Scripts\python.exe" scripts\set_camera_source.py webcam --webcam-index 0
echo.
echo Ahora inicia el dashboard con INICIAR_DASHBOARD.bat
pause
