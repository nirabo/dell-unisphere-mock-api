from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
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
    "/api/types/loginSessionInfo/instances",
    response_model=ApiResponse[LoginSessionInfo],
    responses={200: {"description": "JSON representation of all members of the loginSessionInfo collection"}},
)
async def get_all_sessions(
    response: Response, credentials: HTTPBasicCredentials = Depends(get_current_user)
) -> ApiResponse[LoginSessionInfo]:
    """Get all active login sessions"""
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    return session_controller.get_all_sessions()


@router.get(
    "/api/instances/loginSessionInfo/{session_id}",
    response_model=ApiResponse[LoginSessionInfo],
    responses={200: {"description": "JSON representation of a specific loginSessionInfo instance"}},
)
async def get_session(
    session_id: str, response: Response, credentials: HTTPBasicCredentials = Depends(get_current_user)
) -> ApiResponse[LoginSessionInfo]:
    """Get details of a specific login session"""
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    session = session_controller.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


class LogoutRequest(BaseModel):
    localCleanupOnly: bool = Field(
        default=True, description="If true, log out this session only. If false, log out all sessions."
    )


@router.post(
    "/api/types/loginSessionInfo/action/logout",
    response_model=LogoutResponse,
    responses={200: {"description": "JSON representation of the returned attributes"}},
)
async def logout_session(
    request: LogoutRequest, response: Response, credentials: HTTPBasicCredentials = Depends(get_current_user)
) -> LogoutResponse:
    """Logout from a session or all sessions"""
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"

    try:
        return session_controller.logout(credentials["username"], request.localCleanupOnly)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
