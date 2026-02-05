@echo off
setlocal

set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..

set PORT=8000
if not "%~1"=="" set PORT=%~1

echo Serving repository at http://localhost:%PORT%
start "" "http://localhost:%PORT%/ui/index.html"

where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py "%SCRIPT_DIR%serve.py" --port %PORT%
    goto :end
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    python "%SCRIPT_DIR%serve.py" --port %PORT%
    goto :end
)

echo [ERROR] Python not found. Please install Python and ensure py or python is in PATH.
exit /b 1

:end
endlocal
