import pytest
from pydantic import ValidationError

from dell_unisphere_mock_api.main import app
from dell_unisphere_mock_api.schemas.pool import (
    FastVPRelocationRateEnum,
    FastVPStatusEnum,
    HarvestStateEnum,
    Pool,
    PoolAutoConfigurationResponse,
    PoolCreate,
    PoolFASTVP,
    RaidTypeEnum,
)


@pytest.fixture
def sample_pool_data():
    """Fixture for sample pool data."""
    return {
        "name": "test_pool",
        "description": "Test pool",
        "raidType": "RAID5",
        "sizeTotal": 1000000,
        "alertThreshold": 50,
        "isHarvestEnabled": False,  # Explicitly set to False
        "isSnapHarvestEnabled": False,  # Explicitly set to False
        "isFASTCacheEnabled": False,
        "type": "dynamic",
    }


def test_create_pool(test_client, auth_headers, sample_pool_data):
    """Test creating a pool."""
    headers, base_headers = auth_headers  # Unpack the tuple
    # Use base_headers if headers don't have CSRF token
    request_headers = headers if "EMC-CSRF-TOKEN" in headers else base_headers
    response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=request_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["entries"][0]["content"]["name"] == sample_pool_data["name"]
    assert data["entries"][0]["content"]["description"] == sample_pool_data["description"]
    assert "id" in data["entries"][0]["content"]
    assert "modificationTime" in data["entries"][0]["content"]
    assert "creationTime" in data["entries"][0]["content"]


def test_get_pool(test_client, auth_headers, sample_pool_data):
    """Test getting a pool by ID."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201
    pool_id = create_response.json()["entries"][0]["content"]["id"]

    # Then get it by ID
    response = test_client.get(f"/api/instances/pool/{pool_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["entries"][0]["content"]["id"] == pool_id
    assert data["entries"][0]["content"]["name"] == sample_pool_data["name"]
    assert "modificationTime" in data["entries"][0]["content"]
    assert "creationTime" in data["entries"][0]["content"]


def test_get_pool_by_name(test_client, auth_headers, sample_pool_data):
    """Test getting a pool by name."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201

    # Then get it by name
    response = test_client.get(f"/api/instances/pool/name:{sample_pool_data['name']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["entries"][0]["content"]["name"] == sample_pool_data["name"]
    assert "modificationTime" in data["entries"][0]["content"]
    assert "creationTime" in data["entries"][0]["content"]


def test_list_pools(test_client, auth_headers, sample_pool_data):
    """Test listing pools."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201

    # Then list all pools
    response = test_client.get("/api/types/pool/instances", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["entries"], list)
    assert len(data["entries"]) > 0
    assert data["entries"][0]["content"]["name"] == sample_pool_data["name"]
    assert "modificationTime" in data["entries"][0]["content"]
    assert "creationTime" in data["entries"][0]["content"]


def test_modify_pool(test_client, auth_headers, sample_pool_data):
    """Test modifying a pool."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201
    pool_id = create_response.json()["entries"][0]["content"]["id"]
    initial_modification_time = create_response.json()["entries"][0]["content"]["modificationTime"]

    # Then modify it
    update_data = {"name": "updated_pool", "description": "Updated pool description"}
    response = test_client.patch(f"/api/instances/pool/{pool_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["entries"][0]["content"]["name"] == update_data["name"]
    assert data["entries"][0]["content"]["description"] == update_data["description"]
    assert data["entries"][0]["content"]["modificationTime"] > initial_modification_time


def test_delete_pool(test_client, auth_headers, sample_pool_data):
    """Test deleting a pool."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201
    pool_id = create_response.json()["entries"][0]["content"]["id"]

    # Then delete it
    response = test_client.delete(f"/api/instances/pool/{pool_id}", headers=headers)
    assert response.status_code == 204

    # Verify it's gone
    response = test_client.get(f"/api/instances/pool/{pool_id}", headers=headers)
    assert response.status_code == 404


def test_delete_pool_by_name(test_client, auth_headers, sample_pool_data):
    """Test deleting a pool by name."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201

    # Then delete it by name
    response = test_client.delete(f"/api/instances/pool/name:{sample_pool_data['name']}", headers=headers)
    assert response.status_code == 204

    # Verify it's gone
    response = test_client.get(f"/api/instances/pool/name:{sample_pool_data['name']}", headers=headers)
    assert response.status_code == 404


def test_recommend_auto_configuration(test_client, auth_headers):
    """Test pool auto-configuration endpoint."""
    headers, _ = auth_headers  # Unpack the tuple
    response = test_client.get("/api/types/pool/action/recommendAutoConfiguration", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["entries"], list)
    assert len(data["entries"]) > 0

    # Check SSD configuration
    ssd_config = next(r for r in data["entries"] if "ssd" in r["content"]["name"].lower())
    assert ssd_config["content"]["storageConfiguration"]["raidType"] == "RAID5"
    assert ssd_config["content"]["storageConfiguration"]["diskCount"] == 5  # 4+1 RAID5
    assert not ssd_config["content"]["isFastCacheEnabled"]  # Not needed for all-flash

    # Check SAS configuration
    sas_config = next(r for r in data["entries"] if "sas" in r["content"]["name"].lower())
    assert sas_config["content"]["storageConfiguration"]["raidType"] == "RAID6"
    assert sas_config["content"]["storageConfiguration"]["diskCount"] == 8  # 6+2 RAID6
    assert sas_config["content"]["isFastCacheEnabled"]  # Should be enabled for HDD


def test_pool_create_with_harvest_settings(test_client, auth_headers):
    """Test pool creation with harvest settings."""
    headers, _ = auth_headers  # Unpack the tuple
    pool_data = {
        "name": "test_pool_harvest",
        "description": "Test pool with harvest settings",
        "raidType": "RAID5",
        "sizeTotal": 1000000,
        "alertThreshold": 50,
        "isHarvestEnabled": True,
        "poolSpaceHarvestHighThreshold": 85.0,
        "poolSpaceHarvestLowThreshold": 75.0,
        "isSnapHarvestEnabled": True,
        "snapSpaceHarvestHighThreshold": 85.0,
        "snapSpaceHarvestLowThreshold": 75.0,
        "isFASTCacheEnabled": False,
        "type": "dynamic",
    }

    response = test_client.post("/api/types/pool/instances", json=pool_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["entries"][0]["content"]["isHarvestEnabled"]
    assert data["entries"][0]["content"]["isSnapHarvestEnabled"]
    assert data["entries"][0]["content"]["poolSpaceHarvestHighThreshold"] == 85.0
    assert data["entries"][0]["content"]["poolSpaceHarvestLowThreshold"] == 75.0
    assert data["entries"][0]["content"]["snapSpaceHarvestHighThreshold"] == 85.0
    assert data["entries"][0]["content"]["snapSpaceHarvestLowThreshold"] == 75.0
    assert data["entries"][0]["content"]["harvestState"] == HarvestStateEnum.IDLE


def test_pool_update_harvest_settings(test_client, auth_headers):
    """Test updating pool harvest settings."""
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool with harvest disabled
    pool_data = {
        "name": "test_pool_harvest_update",
        "description": "Test pool for harvest settings update",
        "raidType": "RAID5",
        "sizeTotal": 1000000,
        "alertThreshold": 50,
        "isHarvestEnabled": False,
        "isSnapHarvestEnabled": False,
        "isFASTCacheEnabled": False,
        "type": "dynamic",
    }

    create_response = test_client.post("/api/types/pool/instances", json=pool_data, headers=headers)
    assert create_response.status_code == 201
    pool_id = create_response.json()["entries"][0]["content"]["id"]

    # Then update harvest settings
    update_data = {
        "isHarvestEnabled": True,
        "poolSpaceHarvestHighThreshold": 85.0,
        "poolSpaceHarvestLowThreshold": 75.0,
        "isSnapHarvestEnabled": True,
        "snapSpaceHarvestHighThreshold": 85.0,
        "snapSpaceHarvestLowThreshold": 75.0,
    }

    response = test_client.patch(f"/api/instances/pool/{pool_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["entries"][0]["content"]["isHarvestEnabled"]
    assert data["entries"][0]["content"]["isSnapHarvestEnabled"]
    assert data["entries"][0]["content"]["poolSpaceHarvestHighThreshold"] == 85.0
    assert data["entries"][0]["content"]["poolSpaceHarvestLowThreshold"] == 75.0
    assert data["entries"][0]["content"]["snapSpaceHarvestHighThreshold"] == 85.0
    assert data["entries"][0]["content"]["snapSpaceHarvestLowThreshold"] == 75.0
    assert data["entries"][0]["content"]["harvestState"] == HarvestStateEnum.IDLE


def test_harvest_state_enum():
    """Test HarvestStateEnum values."""
    assert HarvestStateEnum.IDLE == "Idle"
    assert HarvestStateEnum.HARVESTING == "Harvesting"
    assert HarvestStateEnum.PAUSED == "Paused"
    assert HarvestStateEnum.SUSPENDED == "Suspended"
    assert HarvestStateEnum.COMPLETED == "Completed"
    assert HarvestStateEnum.FAILED == "Failed"
    assert HarvestStateEnum.CANCELLING == "Cancelling"
    assert HarvestStateEnum.CANCELLED == "Cancelled"
    assert HarvestStateEnum.QUEUED == "Queued"
    assert HarvestStateEnum.UNKNOWN == "Unknown"


def test_pool_auto_configuration_response():
    """Test PoolAutoConfigurationResponse schema."""
    config = PoolAutoConfigurationResponse(
        name="Test Config",
        description="Test configuration",
        storageConfiguration={
            "raidType": RaidTypeEnum.RAID5,
            "diskGroup": "1",
            "diskCount": 5,
            "stripeWidth": 4,
        },
        alertThreshold=70,
        poolSpaceHarvestHighThreshold=85.0,
        poolSpaceHarvestLowThreshold=75.0,
        snapSpaceHarvestHighThreshold=85.0,
        snapSpaceHarvestLowThreshold=75.0,
        isFastCacheEnabled=False,
        isFASTVpScheduleEnabled=False,
        isDiskTechnologyMixed=False,
        maxSizeLimit=10000000000000,
        maxDiskNumberLimit=16,
        isMaxSizeLimitExceeded=False,
        isMaxDiskNumberLimitExceeded=False,
        isRPMMixed=False,
    )

    assert config.name == "Test Config"
    assert config.description == "Test configuration"
    assert config.storageConfiguration.raidType == RaidTypeEnum.RAID5
    assert config.storageConfiguration.diskCount == 5
    assert config.storageConfiguration.stripeWidth == 4
    assert not config.isFastCacheEnabled
    assert not config.isFASTVpScheduleEnabled
