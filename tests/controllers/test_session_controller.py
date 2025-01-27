from datetime import datetime, timezone
from typing import Any, Dict

import pytest
from fastapi import HTTPException, Request

from dell_unisphere_mock_api.controllers.session_controller import SessionController
from dell_unisphere_mock_api.models.login_session_info import LoginSessionInfo


@pytest.fixture
def mock_request():
    class MockRequest:
        def __init__(self):
            self.base_url = "http://testserver"
            self.path = "/api/types/loginSessionInfo/instances"
            self.url = type("URL", (), {"path": "/api/types/loginSessionInfo/instances"})()

    return MockRequest()


@pytest.fixture
def session_controller():
    return SessionController()


@pytest.mark.asyncio
async def test_create_session(session_controller):
    """Test creating a new session."""
    session = await session_controller.create_session("testuser", "password")
    assert isinstance(session, LoginSessionInfo)
    assert session.user.name == "testuser"
    assert session.user.role == "admin"
    assert session.idleTimeout == 3600
    assert isinstance(session.last_activity, datetime)


@pytest.mark.asyncio
async def test_create_session_existing_user(session_controller):
    """Test creating a session for an existing user."""
    session1 = await session_controller.create_session("testuser", "password")
    session2 = await session_controller.create_session("testuser", "password")
    assert session1.id == session2.id


def test_get_session(session_controller, mock_request):
    """Test getting a specific session."""
    session_id = "test_session"
    session = LoginSessionInfo(
        id=session_id,
        domain="Local",
        user={
            "id": "user_testuser",
            "name": "testuser",
            "role": "admin",
            "password_change_required": False,
            "domain": "Local",
        },
        roles=[{"id": "admin", "name": "Administrator", "description": "Full system access"}],
        idleTimeout=3600,
        isPasswordChangeRequired=False,
        last_activity=datetime.now(timezone.utc),
    )
    session_controller.sessions[session_id] = session

    response = session_controller.get_session(session_id, mock_request)
    assert response.base == "http://testserver/api/types/loginSessionInfo/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content == session
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{session_id}"


def test_get_session_not_found(session_controller, mock_request):
    """Test getting a non-existent session."""
    with pytest.raises(HTTPException) as exc:
        session_controller.get_session("nonexistent", mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Session not found"


def test_get_all_sessions(session_controller, mock_request):
    """Test getting all active sessions."""
    # Create some test sessions
    sessions = {
        "session1": LoginSessionInfo(
            id="session1",
            domain="Local",
            user={
                "id": "user_testuser1",
                "name": "testuser1",
                "role": "admin",
                "password_change_required": False,
                "domain": "Local",
            },
            roles=[{"id": "admin", "name": "Administrator", "description": "Full system access"}],
            idleTimeout=3600,
            isPasswordChangeRequired=False,
            last_activity=datetime.now(timezone.utc),
        ),
        "session2": LoginSessionInfo(
            id="session2",
            domain="Local",
            user={
                "id": "user_testuser2",
                "name": "testuser2",
                "role": "admin",
                "password_change_required": False,
                "domain": "Local",
            },
            roles=[{"id": "admin", "name": "Administrator", "description": "Full system access"}],
            idleTimeout=3600,
            isPasswordChangeRequired=False,
            last_activity=datetime.now(timezone.utc),
        ),
    }
    session_controller.sessions = sessions

    response = session_controller.get_all_sessions(mock_request)
    assert response.base == "http://testserver/api/types/loginSessionInfo/instances"
    assert len(response.entries) == 2
    assert {entry.content.id for entry in response.entries} == {"session1", "session2"}
    for entry in response.entries:
        assert entry.links[0].rel == "self"
        assert entry.links[0].href == f"/{entry.content.id}"


def test_logout(session_controller):
    """Test logging out from a session."""
    # Create a test session
    session_id = "test_session"
    session = LoginSessionInfo(
        id=session_id,
        domain="Local",
        user={
            "id": "user_testuser",
            "name": "testuser",
            "role": "admin",
            "password_change_required": False,
            "domain": "Local",
        },
        roles=[{"id": "admin", "name": "Administrator", "description": "Full system access"}],
        idleTimeout=3600,
        isPasswordChangeRequired=False,
        last_activity=datetime.now(timezone.utc),
    )
    session_controller.sessions[session_id] = session

    # Test local cleanup
    response = session_controller.logout("testuser", localCleanupOnly=True)
    assert session_id not in session_controller.sessions

    # Test global cleanup
    session_controller.sessions[session_id] = session
    response = session_controller.logout("testuser", localCleanupOnly=False)
    assert session_id not in session_controller.sessions
