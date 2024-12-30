import pytest
from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPBasicCredentials
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.core.auth import get_current_user, verify_csrf_token, verify_password
from dell_unisphere_mock_api.main import app

client = TestClient(app)


def test_verify_password():
    assert verify_password("Password123!", "Password123!") is True
    assert not verify_password("wrong", "Password123!")


@pytest.mark.asyncio
async def test_get_current_user_success():
    credentials = HTTPBasicCredentials(username="admin", password="Password123!")
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"x-emc-rest-client", b"true"), (b"authorization", b"Basic YWRtaW46UGFzc3dvcmQxMjMh")],
            "path": "/api/types/pool/instances",
        }
    )
    response = Response()

    user = await get_current_user(request, response, credentials)
    assert user["username"] == "admin"
    assert user["role"] == "admin"
    assert "csrf_token" in user


@pytest.mark.asyncio
async def test_get_current_user_invalid_credentials():
    credentials = HTTPBasicCredentials(username="admin", password="wrong")
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"x-emc-rest-client", b"true"), (b"authorization", b"Basic YWRtaW46d3Jvbmc=")],
            "path": "/api/types/pool/instances",
        }
    )
    response = Response()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request, response, credentials)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid credentials"


@pytest.mark.asyncio
async def test_get_current_user_missing_header():
    credentials = HTTPBasicCredentials(username="admin", password="Password123!")
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"authorization", b"Basic YWRtaW46UGFzc3dvcmQxMjMh")],
            "path": "/api/types/pool/instances",
        }
    )
    response = Response()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request, response, credentials)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "X-EMC-REST-CLIENT header is required"


def test_verify_csrf_token_post_request():
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"emc-csrf-token", b"valid_token"), (b"authorization", b"Basic YWRtaW46UGFzc3dvcmQxMjMh")],
            "method": "POST",
            "path": "/api/types/pool/instances",
        }
    )
    verify_csrf_token(request, "POST")  # Should not raise exception


def test_verify_csrf_token_missing_token():
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"authorization", b"Basic YWRtaW46UGFzc3dvcmQxMjMh")],
            "method": "POST",
            "path": "/api/types/pool/instances",
        }
    )
    with pytest.raises(HTTPException) as exc_info:
        verify_csrf_token(request, "POST")
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "EMC-CSRF-TOKEN header is required" in exc_info.value.detail


def test_verify_csrf_token_get_request():
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"authorization", b"Basic YWRtaW46UGFzc3dvcmQxMjMh")],
            "method": "GET",
            "path": "/api/types/pool/instances",
        }
    )
    verify_csrf_token(request, "GET")  # Should not raise exception for GET
