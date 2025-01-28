"""Authentication utilities."""

import secrets
from typing import Dict

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


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


async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> Dict[str, str]:
    """Get current user from basic auth credentials.

    Args:
        credentials: Basic auth credentials.

    Returns:
        Dict with username and role.

    Raises:
        HTTPException: If credentials are invalid.
    """
    # Verify credentials
    if verify_password(credentials.password, "Password123!") and credentials.username == "admin":
        return {"username": credentials.username, "role": "admin"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
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
