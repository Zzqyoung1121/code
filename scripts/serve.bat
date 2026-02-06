@echo off
setlocal ENABLEDELAYEDEXPANSION

set SCRIPT_DIR=%~dp0
set HOST=0.0.0.0
set PORT=8000

if not "%~1"=="" set PORT=%~1
if not "%~2"=="" set HOST=%~2

echo [INFO] Starting server on %HOST%:%PORT%

echo [INFO] Local URL: http://localhost:%PORT%/ui/index.html
for /f "tokens=2 delims=:" %%I in ('ipconfig ^| findstr /r /c:"IPv4"') do (
    set IP=%%I
    set IP=!IP: =!
    if not "!IP!"=="" (
        echo [INFO] LAN URL:   http://!IP!:%PORT%/ui/index.html
    )
)

echo [INFO] Tip: allow python.exe in Windows firewall for LAN access.
start "" "http://localhost:%PORT%/ui/index.html"

where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py "%SCRIPT_DIR%serve.py" --host %HOST% --port %PORT%
    goto :end
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    python "%SCRIPT_DIR%serve.py" --host %HOST% --port %PORT%
    goto :end
)

echo [ERROR] Python not found. Please install Python and ensure py or python is in PATH.
exit /b 1

:end
endlocal
