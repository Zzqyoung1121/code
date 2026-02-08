@echo off
setlocal EnableExtensions

echo %CMDCMDLINE% | findstr /i /c:"/c" >nul 2>nul
if %ERRORLEVEL%==0 if not defined SERVE_BAT_INTERACTIVE (
    set SERVE_BAT_INTERACTIVE=1
    cmd /k ""%~f0" %*"
    exit /b 0
)

set "SCRIPT_DIR=%~dp0"
set "HOST=0.0.0.0"
set "PORT=8000"

if not "%~1"=="" set "PORT=%~1"
if not "%~2"=="" set "HOST=%~2"

echo [INFO] Starting server on %HOST%:%PORT%
echo [INFO] Python will print Local/LAN URLs after startup.

where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py "%SCRIPT_DIR%serve.py" --host %HOST% --port %PORT% --open
    goto :end
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    python "%SCRIPT_DIR%serve.py" --host %HOST% --port %PORT% --open
    goto :end
)

echo [ERROR] Python not found. Please install Python and ensure py or python is in PATH.
echo [HINT] You can run:  py --version  or  python --version
pause
exit /b 1

:end
if defined SERVE_BAT_INTERACTIVE (
    echo.
    echo [INFO] Server exited. Press any key to close.
    pause >nul
)
endlocal
goto :eof
