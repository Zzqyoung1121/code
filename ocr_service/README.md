# Self-hosted OCR Service (PaddleOCR)

这是一个独立的 OCR 服务（用于自建模式），提供 `POST /ocr` 接口用于识别上传图片中的文字。

## 运行方式
```bash
cd ocr_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

## Docker 运行方式
```bash
docker build -t homework-ocr-service .
docker run -p 9000:9000 homework-ocr-service
```

## 接口示例
```bash
curl -X POST http://127.0.0.1:9000/ocr \
  -F "file=@cover.jpg"
```
