import pytest

from dell_unisphere_mock_api.schemas.disk import DiskTierEnum, DiskTypeEnum


@pytest.fixture(autouse=True)
def client(test_client):
    return test_client


def get_auth_headers():
    """Helper function to get authentication headers."""
    return {"Authorization": "Basic YWRtaW46c2VjcmV0"}  # admin:secret


def test_create_disk(client, auth_headers):
    """Test creating a new disk."""
    headers, _ = auth_headers  # Unpack the tuple
    disk_data = {
        "name": "test_disk",
        "description": "Test disk",
        "disk_type": DiskTypeEnum.SAS,
        "tier_type": DiskTierEnum.PERFORMANCE,
        "size": 1000000,
        "slot_number": 1,
        "firmware_version": "1.0.0",
    }

    response = client.post("/api/types/disk/instances", json=disk_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["entries"][0]["content"]["name"] == disk_data["name"]
    assert data["entries"][0]["content"]["disk_type"] == disk_data["disk_type"]
    assert data["entries"][0]["content"]["tier_type"] == disk_data["tier_type"]
    assert "id" in data["entries"][0]["content"]


def test_create_disk_invalid_type(client, auth_headers):
    """Test creating a disk with invalid disk type."""
    headers, _ = auth_headers  # Unpack the tuple
    disk_data = {
        "name": "test_disk",
        "disk_type": "INVALID_TYPE",
        "tier_type": DiskTierEnum.PERFORMANCE,
        "size": 1000000,
        "slot_number": 1,
    }

    response = client.post("/api/types/disk/instances", json=disk_data, headers=headers)
    assert response.status_code == 422  # Validation error


def test_get_disk(client, auth_headers):
    """Test getting a specific disk."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a disk
    disk_data = {
        "name": "test_disk",
        "disk_type": DiskTypeEnum.SAS,
        "tier_type": DiskTierEnum.PERFORMANCE,
        "size": 1000000,
        "slot_number": 1,
    }
    create_response = client.post("/api/types/disk/instances", json=disk_data, headers=headers)
    disk_id = create_response.json()["entries"][0]["content"]["id"]

    # Then get it
    response = client.get(f"/api/types/disk/instances/{disk_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["entries"][0]["content"]["id"] == disk_id
    assert data["entries"][0]["content"]["name"] == disk_data["name"]


def test_list_disks(client, auth_headers):
    """Test listing all disks."""
    headers, _ = auth_headers  # Unpack the tuple
    response = client.get("/api/types/disk/instances", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "entries" in data
    assert isinstance(data["entries"], list)


def test_update_disk(client, auth_headers):
    """Test updating a disk."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a disk
    disk_data = {
        "name": "test_disk",
        "disk_type": DiskTypeEnum.SAS,
        "tier_type": DiskTierEnum.PERFORMANCE,
        "size": 1000000,
        "slot_number": 1,
    }
    create_response = client.post("/api/types/disk/instances", json=disk_data, headers=headers)
    disk_id = create_response.json()["entries"][0]["content"]["id"]

    # Then update it
    update_data = {
        "name": "updated_disk",
        "description": "Updated description",
        "firmware_version": "2.0.0",
    }
    response = client.patch(f"/api/types/disk/instances/{disk_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["entries"][0]["content"]["name"] == update_data["name"]
    assert data["entries"][0]["content"]["description"] == update_data["description"]
    assert data["entries"][0]["content"]["firmware_version"] == update_data["firmware_version"]


def test_delete_disk(client, auth_headers):
    """Test deleting a disk."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a disk
    disk_data = {
        "name": "test_disk",
        "disk_type": DiskTypeEnum.SAS,
        "tier_type": DiskTierEnum.PERFORMANCE,
        "size": 1000000,
        "slot_number": 1,
    }
    create_response = client.post("/api/types/disk/instances", json=disk_data, headers=headers)
    disk_id = create_response.json()["entries"][0]["content"]["id"]

    # Then delete it
    response = client.delete(f"/api/types/disk/instances/{disk_id}", headers=headers)
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/types/disk/instances/{disk_id}", headers=headers)
    assert get_response.status_code == 404


def test_get_disks_by_pool(client, auth_headers):
    """Test getting disks by pool ID."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a disk with a pool ID
    disk_data = {
        "name": "test_disk",
        "disk_type": DiskTypeEnum.SAS,
        "tier_type": DiskTierEnum.PERFORMANCE,
        "size": 1000000,
        "slot_number": 1,
        "pool_id": "test_pool",
    }
    client.post("/api/types/disk/instances", json=disk_data, headers=headers)

    # Get disks by pool
    response = client.get("/api/types/disk/instances/byPool/test_pool", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["entries"]) > 0
    assert all(disk["content"]["pool_id"] == "test_pool" for disk in data["entries"])


def test_get_disks_by_disk_group(client, auth_headers):
    """Test getting disks by disk group ID."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a disk with a disk group ID
    disk_data = {
        "name": "test_disk",
        "disk_type": DiskTypeEnum.SAS,
        "tier_type": DiskTierEnum.PERFORMANCE,
        "size": 1000000,
        "slot_number": 1,
        "disk_group_id": "test_group",
    }
    client.post("/api/types/disk/instances", json=disk_data, headers=headers)

    # Get disks by disk group
    response = client.get("/api/types/disk/instances/byDiskGroup/test_group", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["entries"]) > 0
    assert all(disk["content"]["disk_group_id"] == "test_group" for disk in data["entries"])
