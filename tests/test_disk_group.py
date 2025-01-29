import pytest
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.main import app
from dell_unisphere_mock_api.schemas.disk_group import RaidStripeWidthEnum, RaidTypeEnum

client = TestClient(app)


@pytest.fixture
def disk_group_data():
    """Sample disk group data for tests."""
    return {
        "name": "test_disk_group",
        "description": "Test disk group",
        "raid_type": RaidTypeEnum.RAID5,
        "stripe_width": RaidStripeWidthEnum.FIVE,
        "disk_ids": ["1", "2", "3", "4", "5"],
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000,
    }


def test_create_disk_group(test_client, auth_headers, disk_group_data):
    """Test creating a new disk group."""
    headers, _ = auth_headers  # Unpack the tuple
    response = test_client.post("/api/types/diskGroup/instances", json=disk_group_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "entries" in data
    assert len(data["entries"]) == 1
    content = data["entries"][0]["content"]
    assert content["name"] == disk_group_data["name"]
    assert "id" in content


def test_create_disk_group_invalid_raid(test_client, auth_headers):
    """Test creating a disk group with invalid RAID configuration."""
    headers, _ = auth_headers  # Unpack the tuple
    invalid_disk_group_data = {
        "name": "test_disk_group",
        "raid_type": RaidTypeEnum.RAID5,
        "stripe_width": RaidStripeWidthEnum.FIVE,
        "disk_ids": ["1", "2", "3"],  # Not enough disks for RAID5
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000,
    }

    response = test_client.post(
        "/api/types/diskGroup/instances",
        json=invalid_disk_group_data,
        headers=headers,
    )
    assert response.status_code == 400


def test_get_disk_group(test_client, auth_headers, disk_group_data):
    """Test getting a specific disk group."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a disk group
    create_response = test_client.post("/api/types/diskGroup/instances", json=disk_group_data, headers=headers)
    assert create_response.status_code == 201
    disk_group_id = create_response.json()["entries"][0]["content"]["id"]

    # Then get it
    response = test_client.get(f"/api/types/diskGroup/instances/{disk_group_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    content = data["entries"][0]["content"]
    assert content["id"] == disk_group_id
    assert content["name"] == disk_group_data["name"]


def test_list_disk_groups(test_client, auth_headers):
    """Test listing all disk groups."""
    headers, _ = auth_headers  # Unpack the tuple
    response = test_client.get("/api/types/diskGroup/instances", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "entries" in data
    assert isinstance(data["entries"], list)


def test_update_disk_group(test_client, auth_headers, disk_group_data):
    """Test updating a disk group."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a disk group
    create_response = test_client.post("/api/types/diskGroup/instances", json=disk_group_data, headers=headers)
    assert create_response.status_code == 201
    disk_group_id = create_response.json()["entries"][0]["content"]["id"]

    # Update the disk group
    update_data = {"description": "Updated disk group description"}
    response = test_client.patch(
        f"/api/types/diskGroup/instances/{disk_group_id}",
        json=update_data,
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    content = data["entries"][0]["content"]
    assert content["description"] == update_data["description"]


def test_delete_disk_group(test_client, auth_headers, disk_group_data):
    """Test deleting a disk group."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a disk group
    create_response = test_client.post("/api/types/diskGroup/instances", json=disk_group_data, headers=headers)
    assert create_response.status_code == 201
    disk_group_id = create_response.json()["entries"][0]["content"]["id"]

    # Then delete it
    response = test_client.delete(f"/api/types/diskGroup/instances/{disk_group_id}", headers=headers)
    assert response.status_code == 204

    # Verify it's gone
    get_response = test_client.get(f"/api/types/diskGroup/instances/{disk_group_id}", headers=headers)
    assert get_response.status_code == 404
