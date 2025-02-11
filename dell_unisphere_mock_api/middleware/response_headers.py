"""Response headers middleware for Dell Unity API compatibility."""

import base64
import logging
import secrets
from datetime import timedelta
from typing import Callable, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from dell_unisphere_mock_api.controllers.session_controller import SessionController
from dell_unisphere_mock_api.core.response_models import create_error_response
from dell_unisphere_mock_api.models.login_session_info import LoginSessionInfo

logger = logging.getLogger(__name__)

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
                error_response = create_error_response(
                    error_code=401,
                    http_status_code=401,
                    messages=["Session expired or invalid"]
                )
                return Response(
                    status_code=401,
                    content=error_response.model_dump_json(by_alias=True),
                    media_type="application/json",
                    headers={"Set-Cookie": "mod_sec_emc=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Strict"}
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
                    logger.warning(f"Invalid base64 in basic auth header: {e}")
                except ValueError as e:
                    logger.warning(f"Invalid basic auth format (missing colon): {e}")

        return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add required headers to response."""
        # Get or create session first
        session = await self._get_or_create_session(request)
        if isinstance(session, Response):
            return session

        # Then validate CSRF token for mutating methods if we have a session
        if session and request.method in ["POST", "PATCH", "DELETE"]:
            csrf_token = request.headers.get("EMC-CSRF-TOKEN")
            if not csrf_token:
                error_response = create_error_response(
                    error_code=401,
                    http_status_code=401,
                    messages=["EMC-CSRF-TOKEN header is required"]
                )
                return Response(
                    status_code=401,
                    content=error_response.model_dump_json(by_alias=True),
                    media_type="application/json"
                )

            # Validate that the token matches
            stored_token = self._csrf_tokens.get(session.id)
            if not stored_token or stored_token != csrf_token:
                error_response = create_error_response(
                    error_code=401,
                    http_status_code=401,
                    messages=["Invalid EMC-CSRF-TOKEN"]
                )
                return Response(
                    status_code=401,
                    content=error_response.model_dump_json(by_alias=True),
                    media_type="application/json"
                )

        response = await call_next(request)

        if session:
            # Get or generate CSRF token
            csrf_token = self._get_csrf_token(session.id)

            # Generate secure cookie value (mocking Dell Unity's format)
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

            # Set cookie
            response.set_cookie(
                "mod_sec_emc",
                cookie_value,
                httponly=True,
                secure=True,
                samesite="strict",
                path="/",
            )

        return response
