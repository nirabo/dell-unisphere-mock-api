import pytest
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.main import app

client = TestClient(app)


def test_get_basic_system_info_collection():
    """Test collection query for basicSystemInfo"""
    response = client.get("/api/types/basicSystemInfo/instances")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, dict) for item in data)
    assert all(
        key in item
        for item in data
        for key in ["id", "model", "name", "softwareVersion", "apiVersion", "earliestApiVersion"]
    )


def test_get_basic_system_info_instance_by_id():
    """Test instance query by ID"""
    # First get a valid ID from the collection
    collection_response = client.get("/api/types/basicSystemInfo/instances")
    assert collection_response.status_code == 200
    test_id = collection_response.json()[0]["id"]

    # Test instance query
    response = client.get(f"/api/instances/basicSystemInfo/{test_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["id"] == test_id
    assert all(key in data for key in ["model", "name", "softwareVersion", "apiVersion", "earliestApiVersion"])


def test_basic_system_info_unauthenticated_access():
    """Verify basicSystemInfo endpoints are accessible without authentication"""
    endpoints = [
        "/api/types/basicSystemInfo/instances",
        "/api/instances/basicSystemInfo/system-1",
        "/api/instances/basicSystemInfo/name/MyStorageSystem",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
