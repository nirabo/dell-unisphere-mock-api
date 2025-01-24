from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import HTTPException

from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry, Link
from dell_unisphere_mock_api.models.login_session_info import LoginSessionInfo, Role, User
from dell_unisphere_mock_api.models.logout_response import LogoutResponse


class SessionController:
    def __init__(self):
        self.sessions: Dict[str, LoginSessionInfo] = {}
        self.idle_timeout = 3600  # 1 hour in seconds

    def _create_api_response(self, entries: List[Entry], request_path: str) -> ApiResponse:
        """Create standardized API response"""
        base_url = "https://127.0.0.1:8000"  # This should come from configuration
        return ApiResponse(
            **{
                "@base": f"{base_url}{request_path}?per_page=2000",
                "updated": datetime.now(timezone.utc),
                "links": [Link(rel="self", href="&page=1")],
                "entries": entries,
            }
        )

    def _create_entry(self, session: LoginSessionInfo, base_url: str) -> Entry:
        """Create standardized entry"""
        return Entry(
            **{
                "@base": f"{base_url}/api/instances/loginSessionInfo",
                "content": session,
                "links": [Link(rel="self", href=f"/{session.id}")],
                "updated": datetime.now(timezone.utc),
            }
        )

    async def create_session(self, username: str, password: str) -> Optional[LoginSessionInfo]:
        """Create a new login session or return existing one."""
        # Find existing session for this user
        for session in self.sessions.values():
            if session.user.name == username:
                # Update last activity and return existing session
                session.last_activity = datetime.now(timezone.utc)
                return session

        # Create new session if user doesn't have one
        session_id = str(uuid4())
        user = User(id=f"user_{username}", name=username, role="admin", password_change_required=False, domain="Local")
        roles = [Role(id="admin", name="Administrator", description="Full system access")]

        session = LoginSessionInfo(
            id=session_id,
            domain=user.domain,
            user=user,
            roles=roles,
            idleTimeout=self.idle_timeout,
            isPasswordChangeRequired=user.password_change_required,
            last_activity=datetime.now(timezone.utc),
        )
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> ApiResponse:
        """Get a session by its ID."""
        session = self.sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check if session has expired
        if not self.validate_session(session_id):
            raise HTTPException(status_code=401, detail="Session expired")

        entry = self._create_entry(session, "https://127.0.0.1:8000")
        return self._create_api_response([entry], f"/api/instances/loginSessionInfo/{session_id}")

    def get_all_sessions(self) -> ApiResponse:
        """Get all active sessions."""
        # Clean up expired sessions first
        self._cleanup_expired_sessions()

        base_url = "https://127.0.0.1:8000"
        entries = [self._create_entry(session, base_url) for session in self.sessions.values()]
        return self._create_api_response(entries, "/api/types/loginSessionInfo/instances")

    def validate_session(self, session_id: str) -> bool:
        """Validate if a session is still active."""
        session = self.sessions.get(session_id)
        if not session:
            return False

        # Check if session has timed out
        if datetime.now(timezone.utc) - session.last_activity > timedelta(seconds=session.idleTimeout):
            self.delete_session(session_id)
            return False

        # Update last activity
        session.last_activity = datetime.now(timezone.utc)
        return True

    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions."""
        now = datetime.now(timezone.utc)
        expired = [
            session_id
            for session_id, session in self.sessions.items()
            if now - session.last_activity > timedelta(seconds=session.idleTimeout)
        ]
        for session_id in expired:
            self.delete_session(session_id)

    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def logout(self, username: str, localCleanupOnly: bool = True) -> LogoutResponse:
        """Logout from a session or all sessions."""
        if localCleanupOnly:
            # Find and remove session for this user
            for session_id, session in list(self.sessions.items()):
                if session.user.name == username:
                    del self.sessions[session_id]
                    break
        else:
            # Remove all sessions for this user
            for session_id, session in list(self.sessions.items()):
                if session.user.name == username:
                    del self.sessions[session_id]

        return LogoutResponse()
