@echo off
cd /d "%~dp0"
echo Activando modo web ESP32...
".venv\Scripts\python.exe" scripts\set_camera_source.py esp32
echo.
echo Ahora inicia el dashboard con INICIAR_DASHBOARD.bat
pause
