"""Object storage URL signing helpers (MinIO-compatible endpoint)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import time
from urllib.parse import urlencode

from app.core.config import settings


def _normalize_endpoint(endpoint: str) -> str:
    endpoint = endpoint.strip()
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint.rstrip("/")
    scheme = "https" if settings.MINIO_SECURE else "http"
    return f"{scheme}://{endpoint.rstrip('/')}"


def _sign(method: str, bucket: str, object_name: str, expires_at: int) -> str:
    payload = f"{method}:{bucket}:{object_name}:{expires_at}".encode("utf-8")
    signature = hmac.new(
        settings.MINIO_SECRET_KEY.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).digest()
    return base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")


def _build_url(method: str, object_name: str, bucket_name: str | None = None) -> str:
    bucket = bucket_name or settings.MINIO_BUCKET
    expires_at = int(time.time()) + settings.MINIO_PRESIGNED_EXPIRE_SECONDS
    sig = _sign(method, bucket, object_name, expires_at)
    query = urlencode({"expires": expires_at, "signature": sig, "method": method})
    base = _normalize_endpoint(settings.MINIO_PUBLIC_ENDPOINT or settings.MINIO_ENDPOINT)
    return f"{base}/{bucket}/{object_name}?{query}"


def get_presigned_get_url(object_name: str, bucket_name: str | None = None) -> str:
    return _build_url("GET", object_name, bucket_name)


def get_presigned_put_url(object_name: str, bucket_name: str | None = None) -> str:
    return _build_url("PUT", object_name, bucket_name)
