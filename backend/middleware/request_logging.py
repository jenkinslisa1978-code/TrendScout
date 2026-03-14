"""
Structured request logging + X-Request-ID + X-App-Version middleware.
Logs: request_id, timestamp, method, path, status, latency_ms, user_id.
"""
import os
import time
import uuid
import logging
import json
import jwt
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("request_log")

APP_VERSION = os.environ.get("APP_VERSION", "dev")
JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")

# Paths to skip logging (noisy/health)
_SKIP_PATHS = {"/api/health", "/api/notifications/stream"}


def _extract_user_id(request) -> str:
    """Best-effort extract user_id from Authorization header."""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer ") and JWT_SECRET:
        try:
            payload = jwt.decode(auth[7:], JWT_SECRET, algorithms=["HS256"], options={"verify_exp": False})
            return payload.get("sub", "")
        except Exception:
            pass
    return ""


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Generate or read request ID
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())[:12]

        start = time.monotonic()
        response = await call_next(request)
        latency_ms = round((time.monotonic() - start) * 1000)

        # Attach headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-App-Version"] = APP_VERSION

        # Structured log (skip noisy paths)
        path = request.url.path
        if path not in _SKIP_PATHS:
            user_id = _extract_user_id(request)
            entry = {
                "request_id": request_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "method": request.method,
                "path": path,
                "status": response.status_code,
                "latency_ms": latency_ms,
            }
            if user_id:
                entry["user_id"] = user_id
            logger.info(json.dumps(entry))

        return response
