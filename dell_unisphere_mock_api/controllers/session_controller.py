from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import HTTPException

from dell_unisphere_mock_api.models.login_session_info import LoginSessionInfo
from dell_unisphere_mock_api.models.role import Role
from dell_unisphere_mock_api.models.user import User


class SessionController:
    def __init__(self):
        self.sessions = {}
        self.idle_timeout = 1800  # 30 minutes in seconds

    def create_session(self, user: User, roles: List[Role]) -> LoginSessionInfo:
        """Create a new login session."""
        session_id = str(uuid4())
        session = LoginSessionInfo(
            id=session_id,
            domain=user.domain,
            user=user,
            roles=roles,
            idleTimeout=self.idle_timeout,
            isPasswordChangeRequired=user.password_change_required,
            last_activity=datetime.utcnow(),
        )
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[LoginSessionInfo]:
        """Get a session by its ID."""
        return self.sessions.get(session_id)

    def get_all_sessions(self) -> List[LoginSessionInfo]:
        """Get all active sessions."""
        return list(self.sessions.values())

    def validate_session(self, session_id: str) -> bool:
        """Validate if a session is still active."""
        session = self.get_session(session_id)
        if not session:
            return False

        # Check if session has timed out
        last_activity = session.last_activity
        if datetime.utcnow() - last_activity > timedelta(seconds=session.idleTimeout):
            self.delete_session(session_id)
            return False

        # Update last activity
        session.last_activity = datetime.utcnow()
        return True

    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def logout(self, session_id: str, localCleanupOnly: bool = False) -> dict:
        """Logout from a specific session or all sessions."""
        if not self.validate_session(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        if localCleanupOnly:
            self.delete_session(session_id)
        else:
            user_id = self.sessions[session_id].user.id
            self.logout_all_sessions(user_id)

        return {"logoutOK": "true"}

    def logout_all_sessions(self, user_id: str) -> None:
        """Logout all sessions for a specific user."""
        sessions_to_delete = [session_id for session_id, session in self.sessions.items() if session.user.id == user_id]
        for session_id in sessions_to_delete:
            self.delete_session(session_id)
