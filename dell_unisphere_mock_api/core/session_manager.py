import secrets
import time
from typing import Dict, Optional

from .session_models import LoginSessionInfo, Role, UserInfo


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}  # token -> session_data
        self.user_sessions: Dict[str, set] = {}  # user_id -> set of tokens

    def create_session(self, username: str, password: str) -> Optional[tuple[str, LoginSessionInfo]]:
        """Create a new session for user authentication"""
        # Mock authentication - in real implementation, verify against actual credentials
        if username == "admin" and password == "Password123!":  # nosec B105 - This is just a mock password for testing
            # Generate CSRF token
            token = secrets.token_urlsafe(48)

            # Create session info
            session = LoginSessionInfo(
                id=secrets.token_hex(16),
                domain="Local",
                user=UserInfo(id="user_admin", name=username),
                roles=[Role(id="administrator", name="Administrator")],
                idleTimeout=3600,
                isPasswordChangeRequired=False,
            )

            # Store session
            self.sessions[token] = {"info": session, "last_access": time.time()}

            # Track user's sessions
            if username not in self.user_sessions:
                self.user_sessions[username] = set()
            self.user_sessions[username].add(token)

            return token, session

        return None

    def get_session(self, token: str) -> Optional[LoginSessionInfo]:
        """Get session information and update last access time"""
        session_data = self.sessions.get(token)
        if session_data:
            # Update last access time
            session_data["last_access"] = time.time()
            return session_data["info"]
        return None

    def validate_session(self, token: str) -> bool:
        """Check if session is valid and not expired"""
        session_data = self.sessions.get(token)
        if not session_data:
            return False

        # Check if session has expired
        idle_time = time.time() - session_data["last_access"]
        if idle_time > session_data["info"].idleTimeout:
            self.logout(token)
            return False

        return True

    def logout(self, token: str, local_cleanup_only: bool = True) -> bool:
        """Logout session(s)"""
        session_data = self.sessions.get(token)
        if not session_data:
            return False

        username = session_data["info"].user.name

        if local_cleanup_only:
            # Remove only this session
            self.sessions.pop(token, None)
            self.user_sessions[username].remove(token)
        else:
            # Remove all sessions for this user
            user_tokens = self.user_sessions.get(username, set())
            for user_token in user_tokens:
                self.sessions.pop(user_token, None)
            self.user_sessions[username] = set()

        return True


# Global session manager instance
session_manager = SessionManager()
