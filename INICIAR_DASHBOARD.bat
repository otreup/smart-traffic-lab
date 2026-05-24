@echo off
cd /d "%~dp0"
echo Iniciando Smart Traffic Lab...
echo.
echo Cuando veas "Uvicorn running", abre:
echo http://127.0.0.1:8000
echo.
".venv\Scripts\python.exe" scripts\run_dashboard.py
pause
