@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" scripts\set_camera_source.py esp32
pause
