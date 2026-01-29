@echo off
setlocal

set ROOT=%~dp0
cd /d %ROOT%

REM Start OCR service in a new window
start "OCR Service" cmd /k "cd /d %ROOT%ocr_service && if not exist .venv (py -3.11 -m venv .venv) && call .venv\Scripts\activate.bat && python -m pip install --upgrade pip && pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 9000"

REM Start backend in a new window with OCR env vars
start "Backend" cmd /k "cd /d %ROOT%backend && if not exist .venv (py -3.11 -m venv .venv) && call .venv\Scripts\activate.bat && python -m pip install --upgrade pip && pip install -r requirements.txt && if not exist data (mkdir data) && set OCR_PROVIDER=self_hosted && set OCR_SERVICE_URL=http://127.0.0.1:9000/ocr && uvicorn app.main:app --reload"

endlocal
