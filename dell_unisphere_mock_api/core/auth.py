from datetime import datetime
from typing import Dict, Optional

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from dell_unisphere_mock_api.controllers.session_controller import SessionController

security = HTTPBasic()
session_controller = SessionController()

# Mock user database
MOCK_USERS = {"admin": {"username": "admin", "password": "Password123!", "role": "admin", "domain": "Local"}}


async def get_current_user(
    request: Request, response: Response, credentials: HTTPBasicCredentials = Depends(security)
) -> Dict:
    """Validate credentials and return the current user."""
    if not verify_password(credentials.password, "Password123!"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Check for EMC REST client header
    if not request.headers.get("x-emc-rest-client"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-EMC-REST-CLIENT header is required",
        )

    # Create session for user
    session_controller = SessionController()
    session = await session_controller.create_session(credentials.username, credentials.password)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return {"username": credentials.username, "role": "admin"}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return plain_password == hashed_password  # Mock implementation


def verify_csrf_token(request: Request, response: Response) -> bool:
    """
    Verify the CSRF token in the request.
    Returns True if the token is valid, False otherwise.
    """
    csrf_token = request.headers.get("X-EMC-CSRF-TOKEN")
    if not csrf_token:
        return False

    # In a mock API, we'll accept any non-empty token
    # In a real implementation, this would validate against a stored token
    return True


def generate_csrf_token() -> str:
    """
    Generate a new CSRF token.
    For this mock API, we'll return a static token.
    In a real implementation, this would generate a secure random token.
    """
    return "mock-csrf-token"
