from typing import Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip CSRF check for GET/HEAD requests and login endpoint
        if request.method in ["GET", "HEAD"] or request.url.path == "/api/types/user/instances":
            return await call_next(request)

        # Check for CSRF token in headers
        csrf_token = request.headers.get("EMC-CSRF-TOKEN")
        if not csrf_token:
            raise HTTPException(
                status_code=401,
                detail="EMC-CSRF-TOKEN header is required for POST, PATCH and DELETE requests",
            )

        return await call_next(request)
