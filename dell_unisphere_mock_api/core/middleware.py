import secrets
from typing import Optional

from fastapi import HTTPException, Request


class UnityAuthMiddleware:
    def __init__(self):
        self.csrf_tokens = {}

    async def __call__(self, request: Request, call_next):
        # Verify required headers
        if not request.headers.get("X-EMC-REST-CLIENT"):
            raise HTTPException(403, "X-EMC-REST-CLIENT header required")

        # CSRF protection for write operations
        if request.method in ("POST", "PUT", "DELETE"):
            csrf_token = request.headers.get("EMC-CSRF-TOKEN")
            session_id = request.cookies.get("EMC-SESSION-ID")

            if not csrf_token or not self._validate_csrf(session_id, csrf_token):
                raise HTTPException(403, "Invalid CSRF token")

        response = await call_next(request)

        # Set initial CSRF token for new sessions
        if request.method == "GET" and not request.cookies.get("EMC-SESSION-ID"):
            session_id = secrets.token_urlsafe(16)
            new_csrf = self._generate_csrf_token(session_id)
            response.set_cookie(key="EMC-SESSION-ID", value=session_id, httponly=True)
            response.headers["EMC-CSRF-TOKEN"] = new_csrf

        return response

    def _generate_csrf_token(self, session_id: str) -> str:
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[session_id] = token
        return token

    def _validate_csrf(self, session_id: Optional[str], token: str) -> bool:
        if not session_id:
            return False
        return secrets.compare_digest(token, self.csrf_tokens.get(session_id, ""))
