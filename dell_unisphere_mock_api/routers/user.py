"""User router."""

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic
from pydantic import BaseModel

from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse, Link


class User(BaseModel):
    """User model for Unity API responses."""

    id: str
    name: str
    role: str
    domain: str
    is_built_in: bool
    is_locked: bool
    password_expiration_date: Optional[datetime] = None
    is_password_expired: bool


router = APIRouter(prefix="/types/user/instances", tags=["User"])
security = HTTPBasic()


@router.get("")
async def get_users(request: Request, current_user: Dict[str, str] = Depends(get_current_user)) -> ApiResponse[User]:
    """Get all users."""
    users = []
    for user_id in ["admin"]:
        user = User(
            id=f"user_{user_id}",
            name=user_id,
            role="administrator",
            domain="Local",
            is_built_in=True,
            is_locked=False,
            password_expiration_date=None,
            is_password_expired=False,
        )
        users.append(user)

    formatter = UnityResponseFormatter(request)
    return formatter.format_collection(users)


@router.get("/{user_id}")
async def get_user(
    user_id: str, request: Request, current_user: Dict[str, str] = Depends(get_current_user)
) -> ApiResponse[User]:
    """Get a specific user."""
    if user_id != "admin":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )

    user = User(
        id=f"user_{user_id}",
        name=user_id,
        role="administrator",
        domain="Local",
        is_built_in=True,
        is_locked=False,
        password_expiration_date=None,
        is_password_expired=False,
    )

    formatter = UnityResponseFormatter(request)
    return formatter.format_item(user)
