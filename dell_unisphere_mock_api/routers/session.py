from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials

from dell_unisphere_mock_api.controllers.session_controller import SessionController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.models.login_session_info import LoginSessionInfo

router = APIRouter(prefix="/api/types/loginSessionInfo", tags=["Session"])

session_controller = SessionController()


@router.get("/instances", response_model=List[LoginSessionInfo])
async def get_all_sessions(credentials: HTTPBasicCredentials = Depends(get_current_user)) -> List[LoginSessionInfo]:
    """Get all active login sessions"""
    return session_controller.get_all_sessions()


@router.get("/instances/{session_id}", response_model=LoginSessionInfo)
async def get_session(
    session_id: str, credentials: HTTPBasicCredentials = Depends(get_current_user)
) -> LoginSessionInfo:
    """Get details of a specific login session"""
    session = session_controller.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/action/logout")
async def logout_session(
    session_id: str, localCleanupOnly: bool = False, credentials: HTTPBasicCredentials = Depends(get_current_user)
) -> dict:
    """Logout from a session or all sessions"""
    try:
        return session_controller.logout(session_id, localCleanupOnly)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
