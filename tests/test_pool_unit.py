import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from dell_unisphere_mock_api.controllers.pool_controller import PoolController
from dell_unisphere_mock_api.main import app
from dell_unisphere_mock_api.schemas.pool import HarvestStateEnum, PoolCreate, PoolUpdate, RaidTypeEnum
from dell_unisphere_mock_api.schemas.pool_unit import PoolUnitTypeEnum

client = TestClient(app)


def get_auth_headers():
    """Helper function to get authentication headers."""
    # admin:Password123! in base64
    return {
        "Authorization": "Basic YWRtaW46UGFzc3dvcmQxMjMh",
        "X-EMC-REST-CLIENT": "true",
        "EMC-CSRF-TOKEN": "test-csrf-token",
    }


def test_create_pool_unit():
    """Test creating a new pool unit."""
    pool_unit_data = {
        "name": "test_pool_unit",
        "description": "Test pool unit",
        "type": PoolUnitTypeEnum.VIRTUAL_DISK,
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000,
        "raid_type": "RAID5",
        "disk_group": "1",
    }

    response = client.post("/api/types/poolUnit/instances", json=pool_unit_data, headers=get_auth_headers())
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == pool_unit_data["name"]
    assert "id" in data


def test_get_pool_unit():
    """Test getting a specific pool unit."""
    # First create a pool unit
    pool_unit_data = {
        "name": "test_pool_unit",
        "type": PoolUnitTypeEnum.VIRTUAL_DISK,
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000,
    }
    create_response = client.post("/api/types/poolUnit/instances", json=pool_unit_data, headers=get_auth_headers())
    pool_unit_id = create_response.json()["id"]

    # Then get it
    response = client.get(f"/api/types/poolUnit/instances/{pool_unit_id}", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pool_unit_id
    assert data["name"] == pool_unit_data["name"]


def test_list_pool_units():
    """Test listing all pool units."""
    response = client.get("/api/types/poolUnit/instances", headers=get_auth_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_pool_unit():
    """Test updating a pool unit."""
    # First create a pool unit
    pool_unit_data = {
        "name": "test_pool_unit",
        "type": PoolUnitTypeEnum.VIRTUAL_DISK,
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000,
    }
    create_response = client.post("/api/types/poolUnit/instances", json=pool_unit_data, headers=get_auth_headers())
    pool_unit_id = create_response.json()["id"]

    # Then update it
    update_data = {"name": "updated_pool_unit", "description": "Updated description"}
    response = client.patch(
        f"/api/types/poolUnit/instances/{pool_unit_id}",
        json=update_data,
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_delete_pool_unit():
    """Test deleting a pool unit."""
    # First create a pool unit
    pool_unit_data = {
        "name": "test_pool_unit",
        "type": PoolUnitTypeEnum.VIRTUAL_DISK,
        "size_total": 1000000,
        "size_used": 0,
        "size_free": 1000000,
    }
    create_response = client.post("/api/types/poolUnit/instances", json=pool_unit_data, headers=get_auth_headers())
    pool_unit_id = create_response.json()["id"]

    # Then delete it
    response = client.delete(f"/api/types/poolUnit/instances/{pool_unit_id}", headers=get_auth_headers())
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/types/poolUnit/instances/{pool_unit_id}", headers=get_auth_headers())
    assert get_response.status_code == 404


@pytest.fixture
def pool_controller():
    """Fixture for pool controller."""
    return PoolController()


@pytest.fixture
def base_pool_data():
    """Fixture for base pool data."""
    return {
        "name": "test_pool",
        "raidType": "RAID5",
        "sizeTotal": 1000000,
        "isHarvestEnabled": False,
        "isSnapHarvestEnabled": False,
    }

    # def test_recommend_auto_configuration_no_pools(pool_controller):
    """Test auto configuration recommendations when no pools exist."""
    recommendations = pool_controller.recommend_auto_configuration()

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    # Check SSD configuration
    ssd_config = next(r for r in recommendations if "ssd" in r.name.lower())
    assert ssd_config.storageConfiguration.raidType == "RAID5"
    assert ssd_config.storageConfiguration.diskCount == 5  # 4+1 RAID5
    assert not ssd_config.isFastCacheEnabled  # Not needed for all-flash

    # Check SAS configuration
    sas_config = next(r for r in recommendations if "sas" in r.name.lower())
    assert sas_config.storageConfiguration.raidType == "RAID6"
    assert sas_config.storageConfiguration.diskCount == 8  # 6+2 RAID6
    assert sas_config.isFastCacheEnabled  # Should be enabled for HDD

    # def test_create_pool_with_harvest_validation(pool_controller):
    """Test validation of harvest settings in pool creation."""
    # Test with harvest enabled but no thresholds
    with pytest.raises(ValidationError) as exc_info:
        PoolCreate(
            name="test_pool",
            description="Test pool",
            raidType=RaidTypeEnum.RAID5,
            sizeTotal=1000000,
            isHarvestEnabled=True,  # Enable harvest but don't set thresholds
            alertThreshold=50,
            type="dynamic",
        )
    error_msg = str(exc_info.value)
    assert "Pool space harvest high threshold must be set when harvesting is enabled" in error_msg

    # Test with snap harvest enabled but no thresholds
    with pytest.raises(ValidationError) as exc_info:
        PoolCreate(
            name="test_pool",
            description="Test pool",
            raidType=RaidTypeEnum.RAID5,
            sizeTotal=1000000,
            isSnapHarvestEnabled=True,  # Enable snap harvest but don't set thresholds
            alertThreshold=50,
            type="dynamic",
        )
    error_msg = str(exc_info.value)
    assert "Snap space harvest high threshold must be set when snap harvesting is enabled" in error_msg

    # Test with invalid threshold values (low >= high)
    with pytest.raises(ValidationError) as exc_info:
        PoolCreate(
            name="test_pool",
            description="Test pool",
            raidType=RaidTypeEnum.RAID5,
            sizeTotal=1000000,
            isHarvestEnabled=True,
            poolSpaceHarvestHighThreshold=80.0,
            poolSpaceHarvestLowThreshold=85.0,  # Low threshold higher than high threshold
            alertThreshold=50,
            type="dynamic",
        )
    error_msg = str(exc_info.value)
    assert "Low threshold must be less than high threshold" in error_msg

    # Test creating pool with valid harvest settings
    pool_data = {
        "name": "test_pool",
        "description": "Test pool",
        "raidType": RaidTypeEnum.RAID5,
        "sizeTotal": 1000000,
        "isHarvestEnabled": True,
        "poolSpaceHarvestHighThreshold": 85.0,
        "poolSpaceHarvestLowThreshold": 75.0,
        "alertThreshold": 50,
        "type": "dynamic",
    }
    pool = PoolCreate(**pool_data)
    assert pool.isHarvestEnabled is True
    assert pool.poolSpaceHarvestHighThreshold == 85.0
    assert pool.poolSpaceHarvestLowThreshold == 75.0

    # Test creating pool with valid harvest settings
    pool_data = {
        "name": "test_pool",
        "raidType": RaidTypeEnum.RAID5,
        "sizeTotal": 1000000,
        "isHarvestEnabled": True,
        "poolSpaceHarvestHighThreshold": 80.0,
        "poolSpaceHarvestLowThreshold": 70.0,
    }
    pool = pool_controller.create_pool(PoolCreate(**pool_data))
    assert pool.isHarvestEnabled is True
    assert pool.poolSpaceHarvestHighThreshold == 80.0
    assert pool.poolSpaceHarvestLowThreshold == 70.0
    assert pool.harvestState == HarvestStateEnum.IDLE


def test_update_pool_with_harvest_validation(pool_controller):
    """Test pool update with harvest settings validation."""
    # Create a pool first
    pool_data = {"name": "test_pool", "raidType": "RAID5", "sizeTotal": 1000000, "isHarvestEnabled": False}
    pool = pool_controller.create_pool(PoolCreate(**pool_data))

    # Test updating with harvest enabled but no thresholds
    update_data = {"isHarvestEnabled": True}
    with pytest.raises(HTTPException) as exc_info:
        pool_controller.update_pool(pool.id, PoolUpdate(**update_data))
    assert exc_info.value.status_code == 422
    assert "harvest high threshold must be set" in exc_info.value.detail

    # Test updating with valid harvest settings
    update_data = {
        "isHarvestEnabled": True,
        "poolSpaceHarvestHighThreshold": 85.0,
        "poolSpaceHarvestLowThreshold": 75.0,
    }
    updated_pool = pool_controller.update_pool(pool.id, PoolUpdate(**update_data))
    assert updated_pool.isHarvestEnabled is True
    assert updated_pool.poolSpaceHarvestHighThreshold == 85.0
    assert updated_pool.poolSpaceHarvestLowThreshold == 75.0
    assert updated_pool.harvestState == HarvestStateEnum.IDLE
