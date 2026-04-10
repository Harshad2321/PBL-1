@echo off
cd /d "%~dp0"
start "" python -m uvicorn api_server:app --host 127.0.0.1 --port 8000
timeout /t 3
echo Backend started on port 8000
