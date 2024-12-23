import pytest
from fastapi import HTTPException, Request, Response
from dell_unisphere_mock_api.core.auth import (
    get_current_user,
    verify_password,
    verify_csrf_token
)
from fastapi.security import HTTPBasicCredentials

class MockRequest:
    def __init__(self, headers=None, method="GET"):
        self.headers = headers or {}
        self.method = method

class MockResponse:
    def __init__(self):
        self.headers = {}
        self.cookies = {}

    def set_cookie(self, key, value, httponly=False, secure=False):
        self.cookies[key] = {
            "value": value,
            "httponly": httponly,
            "secure": secure
        }

@pytest.fixture
def test_user_data():
    return {
        "username": "admin",
        "role": "admin"
    }

@pytest.fixture
def mock_request():
    return MockRequest(
        headers={
            "X-EMC-REST-CLIENT": "true"
        }
    )

@pytest.fixture
def mock_response():
    return MockResponse()

def test_password_verification():
    assert verify_password("Password123!", "Password123!")
    assert not verify_password("wrongpassword", "Password123!")

@pytest.mark.asyncio
async def test_get_current_user_valid_credentials(test_user_data, mock_request, mock_response):
    credentials = HTTPBasicCredentials(username=test_user_data["username"], password="Password123!")
    user = await get_current_user(mock_request, mock_response, credentials)
    assert user["username"] == test_user_data["username"]
    assert user["role"] == test_user_data["role"]
    assert "csrf_token" in user
    assert "mod_sec_emc" in mock_response.cookies
    assert "EMC-CSRF-TOKEN" in mock_response.headers

@pytest.mark.asyncio
async def test_get_current_user_invalid_credentials(mock_request, mock_response):
    credentials = HTTPBasicCredentials(username="wrong", password="wrong")
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request, mock_response, credentials)
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_missing_emc_header(test_user_data, mock_response):
    request = MockRequest(headers={})  # Missing X-EMC-REST-CLIENT header
    credentials = HTTPBasicCredentials(username=test_user_data["username"], password="Password123!")
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request, mock_response, credentials)
    assert exc_info.value.status_code == 401

def test_verify_csrf_token_post_request():
    # Test POST request without CSRF token
    request = MockRequest(headers={}, method="POST")
    with pytest.raises(HTTPException) as exc_info:
        verify_csrf_token(request, "POST")
    assert exc_info.value.status_code == 403

    # Test POST request with CSRF token
    request = MockRequest(headers={"EMC-CSRF-TOKEN": "valid-token"}, method="POST")
    verify_csrf_token(request, "POST")  # Should not raise exception

def test_verify_csrf_token_get_request():
    # GET requests don't require CSRF token
    request = MockRequest(headers={}, method="GET")
    verify_csrf_token(request, "GET")  # Should not raise exception
