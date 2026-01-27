import base64
import os
from typing import Optional

import requests
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models


class OcrConfigError(RuntimeError):
    pass


def _read_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _baidu_ocr(image_path: str) -> str:
    api_key = os.getenv("BAIDU_API_KEY")
    secret_key = os.getenv("BAIDU_SECRET_KEY")
    if not api_key or not secret_key:
        raise OcrConfigError("Missing BAIDU_API_KEY or BAIDU_SECRET_KEY")

    token_resp = requests.get(
        "https://aip.baidubce.com/oauth/2.0/token",
        params={
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": secret_key,
        },
        timeout=10,
    )
    token_resp.raise_for_status()
    access_token = token_resp.json().get("access_token")
    if not access_token:
        raise OcrConfigError("Failed to obtain Baidu access token")

    image_base64 = _read_image_base64(image_path)
    ocr_resp = requests.post(
        "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic",
        params={"access_token": access_token},
        data={"image": image_base64, "language_type": "CHN_ENG"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=20,
    )
    ocr_resp.raise_for_status()
    result = ocr_resp.json()
    words = [item.get("words", "") for item in result.get("words_result", [])]
    return " ".join([word for word in words if word]).strip()


def _tencent_ocr(image_path: str) -> str:
    secret_id = os.getenv("TENCENT_SECRET_ID")
    secret_key = os.getenv("TENCENT_SECRET_KEY")
    region = os.getenv("TENCENT_REGION", "ap-beijing")
    if not secret_id or not secret_key:
        raise OcrConfigError("Missing TENCENT_SECRET_ID or TENCENT_SECRET_KEY")

    cred = credential.Credential(secret_id, secret_key)
    http_profile = HttpProfile()
    http_profile.endpoint = "ocr.tencentcloudapi.com"
    client_profile = ClientProfile(httpProfile=http_profile)
    client = ocr_client.OcrClient(cred, region, client_profile)

    req = models.GeneralBasicOCRRequest()
    req.ImageBase64 = _read_image_base64(image_path)
    resp = client.GeneralBasicOCR(req)
    words = [item.DetectedText for item in resp.TextDetections or []]
    return " ".join([word for word in words if word]).strip()

def _self_hosted_ocr(image_path: str) -> str:
    service_url = os.getenv("OCR_SERVICE_URL", "http://127.0.0.1:9000/ocr")
    with open(image_path, "rb") as image_file:
        files = {"file": image_file}
        resp = requests.post(service_url, files=files, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    text = data.get("text") if isinstance(data, dict) else ""
    return text.strip() if text else ""


def recognize_text(image_path: str) -> Optional[str]:
    provider = os.getenv("OCR_PROVIDER", "demo").lower()
    if provider == "demo":
        return None
    if provider == "baidu":
        return _baidu_ocr(image_path)
    if provider == "tencent":
        return _tencent_ocr(image_path)
    if provider in {"self_hosted", "self-hosted"}:
        return _self_hosted_ocr(image_path)
    raise OcrConfigError(f"Unsupported OCR_PROVIDER: {provider}")
