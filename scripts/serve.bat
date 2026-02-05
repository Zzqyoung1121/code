@echo off
setlocal

set PORT=8000
if not "%~1"=="" set PORT=%~1

echo Serving repository at http://localhost:%PORT%
start "" "http://localhost:%PORT%/docs/index.md"
python scripts\serve.py --port %PORT%

endlocal
