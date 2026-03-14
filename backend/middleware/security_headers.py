"""
Security headers middleware — applied globally.
Adds HSTS, Referrer-Policy, X-Frame-Options, and CSP.
"""
import os
from starlette.middleware.base import BaseHTTPMiddleware

# Feature flag: when True, CSP is enforced; when False, report-only
_CSP_ENFORCE = os.environ.get("FEATURE_CSP_ENFORCE", "false").lower() == "true"

CSP_DIRECTIVES = "; ".join([
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://assets.emergent.sh https://us.i.posthog.com https://*.posthog.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: blob: https: http:",
    "connect-src 'self' https: wss:",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
])


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        csp_header = "Content-Security-Policy" if _CSP_ENFORCE else "Content-Security-Policy-Report-Only"
        response.headers[csp_header] = CSP_DIRECTIVES

        return response
