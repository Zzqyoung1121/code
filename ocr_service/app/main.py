import io
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

try:
    from paddleocr import PaddleOCR
except ImportError:  # pragma: no cover
    PaddleOCR = None

app = FastAPI(title="Self-hosted OCR Service")
ocr_engine = None


def _get_engine():
    global ocr_engine
    if ocr_engine is None:
        if PaddleOCR is None:
            raise HTTPException(status_code=500, detail="PaddleOCR is not installed")
        ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch")
    return ocr_engine


def _extract_text(result: List) -> str:
    words = []
    for line in result:
        for item in line:
            if isinstance(item, list) and len(item) > 1:
                words.append(item[1][0])
    return " ".join([word for word in words if word]).strip()


@app.post("/ocr")
async def recognize(file: UploadFile = File(...)):
    if PaddleOCR is None:
        raise HTTPException(status_code=500, detail="PaddleOCR is not installed")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    engine = _get_engine()
    result = engine.ocr(io.BytesIO(content), cls=True)
    text = _extract_text(result)
    return {"text": text}


@app.get("/")
def root():
    return JSONResponse({"status": "ok", "service": "self-hosted-ocr"})
