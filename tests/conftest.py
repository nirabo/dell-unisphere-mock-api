import pytest
from fastapi.testclient import TestClient
from dell_unisphere_mock_api.main import app
from dell_unisphere_mock_api.core.auth import create_access_token, get_current_user
from dell_unisphere_mock_api.models.pool import PoolModel
from dell_unisphere_mock_api.models.lun import LUNModel
from datetime import timedelta, UTC
from fastapi import Request
from typing import Optional

# Override the get_current_user function for testing
async def mock_get_current_user(request: Request) -> Optional[dict]:
    return {
        "username": "test_user",
        "role": "admin"
    }

@pytest.fixture(autouse=True)
def clear_data():
    """Clear all data before each test."""
    pool_model = PoolModel()
    lun_model = LUNModel()
    pool_model.pools.clear()
    lun_model.luns.clear()
    yield

@pytest.fixture
def test_client():
    # Override the dependency in our app
    app.dependency_overrides[get_current_user] = mock_get_current_user
    client = TestClient(app)
    yield client
    # Clean up after test
    app.dependency_overrides.clear()

@pytest.fixture
def test_user():
    return {
        "username": "test_user",
        "role": "admin"
    }

@pytest.fixture
def auth_headers(test_user):
    access_token = create_access_token(
        data={"sub": test_user["username"], "role": test_user["role"]},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}
