import secrets
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class ResponseHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._csrf_tokens = {}

    def _generate_csrf_token(self, session_id: str) -> str:
        token = secrets.token_urlsafe(48)
        self._csrf_tokens[session_id] = token
        return token

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Generate session ID and CSRF token for new sessions
        if request.method == "GET" and "Authorization" in request.headers:
            session_id = secrets.token_urlsafe(32)
            csrf_token = self._generate_csrf_token(session_id)

            # Generate secure cookie value (mocking Dell Unity's format)
            cookie_value = f"value3&1&value1&{session_id}&value2&{secrets.token_hex(32)}"

            # Set required headers
            response.headers["Server"] = "Apache"
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubdomains;"
            response.headers["EMC-CSRF-TOKEN"] = csrf_token
            response.headers["Pragma"] = "no-cache"
            response.headers["Cache-Control"] = "no-cache, no-store, max-age=0"
            response.headers["Expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
            response.headers["Content-Language"] = "en-US"
            response.headers["Vary"] = "Accept-Encoding"
            response.headers["Content-Type"] = "application/json; version=1.0;charset=UTF-8"

            # Set secure cookie
            response.set_cookie(key="mod_sec_emc", value=cookie_value, path="/", secure=True, httponly=True)

        return response
