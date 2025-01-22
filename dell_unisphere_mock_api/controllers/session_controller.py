from typing import List

from fastapi import HTTPException

from .models import LoginSessionInfo


class SessionController:
    def __init__(self):
        self._sessions = {}  # Session storage

    async def get_all_sessions(self) -> List[LoginSessionInfo]:
        return list(self._sessions.values())

    async def get_session(id: str) -> LoginSessionInfo:
        # TODO: Implement single session retrieval logic
        return LoginSessionInfo()

    async def logout(self, session_id: str, localCleanupOnly: bool = False) -> dict:
        if session_id not in self._sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        del self._sessions[session_id]
        return {"logoutOK": "true"}
