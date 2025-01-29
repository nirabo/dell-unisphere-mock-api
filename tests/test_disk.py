import pytest

from dell_unisphere_mock_api.schemas.disk import DiskTierEnum, DiskTypeEnum


@pytest.fixture(autouse=True)
def client(test_client):
    return test_client


def get_auth_headers():
    """Helper function to get authentication headers."""
    return {"Authorization": "Basic YWRtaW46c2VjcmV0"}  # admin:secret


def verify_response_format(response_data):
    """Helper function to verify the response format from middleware."""
    if response_data.get("errorCode") is not None:
        # This is an error response
        assert "errorCode" in response_data
        assert "messages" in response_data
        return

    # Regular response
    assert "@base" in response_data, "Response missing @base field from middleware"
    assert "entries" in response_data, "Response missing entries field"
    if response_data["entries"]:
        assert "content" in response_data["entries"][0], "Response entry missing content field"
        assert "id" in response_data["entries"][0]["content"], "Response content missing id field"


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
    verify_response_format(data)
    content = data["entries"][0]["content"]
    assert content["name"] == disk_data["name"]
    assert content["disk_type"] == disk_data["disk_type"]
    assert content["tier_type"] == disk_data["tier_type"]


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
    assert response.status_code == 422
    data = response.json()
    verify_response_format(data)


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
    assert create_response.status_code == 201
    created_data = create_response.json()
    verify_response_format(created_data)
    disk_id = created_data["entries"][0]["content"]["id"]

    # Get the disk
    response = client.get(f"/api/types/disk/instances/{disk_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    verify_response_format(data)
    content = data["entries"][0]["content"]
    assert content["id"] == disk_id
    assert content["name"] == disk_data["name"]


def test_list_disks(client, auth_headers):
    """Test listing all disks."""
    headers, _ = auth_headers  # Unpack the tuple
    response = client.get("/api/types/disk/instances", headers=headers)
    assert response.status_code == 200
    data = response.json()
    verify_response_format(data)


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
    assert create_response.status_code == 201
    created_data = create_response.json()
    verify_response_format(created_data)
    disk_id = created_data["entries"][0]["content"]["id"]

    # Update the disk
    update_data = {
        "name": "updated_disk",
        "description": "Updated disk description",
    }
    response = client.patch(f"/api/types/disk/instances/{disk_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    verify_response_format(data)
    content = data["entries"][0]["content"]
    assert content["name"] == update_data["name"]
    assert content["description"] == update_data["description"]


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
    assert create_response.status_code == 201
    created_data = create_response.json()
    verify_response_format(created_data)
    disk_id = created_data["entries"][0]["content"]["id"]

    # Delete the disk
    response = client.delete(f"/api/types/disk/instances/{disk_id}", headers=headers)
    assert response.status_code == 204

    # Verify disk is deleted
    get_response = client.get(f"/api/types/disk/instances/{disk_id}", headers=headers)
    assert get_response.status_code == 404
    error_data = get_response.json()
    verify_response_format(error_data)


def test_get_disks_by_pool(client, auth_headers):
    """Test getting disks by pool ID."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a disk with a pool_id
    disk_data = {
        "name": "test_disk",
        "disk_type": DiskTypeEnum.SAS,
        "tier_type": DiskTierEnum.PERFORMANCE,
        "size": 1000000,
        "slot_number": 1,
        "pool_id": "pool_1",
    }
    create_response = client.post("/api/types/disk/instances", json=disk_data, headers=headers)
    assert create_response.status_code == 201
    created_data = create_response.json()
    verify_response_format(created_data)
    pool_id = disk_data["pool_id"]

    # Get disks by pool
    response = client.get(f"/api/types/disk/instances/byPool/{pool_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    verify_response_format(data)
    content = data["entries"][0]["content"]
    assert content["pool_id"] == pool_id


def test_get_disks_by_disk_group(client, auth_headers):
    """Test getting disks by disk group ID."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a disk with a disk_group_id
    disk_data = {
        "name": "test_disk",
        "disk_type": DiskTypeEnum.SAS,
        "tier_type": DiskTierEnum.PERFORMANCE,
        "size": 1000000,
        "slot_number": 1,
        "disk_group_id": "group_1",
    }
    create_response = client.post("/api/types/disk/instances", json=disk_data, headers=headers)
    assert create_response.status_code == 201
    created_data = create_response.json()
    verify_response_format(created_data)
    disk_group_id = disk_data["disk_group_id"]

    # Get disks by disk group
    response = client.get(f"/api/types/disk/instances/byDiskGroup/{disk_group_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    verify_response_format(data)
    content = data["entries"][0]["content"]
    assert content["disk_group_id"] == disk_group_id
