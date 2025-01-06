from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from dell_unisphere_mock_api.core.auth import generate_csrf_token, get_current_user

router = APIRouter()


@router.post("/auth", dependencies=[])  # Remove CSRF token verification for login
async def login(response: Response, current_user: dict = Depends(get_current_user)):
    """Login endpoint that returns a CSRF token."""
    csrf_token = generate_csrf_token()
    print(f"Auth endpoint generating new CSRF token: {csrf_token}")

    # Set token in response header
    response.headers["EMC-CSRF-TOKEN"] = csrf_token

    # Set token in cookie
    response.set_cookie(
        key="emc_csrf_token", value=csrf_token, httponly=False, secure=True, samesite="Lax"  # Allow JavaScript access
    )

    return {"success": True, "csrf_token": csrf_token}
