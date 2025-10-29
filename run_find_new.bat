@echo off
REM Find new parameters not in database
echo ================================================================================
echo MaxManager - Find New Parameters
echo ================================================================================
echo.
echo Searching for parameters not in our database...
echo This will search:
echo   - Autodesk Help documentation
echo   - Autodesk Forums
echo   - Polycount, CGArchitect
echo.
echo Estimated time: ~10 minutes
echo ================================================================================
echo.

python parsers/new_parameter_finder.py

echo.
echo ================================================================================
echo Report saved: parsers/new_parameters_report.json
echo ================================================================================
pause

