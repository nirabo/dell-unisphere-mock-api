import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from dell_unisphere_mock_api.core.auth import (
    create_access_token,
    get_current_user,
    verify_password,
    get_password_hash,
    Token,
    TokenData,
)
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock

@pytest.fixture
def mock_request():
    return Mock()

@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "role": "admin"
    }

@pytest.fixture
def test_token(test_user_data):
    return create_access_token(
        data={"sub": test_user_data["username"], "role": test_user_data["role"]},
        expires_delta=timedelta(minutes=30)
    )

def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_create_access_token(test_user_data):
    token = create_access_token(
        data={"sub": test_user_data["username"], "role": test_user_data["role"]},
        expires_delta=timedelta(minutes=30)
    )
    assert isinstance(token, str)

@pytest.mark.asyncio
async def test_get_current_user_valid_token(mock_request, test_token):
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=test_token)
    user = await get_current_user(mock_request, credentials)
    assert user["username"] == "testuser"
    assert user["role"] == "admin"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_request):
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request, credentials)
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_expired_token(mock_request, test_user_data):
    expired_token = create_access_token(
        data={"sub": test_user_data["username"], "role": test_user_data["role"]},
        expires_delta=timedelta(minutes=-30)  # Token is already expired
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request, credentials)
    assert exc_info.value.status_code == 401
