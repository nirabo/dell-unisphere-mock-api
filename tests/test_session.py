import base64

from fastapi.testclient import TestClient
from httpx import ASGITransport

from dell_unisphere_mock_api.main import app

client = TestClient(app)


def get_basic_auth_header(username: str, password: str) -> dict:
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "X-EMC-REST-CLIENT": "true",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def test_get_all_sessions_unauthorized():
    """Test getting all sessions without authentication"""
    response = client.get("/api/types/loginSessionInfo/instances")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_get_all_sessions_wrong_credentials():
    """Test getting all sessions with wrong credentials"""
    headers = get_basic_auth_header("wrong", "wrong")
    response = client.get("/api/types/loginSessionInfo/instances", headers=headers)
    assert response.status_code == 401


def test_get_all_sessions():
    """Test getting all sessions with correct credentials"""
    headers = get_basic_auth_header("admin", "Password123!")  # nosec B105 - This is just a mock password for testing
    response = client.get("/api/types/loginSessionInfo/instances", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "@base" in data
    assert "updated" in data
    assert "links" in data
    assert "entries" in data

    # Check entries structure if any exist
    if data["entries"]:
        entry = data["entries"][0]
        assert "@base" in entry
        assert "content" in entry
        assert "links" in entry
        assert "updated" in entry

        # Check content structure
        content = entry["content"]
        assert "id" in content
        assert "domain" in content
        assert "user" in content
        assert "roles" in content
        assert "idleTimeout" in content
        assert "isPasswordChangeRequired" in content


def test_get_specific_session():
    """Test getting a specific session"""
    # First create a session
    headers = get_basic_auth_header("admin", "Password123!")
    response = client.get("/api/types/loginSessionInfo/instances", headers=headers)
    assert response.status_code == 200
    data = response.json()

    if data["entries"]:
        session_id = data["entries"][0]["content"]["id"]

        # Now get the specific session
        response = client.get(f"/api/instances/loginSessionInfo/{session_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "@base" in data
        assert "entries" in data
        assert len(data["entries"]) == 1
        assert data["entries"][0]["content"]["id"] == session_id


def test_logout_session():
    """Test logging out of a session"""
    # First create a session
    headers = get_basic_auth_header("admin", "Password123!")  # nosec B105 - This is just a mock password for testing
    response = client.get("/api/types/loginSessionInfo/instances", headers=headers)
    assert response.status_code == 200

    # Now logout
    logout_data = {"localCleanupOnly": True}
    response = client.post("/api/types/loginSessionInfo/action/logout", headers=headers, json=logout_data)
    print("Logout response:", response.content)  # Print response content for debugging
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["logoutOK"] == "true"
