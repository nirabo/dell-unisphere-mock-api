"""Integration tests for session management functionality."""

import base64
from datetime import datetime, timedelta, timezone
from typing import Dict, Generator

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient
from freezegun import freeze_time

from dell_unisphere_mock_api.controllers.session_controller import SessionController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.middleware.response_headers import ResponseHeaderMiddleware


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI application."""
    app = FastAPI()
    app.add_middleware(ResponseHeaderMiddleware)

    @app.get("/api/test")
    async def test_endpoint(user: Dict[str, str] = Depends(get_current_user)):
        return {"status": "ok"}

    @app.post("/api/test")
    async def test_post_endpoint(request: Request, user: Dict[str, str] = Depends(get_current_user)):
        return {"status": "ok"}

    return app


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Create a test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear all sessions before each test."""
    session_controller = SessionController()
    session_controller.sessions.clear()


def get_basic_auth_header(username: str = "admin", password: str = "Password123!") -> Dict[str, str]:
    """Create Basic Auth header."""
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}


def test_basic_auth_creates_session(client: TestClient):
    """Test that Basic Auth creates a new session."""
    # Make request with Basic Auth
    response = client.get("/api/test", headers={**get_basic_auth_header(), "X-EMC-REST-CLIENT": "true"})
    assert response.status_code == 200

    # Verify session cookie is set
    assert "mod_sec_emc" in response.cookies
    cookie = response.cookies["mod_sec_emc"]
    assert "value3&1&value1&" in cookie

    # Verify session is stored in controller
    session_id = cookie.split("&")[3]
    session_controller = SessionController()
    assert session_id in session_controller.sessions


def test_session_cookie_auth(client: TestClient):
    """Test that session cookie can be used for authentication."""
    # First create session with Basic Auth
    response = client.get("/api/test", headers={**get_basic_auth_header(), "X-EMC-REST-CLIENT": "true"})
    assert response.status_code == 200
    cookie = response.cookies["mod_sec_emc"]

    # Use session cookie for next request
    client.cookies.set("mod_sec_emc", cookie)
    response = client.get("/api/test", headers={"X-EMC-REST-CLIENT": "true"})
    assert response.status_code == 200


def test_session_expiry(client: TestClient):
    """Test that sessions expire after idle timeout."""
    current_time = datetime.now(timezone.utc)

    with freeze_time(current_time):
        # Create session
        response = client.get("/api/test", headers={**get_basic_auth_header(), "X-EMC-REST-CLIENT": "true"})
        assert response.status_code == 200
        cookie = response.cookies["mod_sec_emc"]

        # Move time forward past idle timeout
        session_controller = SessionController()
        future_time = current_time + timedelta(seconds=session_controller.idle_timeout + 1)

    with freeze_time(future_time):
        # Try to use expired session
        client.cookies.set("mod_sec_emc", cookie)
        response = client.get("/api/test", headers={"X-EMC-REST-CLIENT": "true"})
        assert response.status_code == 401


def test_session_refresh(client: TestClient):
    """Test that session timeout is refreshed on activity."""
    current_time = datetime.now(timezone.utc)

    with freeze_time(current_time):
        # Create session
        response = client.get("/api/test", headers={**get_basic_auth_header(), "X-EMC-REST-CLIENT": "true"})
        assert response.status_code == 200
        cookie = response.cookies["mod_sec_emc"]

        # Move time forward but not past timeout
        session_controller = SessionController()
        future_time = current_time + timedelta(seconds=session_controller.idle_timeout - 10)

        with freeze_time(future_time):
            # Use session before timeout
            client.cookies.set("mod_sec_emc", cookie)
            response = client.get("/api/test", headers={"X-EMC-REST-CLIENT": "true"})
            assert response.status_code == 200

            # Move time forward again but not past new timeout
            future_time2 = future_time + timedelta(seconds=session_controller.idle_timeout - 10)
            with freeze_time(future_time2):
                # Session should still be valid due to refresh
                response = client.get("/api/test", headers={"X-EMC-REST-CLIENT": "true"})
                assert response.status_code == 200


def test_csrf_token_required_for_post(client: TestClient):
    """Test that CSRF token is required for POST requests."""
    # Create session
    response = client.get("/api/test", headers={**get_basic_auth_header(), "X-EMC-REST-CLIENT": "true"})
    assert response.status_code == 200
    cookie = response.cookies["mod_sec_emc"]
    csrf_token = response.headers["EMC-CSRF-TOKEN"]

    # POST without CSRF token should fail
    client.cookies.set("mod_sec_emc", cookie)
    response = client.post("/api/test", headers={"X-EMC-REST-CLIENT": "true"})
    assert response.status_code == 401

    # POST with CSRF token should succeed
    response = client.post("/api/test", headers={"X-EMC-REST-CLIENT": "true", "EMC-CSRF-TOKEN": csrf_token})
    assert response.status_code == 200


def test_invalid_session_falls_back_to_basic_auth(client: TestClient):
    """Test that invalid session falls back to Basic Auth."""
    # Set invalid session cookie on the client
    client.cookies.set("mod_sec_emc", "value3&1&value1&invalid_session&value2&token")

    # Try invalid session first
    response = client.get("/api/test", headers={**get_basic_auth_header(), "X-EMC-REST-CLIENT": "true"})
    # Should still succeed due to Basic Auth fallback
    assert response.status_code == 200
    # Should get new session cookie
    assert "mod_sec_emc" in response.cookies
