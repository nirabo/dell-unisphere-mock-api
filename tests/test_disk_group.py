from fastapi.testclient import TestClient
import pytest
from dell_unisphere_mock_api.main import app
from dell_unisphere_mock_api.schemas.disk_group import RaidTypeEnum, RaidStripeWidthEnum

client = TestClient(app)

def get_auth_headers():
    """Helper function to get authentication headers."""
    return {"Authorization": "Basic YWRtaW46c2VjcmV0"}  # admin:secret

def test_create_disk_group():
    """Test creating a new disk group."""
    disk_group_data = {
        "name": "test_disk_group",
        "description": "Test disk group",
        "raid_type": RaidTypeEnum.RAID5,
        "stripe_width": RaidStripeWidthEnum.FIVE,
        "disk_ids": ["1", "2", "3", "4", "5"],
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000
    }
    
    response = client.post(
        "/api/types/diskGroup/instances",
        json=disk_group_data,
        headers=get_auth_headers()
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == disk_group_data["name"]
    assert "id" in data

def test_create_disk_group_invalid_raid():
    """Test creating a disk group with invalid RAID configuration."""
    disk_group_data = {
        "name": "test_disk_group",
        "raid_type": RaidTypeEnum.RAID5,
        "stripe_width": RaidStripeWidthEnum.FIVE,
        "disk_ids": ["1", "2", "3"],  # Not enough disks for RAID5
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000
    }
    
    response = client.post(
        "/api/types/diskGroup/instances",
        json=disk_group_data,
        headers=get_auth_headers()
    )
    assert response.status_code == 400

def test_get_disk_group():
    """Test getting a specific disk group."""
    # First create a disk group
    disk_group_data = {
        "name": "test_disk_group",
        "raid_type": RaidTypeEnum.RAID5,
        "stripe_width": RaidStripeWidthEnum.FIVE,
        "disk_ids": ["1", "2", "3", "4", "5"],
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000
    }
    create_response = client.post(
        "/api/types/diskGroup/instances",
        json=disk_group_data,
        headers=get_auth_headers()
    )
    disk_group_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(
        f"/api/types/diskGroup/instances/{disk_group_id}",
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == disk_group_id
    assert data["name"] == disk_group_data["name"]

def test_list_disk_groups():
    """Test listing all disk groups."""
    response = client.get(
        "/api/types/diskGroup/instances",
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_disk_group():
    """Test updating a disk group."""
    # First create a disk group
    disk_group_data = {
        "name": "test_disk_group",
        "raid_type": RaidTypeEnum.RAID5,
        "stripe_width": RaidStripeWidthEnum.FIVE,
        "disk_ids": ["1", "2", "3", "4", "5"],
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000
    }
    create_response = client.post(
        "/api/types/diskGroup/instances",
        json=disk_group_data,
        headers=get_auth_headers()
    )
    disk_group_id = create_response.json()["id"]
    
    # Then update it
    update_data = {
        "name": "updated_disk_group",
        "description": "Updated description"
    }
    response = client.patch(
        f"/api/types/diskGroup/instances/{disk_group_id}",
        json=update_data,
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_delete_disk_group():
    """Test deleting a disk group."""
    # First create a disk group
    disk_group_data = {
        "name": "test_disk_group",
        "raid_type": RaidTypeEnum.RAID5,
        "stripe_width": RaidStripeWidthEnum.FIVE,
        "disk_ids": ["1", "2", "3", "4", "5"],
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000
    }
    create_response = client.post(
        "/api/types/diskGroup/instances",
        json=disk_group_data,
        headers=get_auth_headers()
    )
    disk_group_id = create_response.json()["id"]
    
    # Then delete it
    response = client.delete(
        f"/api/types/diskGroup/instances/{disk_group_id}",
        headers=get_auth_headers()
    )
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(
        f"/api/types/diskGroup/instances/{disk_group_id}",
        headers=get_auth_headers()
    )
    assert get_response.status_code == 404
