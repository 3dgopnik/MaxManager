@echo off
echo ================================================================================
echo MaxManager - Manual Enricher UI
echo ================================================================================
echo.
echo Starting HTTP server...
echo UI: http://localhost:8889/manual_enricher_ui.html
echo.
echo Workflow:
echo   1. Select parameter from list
echo   2. Click search buttons (Autodesk/Forum/Google)
echo   3. Copy-paste info from results
echo   4. Save and Next
echo   5. Export database when done
echo.
echo Press Ctrl+C to stop
echo ================================================================================
echo.

cd parsers
start http://localhost:8889/manual_enricher_ui.html
python -m http.server 8889

pause

