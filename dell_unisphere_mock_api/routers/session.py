from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel, Field

from dell_unisphere_mock_api.controllers.session_controller import SessionController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.login_session_info import LoginSessionInfo
from dell_unisphere_mock_api.models.logout_response import LogoutResponse

router = APIRouter()
session_controller = SessionController()


@router.get(
    "/types/loginSessionInfo/instances",
    response_model=ApiResponse[LoginSessionInfo],
    responses={200: {"description": "JSON representation of all members of the loginSessionInfo collection"}},
)
async def get_all_sessions(
    request: Request, response: Response, credentials: HTTPBasicCredentials = Depends(get_current_user)
) -> ApiResponse[LoginSessionInfo]:
    """Get all active login sessions"""
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    return await session_controller.get_all_sessions(request)


@router.get(
    "/types/loginSessionInfo/instances/{session_id}",
    response_model=ApiResponse[LoginSessionInfo],
    responses={200: {"description": "JSON representation of a specific loginSessionInfo instance"}},
)
async def get_session(
    session_id: str, request: Request, response: Response, credentials: HTTPBasicCredentials = Depends(get_current_user)
) -> ApiResponse[LoginSessionInfo]:
    """Get details of a specific login session"""
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    return await session_controller.get_session(session_id, request)


class LogoutRequest(BaseModel):
    localCleanupOnly: bool = Field(
        default=True, description="If true, log out this session only. If false, log out all sessions."
    )


@router.post(
    "/instances/loginSessionInfo/action/logout",
    response_model=ApiResponse[LogoutResponse],
    responses={200: {"description": "JSON representation of the logout response"}},
)
async def logout_session(
    request: Request, response: Response, credentials: HTTPBasicCredentials = Depends(get_current_user)
) -> ApiResponse[LogoutResponse]:
    """Logout from a session or all sessions"""
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    return await session_controller.logout(credentials.username)
