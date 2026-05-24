@echo off
cd /d "%~dp0"
echo Descargando modelo base YOLO...
".venv\Scripts\python.exe" scripts\download_model.py --model yolo11n.pt
pause
