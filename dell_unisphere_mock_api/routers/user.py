"""User router."""

from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic

from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link

router = APIRouter(prefix="/api/types/user/instances", tags=["user"])
security = HTTPBasic()


@router.get("")
async def get_users(current_user: Dict[str, str] = Depends(get_current_user)) -> ApiResponse:
    """Get all users."""
    entries = []
    for user_id in ["admin"]:
        entry = Entry(
            content={
                "id": f"user_{user_id}",
                "name": user_id,
                "role": "administrator",
                "domain": "Local",
                "is_built_in": True,
                "is_locked": False,
                "password_expiration_date": None,
                "is_password_expired": False,
            },
            links=[
                Link(rel="self", href=f"/api/types/user/instances/{user_id}"),
            ],
        )
        entries.append(entry)

    return ApiResponse(
        base="/api/types/user/instances",
        updated=datetime.utcnow(),
        entries=entries,
    )


@router.get("/{user_id}")
async def get_user(user_id: str, current_user: Dict[str, str] = Depends(get_current_user)) -> ApiResponse:
    """Get a specific user."""
    if user_id != "admin":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )

    entry = Entry(
        content={
            "id": f"user_{user_id}",
            "name": user_id,
            "role": "administrator",
            "domain": "Local",
            "is_built_in": True,
            "is_locked": False,
            "password_expiration_date": None,
            "is_password_expired": False,
        },
        links=[
            Link(rel="self", href=f"/api/types/user/instances/{user_id}"),
        ],
    )

    return ApiResponse(
        base="/api/types/user/instances",
        updated=datetime.utcnow(),
        entries=[entry],
    )
