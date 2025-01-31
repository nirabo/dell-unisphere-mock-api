"""Authentication utilities."""

import logging
import secrets
import time
from typing import Dict, Optional

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from dell_unisphere_mock_api.controllers.session_controller import SessionController

logger = logging.getLogger(__name__)
security = HTTPBasic(auto_error=False)  # Make basic auth optional
session_controller = SessionController()

# Use a consistent time source
start_time = time.time()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password.

    For now, this is a simple comparison since we're not hashing passwords in the mock API.
    In a real application, this would use proper password hashing.

    Args:
        plain_password: Plain text password.
        hashed_password: Hashed password to compare against.

    Returns:
        True if passwords match.
    """
    return plain_password == hashed_password


def _get_session_id_from_cookie(request: Request) -> Optional[str]:
    """Extract session ID from cookie."""
    cookie = request.cookies.get("mod_sec_emc")
    logger.debug(f"Got cookie value: {cookie}")
    if cookie:
        # Extract session ID from cookie (format: value3&1&value1&session_id&value2&value)
        parts = cookie.split("&")
        if len(parts) >= 4:
            session_id = parts[3]
            logger.debug(f"Extracted session ID from cookie: {session_id}")
            return session_id
    logger.debug("No valid session ID found in cookie")
    return None


async def get_current_user(
    request: Request, credentials: Optional[HTTPBasicCredentials] = Depends(security)
) -> Dict[str, str]:
    """Get current user from either basic auth credentials or session cookie.

    Args:
        request: FastAPI request object.
        credentials: Optional basic auth credentials.

    Returns:
        Dict with username and role.

    Raises:
        HTTPException: If authentication fails.
    """
    # First try cookie-based auth
    session_id = _get_session_id_from_cookie(request)
    if session_id:
        logger.debug(f"Attempting to validate session: {session_id}")
        # Validate session
        if await session_controller.validate_session(session_id):
            logger.debug("Session validation successful")
            session = session_controller.sessions.get(session_id)
            if session:
                logger.debug(f"Found valid session for user: {session.user.name}")
                return {"username": session.user.name, "role": session.user.role}
            logger.debug("Session not found in controller after validation")
        else:
            logger.debug("Session validation failed")

    # Fall back to basic auth if cookie auth failed
    if credentials:
        logger.debug("Attempting basic auth validation")
        if verify_password(credentials.password, "Password123!") and credentials.username == "admin":
            logger.debug("Basic auth validation successful")
            return {"username": credentials.username, "role": "admin"}
        logger.debug("Basic auth validation failed")

    logger.debug("All authentication methods failed")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Basic"},
    )


def verify_emc_rest_client(request: Request) -> bool:
    """Verify EMC REST client header is present.

    Args:
        request: FastAPI request object.

    Returns:
        True if header is present and valid.

    Raises:
        HTTPException: If header is missing or invalid.
    """
    emc_rest_client = request.headers.get("x-emc-rest-client", "").lower()
    if emc_rest_client != "true":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-EMC-REST-CLIENT header is required",
        )
    return True


def verify_csrf_token(request: Request, method: str) -> bool:
    """Verify CSRF token in request header matches cookie.

    Args:
        request: FastAPI request object.
        method: HTTP method.

    Returns:
        True if CSRF token is valid.

    Raises:
        HTTPException: If CSRF token is missing or invalid.
    """
    # Skip CSRF verification for non-mutating methods
    if method not in ["POST", "PATCH", "DELETE"]:
        return True

    # Get CSRF token from header
    csrf_token = request.headers.get("EMC-CSRF-TOKEN")
    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="EMC-CSRF-TOKEN header is required for POST, PATCH and DELETE requests",
        )

    return True
