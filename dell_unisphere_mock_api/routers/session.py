from fastapi import APIRouter, Depends

from .controllers import session_controller
from .models import LoginSessionInfo

router = APIRouter(prefix="/api/types/loginSessionInfo")


@router.get("/instances")
async def get_all_sessions():
    return await session_controller.get_all_sessions()


@router.get("/instances/{id}")
async def get_session(id: str):
    return await session_controller.get_session(id)


@router.post("/instances/{id}/action/logout")
async def logout(id: str):
    return await session_controller.logout(id)
