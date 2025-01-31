"""Session controller for managing user sessions."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from uuid import uuid4

from fastapi import HTTPException, Request

from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.models.login_session_info import LoginSessionInfo, Role, User
from dell_unisphere_mock_api.models.logout_response import LogoutResponse

logger = logging.getLogger(__name__)


class SessionController:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            logger.debug("Creating new SessionController instance")
            cls._instance = super(SessionController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            logger.debug("Initializing SessionController")
            self.sessions: Dict[str, LoginSessionInfo] = {}
            self.idle_timeout = 3600  # 1 hour in seconds
            self._initialized = True

    async def create_session(self, username: str, password: str) -> Optional[LoginSessionInfo]:
        """Create a new login session or return existing one."""
        logger.debug(f"Creating session for user: {username}")
        # Find existing session for this user
        for session in list(self.sessions.values()):
            if session.user.name == username:
                # Check if session is still valid
                if await self.validate_session(session.id):
                    # Update last activity and return existing session
                    logger.debug(f"Found existing valid session for user: {username}")
                    session.last_activity = datetime.now(timezone.utc)
                    return session
                else:
                    # Remove expired session
                    logger.debug(f"Found expired session for user: {username}, removing it")
                    await self.delete_session(session.id)

        # Create new session
        session_id = str(uuid4())
        logger.debug(f"Creating new session with ID: {session_id}")
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
        logger.debug(f"Created new session for user: {username}, total sessions: {len(self.sessions)}")
        return session

    async def get_session(self, session_id: str, request: Request) -> ApiResponse:
        """Get a session by its ID."""
        logger.debug(f"Getting session: {session_id}")
        session = self.sessions.get(session_id)

        if not session:
            logger.debug(f"Session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")

        # Check if session has expired
        if not await self.validate_session(session_id):
            logger.debug(f"Session expired: {session_id}")
            raise HTTPException(status_code=401, detail="Session expired")

        formatter = UnityResponseFormatter(request)
        return await formatter.format_collection(
            [session], entry_links={0: [{"rel": "self", "href": f"/{session_id}"}]}
        )

    async def get_all_sessions(self, request: Request) -> ApiResponse:
        """Get all active sessions."""
        logger.debug(f"Getting all sessions, count: {len(self.sessions)}")
        # Clean up expired sessions first
        await self._cleanup_expired_sessions()

        formatter = UnityResponseFormatter(request)
        sessions = list(self.sessions.values())
        entry_links = {i: [{"rel": "self", "href": f"/{session.id}"}] for i, session in enumerate(sessions)}

        return await formatter.format_collection(sessions, entry_links=entry_links)

    async def validate_session(self, session_id: str) -> bool:
        """Validate if a session is still active."""
        logger.debug(f"Validating session: {session_id}, total sessions: {len(self.sessions)}")
        session = self.sessions.get(session_id)
        if not session:
            logger.debug(f"Session not found: {session_id}")
            return False

        # Check if session has timed out
        now = datetime.now(timezone.utc)
        idle_time = now - session.last_activity
        if idle_time > timedelta(seconds=session.idleTimeout):
            logger.debug(f"Session expired, idle time: {idle_time.total_seconds()}s")
            await self.delete_session(session_id)
            return False

        # Update last activity time
        session.last_activity = now
        logger.debug(f"Session validated successfully: {session_id}")
        return True

    async def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions."""
        logger.debug("Cleaning up expired sessions")
        now = datetime.now(timezone.utc)
        expired = [
            session_id
            for session_id, session in self.sessions.items()
            if now - session.last_activity > timedelta(seconds=session.idleTimeout)
        ]
        for session_id in expired:
            logger.debug(f"Removing expired session: {session_id}")
            await self.delete_session(session_id)

    async def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        logger.debug(f"Deleting session: {session_id}")
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.debug(f"Session deleted, remaining sessions: {len(self.sessions)}")

    async def logout(self, username: str, localCleanupOnly: bool = True) -> LogoutResponse:
        """Logout user sessions."""
        logger.debug(f"Logging out user: {username}")
        # Find all sessions for this user
        user_sessions = [session_id for session_id, session in self.sessions.items() if session.user.name == username]

        # Delete sessions
        for session_id in user_sessions:
            await self.delete_session(session_id)

        return LogoutResponse(logoutOK="true")
