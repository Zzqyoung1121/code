@echo off
setlocal ENABLEDELAYEDEXPANSION

set SCRIPT_DIR=%~dp0
set HOST=0.0.0.0
set PORT=8000

if not "%~1"=="" set PORT=%~1
if not "%~2"=="" set HOST=%~2

echo [INFO] Starting server on %HOST%:%PORT%
echo [INFO] Local URL: http://localhost:%PORT%/ui/index.html

set LAN_IP=
for /f "tokens=2 delims=:" %%I in ('ipconfig ^| findstr /i "IPv4"') do (
    set CAND=%%I
    set CAND=!CAND: =!
    if not "!CAND!"=="" if /i not "!CAND!"=="127.0.0.1" (
        set LAN_IP=!CAND!
        goto :got_lan
    )
)
:got_lan
if not "%LAN_IP%"=="" (
    echo [INFO] LAN URL:   http://%LAN_IP%:%PORT%/ui/index.html
) else (
    echo [WARN] Failed to detect LAN IP automatically.
)

rem Try to add firewall inbound rule (requires Administrator)
net session >nul 2>nul
if %ERRORLEVEL%==0 (
    netsh advfirewall firewall delete rule name="NOI-Template-Library-%PORT%" >nul 2>nul
    netsh advfirewall firewall add rule name="NOI-Template-Library-%PORT%" dir=in action=allow protocol=TCP localport=%PORT% profile=private >nul 2>nul
    if %ERRORLEVEL%==0 (
        echo [INFO] Firewall rule added for TCP %PORT% (Private profile).
    ) else (
        echo [WARN] Failed to add firewall rule automatically.
    )
) else (
    echo [WARN] Not running as Administrator. If LAN access fails, run CMD as admin and rerun this script.
)

echo [INFO] If still unreachable: ensure both devices are on same LAN and AP isolation is disabled.
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
