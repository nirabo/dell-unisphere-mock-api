import pytest
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.main import app

client = TestClient(app)


def test_get_basic_system_info_collection():
    """Test collection query for basicSystemInfo"""
    response = client.get("/api/types/basicSystemInfo/instances")
    assert response.status_code == 200
    data = response.json()
    assert "@base" in data
    assert "updated" in data
    assert "links" in data
    assert "entries" in data
    assert len(data["entries"]) > 0

    # Check first entry
    entry = data["entries"][0]
    assert "@base" in entry
    assert "content" in entry
    content = entry["content"]
    assert all(key in content for key in ["id", "model", "name", "softwareVersion", "apiVersion", "earliestApiVersion"])


def test_get_basic_system_info_instance_by_id():
    """Test instance query by ID"""
    # First get a valid ID from the collection
    collection_response = client.get("/api/types/basicSystemInfo/instances")
    assert collection_response.status_code == 200
    test_id = collection_response.json()["entries"][0]["content"]["id"]

    # Test instance query
    response = client.get(f"/api/instances/basicSystemInfo/{test_id}")
    assert response.status_code == 200
    data = response.json()
    assert "@base" in data
    assert "updated" in data
    assert "links" in data
    assert "entries" in data
    assert len(data["entries"]) == 1

    # Check content
    content = data["entries"][0]["content"]
    assert content["id"] == test_id
    assert all(key in content for key in ["model", "name", "softwareVersion", "apiVersion", "earliestApiVersion"])


def test_basic_system_info_unauthenticated_access():
    """Verify basicSystemInfo endpoints are accessible without authentication"""
    endpoints = [
        "/api/types/basicSystemInfo/instances",
        "/api/instances/basicSystemInfo/0",
        # "/api/instances/basicSystemInfo/name/MyStorageSystem",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = response.json()
        assert "@base" in data
        assert "updated" in data
        assert "links" in data
        assert "entries" in data
