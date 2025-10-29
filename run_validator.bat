@echo off
REM MaxManager Validator - Easy Launch
echo ================================================================================
echo MaxManager Parameter Validator
echo ================================================================================
echo.
echo Starting validation daemon...
echo Dashboard: http://localhost:8888/dashboard.html
echo.
echo Controls:
echo   - Dashboard will auto-open in browser
echo   - Use buttons: Start / Pause / Stop
echo   - Progress is saved automatically
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

REM Start HTTP server in background
start /B python -m http.server 8888 --directory parsers

REM Wait a bit
timeout /t 2 /nobreak > nul

REM Open dashboard
start http://localhost:8888/dashboard.html

REM Run validator daemon
python parsers/validator_daemon.py

pause

