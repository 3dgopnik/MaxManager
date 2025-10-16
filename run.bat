@echo off
setlocal

set PY=%~dp0\.venv\Scripts\python.exe
if not exist "%PY%" (
  echo Virtualenv Python not found: %PY%
  exit /b 1
)

"%PY%" -m pip install -r "%~dp0%requirements.txt"
"%PY%" "%~dp0%src\main.py"
