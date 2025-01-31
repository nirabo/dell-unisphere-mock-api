"""Response headers middleware for Dell Unity API compatibility.

This middleware handles session management and response headers to ensure compatibility
with the Dell Unity REST API specification. It manages:

1. Session Management:
   - Creates new sessions when Basic Auth credentials are provided
   - Validates and retrieves existing sessions from cookies
   - Sets session cookies in responses with proper security attributes
   - Maintains session state using the singleton SessionController

2. Cookie Management:
   - Sets 'mod_sec_emc' cookie with session information
   - Format: value3&1&value1&session_id&value2&csrf_token
   - Security attributes: HttpOnly, Secure, SameSite=Strict
   - Expiry based on session idle timeout

3. CSRF Protection:
   - Generates and validates CSRF tokens
   - Requires EMC-CSRF-TOKEN header for mutating requests
   - Token is tied to session ID for security

4. Response Headers:
   - Sets Dell Unity specific headers
   - Handles caching directives
   - Sets security headers
   - Manages content type and language

Authentication Flow:
1. Client sends request
2. Middleware checks for existing session cookie
3. If cookie exists:
   - Extracts session ID
   - Validates session via SessionController
   - If valid, request proceeds
   - If invalid, falls back to Basic Auth
4. If Basic Auth present:
   - Creates new session
   - Sets session cookie
5. If no valid auth, request fails with 401

Example Usage:
```python
app = FastAPI()
app.add_middleware(ResponseHeaderMiddleware)

# Protected route using session auth
@app.get("/api/types/user/instances")
async def get_users():
    # Will only reach here if session is valid
    return {"users": [...]}
```
"""

import base64
import logging
import secrets
from datetime import timedelta
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from dell_unisphere_mock_api.controllers.session_controller import SessionController
from dell_unisphere_mock_api.models.login_session_info import LoginSessionInfo


class ResponseHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._csrf_tokens = {}
        self._session_controller = SessionController()

    def _generate_csrf_token(self, session_id: str) -> str:
        token = secrets.token_urlsafe(48)
        self._csrf_tokens[session_id] = token
        return token

    def _get_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from cookie."""
        cookie = request.cookies.get("mod_sec_emc")
        if cookie:
            # Extract session ID from cookie (format: value3&1&value1&session_id&value2&value)
            parts = cookie.split("&")
            if len(parts) >= 4:
                session_id = parts[3]
                if session_id:
                    return session_id
        return None

    def _get_csrf_token(self, session_id: str) -> str:
        """Get existing CSRF token or generate a new one."""
        csrf_token = self._csrf_tokens.get(session_id)
        if csrf_token is None:
            csrf_token = self._generate_csrf_token(session_id)
        return csrf_token

    async def _get_or_create_session(self, request: Request) -> Optional[LoginSessionInfo]:
        """Get existing session or create a new one if basic auth is present."""
        session_id = self._get_session_id(request)

        if session_id:
            # Try to get existing session
            if await self._session_controller.validate_session(session_id):
                session = self._session_controller.sessions.get(session_id)
                if session:
                    return session
            # If session is invalid and there's no basic auth, return 401
            elif "Authorization" not in request.headers:
                return Response(
                    status_code=401,
                    content=(
                        '{"errorCode": 401, "httpStatusCode": 401, ' '"messages": ["Session expired or invalid"]}'
                    ),
                    media_type="application/json",
                    headers={"Set-Cookie": "mod_sec_emc=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Strict"},
                )

        # Create new session if basic auth is present
        if "Authorization" in request.headers and request.method == "GET":
            # Extract username from basic auth
            auth = request.headers["Authorization"]
            if auth.startswith("Basic "):
                try:
                    credentials = base64.b64decode(auth[6:]).decode("utf-8")
                    username, password = credentials.split(":")
                    session = await self._session_controller.create_session(username, password)
                    if session:
                        return session
                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    logging.warning(f"Invalid base64 in basic auth header: {e}")
                except ValueError as e:
                    logging.warning(f"Invalid basic auth format (missing colon): {e}")

        return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add required headers to response."""
        # First validate CSRF token for mutating methods
        if request.method in ["POST", "PATCH", "DELETE"]:
            csrf_token = request.headers.get("EMC-CSRF-TOKEN")
            if not csrf_token:
                return Response(
                    status_code=401,
                    content=(
                        '{"errorCode": 401, "httpStatusCode": 401, '
                        '"messages": ["EMC-CSRF-TOKEN header is required"]}'
                    ),
                    media_type="application/json",
                )

        session = await self._get_or_create_session(request)
        if isinstance(session, Response):
            return session

        response = await call_next(request)

        if session:
            # Get or generate CSRF token
            csrf_token = self._get_csrf_token(session.id)

            # Generate secure cookie value (mocking Dell Unity's format)
            # Use the session ID from the session object
            cookie_value = f"value3&1&value1&{session.id}&value2&{secrets.token_hex(32)}"

            # Set required headers
            response.headers["Server"] = "Apache"
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubdomains;"
            response.headers["EMC-CSRF-TOKEN"] = csrf_token
            response.headers["Pragma"] = "no-cache"
            response.headers["Cache-Control"] = "no-cache, no-store, max-age=0"

            # Use session's expiry time
            expires = session.last_activity + timedelta(seconds=session.idleTimeout)
            response.headers["Expires"] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
            response.headers["Content-Language"] = "en-US"
            response.headers["Vary"] = "Accept-Encoding"
            response.headers["Content-Type"] = "application/json; version=1.0;charset=UTF-8"

            # Set cookie with same expiry
            response.set_cookie(
                "mod_sec_emc",
                cookie_value,
                expires=expires,
                httponly=True,
                secure=True,
                samesite="strict",
                path="/",
            )

        return response
