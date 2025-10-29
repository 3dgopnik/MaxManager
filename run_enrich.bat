@echo off
REM Manual enrichment tool
echo ================================================================================
echo MaxManager - Community Enricher
echo ================================================================================
echo.
echo Adding manually curated recommendations to database...
echo.
echo Edit parsers/community_enricher.py to add more recommendations
echo ================================================================================
echo.

python parsers/community_enricher.py

echo.
echo Database updated!
pause

