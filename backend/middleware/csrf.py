"""
CSRF protection middleware — double-submit cookie pattern.
Only applies to cookie-authenticated state-changing routes (POST/PUT/DELETE).
Skips bearer-only APIs and Stripe webhooks.
"""
import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Paths exempt from CSRF (webhooks, public endpoints)
CSRF_EXEMPT_PATHS = {
    "/api/stripe/webhook",
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/refresh",
    "/api/auth/logout",
    "/api/auth/login-submit",
    "/api/auth/signup-submit",
    "/api/auth/forgot-password",
    "/api/auth/reset-password",
}

# Only enforce CSRF on routes that use cookie auth
CSRF_COOKIE_NAME = "__Host-csrf"
CSRF_HEADER_NAME = "x-csrf-token"


def generate_csrf_token():
    return secrets.token_urlsafe(32)


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Only check state-changing methods
        if request.method in ("GET", "HEAD", "OPTIONS"):
            response = await call_next(request)
            # Set CSRF cookie if not present
            if CSRF_COOKIE_NAME not in request.cookies:
                token = generate_csrf_token()
                response.set_cookie(
                    key=CSRF_COOKIE_NAME,
                    value=token,
                    httponly=False,  # JS must read it
                    secure=True,
                    samesite="lax",
                    path="/",
                )
            return response

        path = request.url.path

        # Skip exempt paths
        if path in CSRF_EXEMPT_PATHS:
            return await call_next(request)

        # Only enforce CSRF on cookie-authenticated requests
        refresh_cookie = request.cookies.get("__Host-refresh")
        if not refresh_cookie:
            # Bearer-only request, no CSRF needed
            return await call_next(request)

        # Validate CSRF token: header must match cookie
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)

        if not cookie_token or not header_token or cookie_token != header_token:
            return JSONResponse(
                status_code=403,
                content={"success": False, "error": {"code": "CSRF_INVALID", "message": "CSRF token validation failed"}},
            )

        return await call_next(request)
