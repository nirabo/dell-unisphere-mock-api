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
    headers, _ = auth_headers  # Unpack the tuple
    response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_pool_data["name"]
    assert data["description"] == sample_pool_data["description"]
    assert "id" in data


def test_get_pool(test_client, auth_headers, sample_pool_data):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201
    pool_id = create_response.json()["id"]

    # Then get it by ID
    response = test_client.get(f"/api/instances/pool/{pool_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pool_id
    assert data["name"] == sample_pool_data["name"]


def test_get_pool_by_name(test_client, auth_headers, sample_pool_data):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201

    # Then get it by name
    response = test_client.get(f"/api/instances/pool/name:{sample_pool_data['name']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_pool_data["name"]


def test_list_pools(test_client, auth_headers, sample_pool_data):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201

    # Then list all pools
    response = test_client.get("/api/types/pool/instances", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "@base" in data
    assert "entries" in data
    assert len(data["entries"]) > 0

    # Find our created pool in the list
    found_pool = None
    for pool in data["entries"]:
        if pool["content"]["name"] == sample_pool_data["name"]:
            found_pool = pool["content"]
            break

    assert found_pool is not None
    assert found_pool["name"] == sample_pool_data["name"]
    assert found_pool["description"] == sample_pool_data["description"]
    assert isinstance(found_pool["creationTime"], str)  # Should be ISO format string
    # assert found_pool["creationTime"].endswith("Z")  # UTC timezone


def test_modify_pool(test_client, auth_headers, sample_pool_data):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201
    pool_id = create_response.json()["id"]

    # Modify the pool
    update_data = {"description": "Modified test pool", "alertThreshold": 75}
    response = test_client.patch(f"/api/instances/pool/{pool_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update_data["description"]
    assert data["alertThreshold"] == update_data["alertThreshold"]


def test_delete_pool(test_client, auth_headers, sample_pool_data):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201
    pool_id = create_response.json()["id"]

    # Then delete it
    response = test_client.delete(f"/api/instances/pool/{pool_id}", headers=headers)
    assert response.status_code == 204

    # Verify it's gone
    get_response = test_client.get(f"/api/instances/pool/{pool_id}", headers=headers)
    assert get_response.status_code == 404


def test_delete_pool_by_name(test_client, auth_headers, sample_pool_data):
    headers, _ = auth_headers  # Unpack the tuple
    # First create a pool
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201

    # Delete the pool by name
    response = test_client.delete(f"/api/instances/pool/name:{sample_pool_data['name']}", headers=headers)
    assert response.status_code == 204

    # Verify it's gone
    get_response = test_client.get(f"/api/instances/pool/name:{sample_pool_data['name']}", headers=headers)
    assert get_response.status_code == 404


# def test_pool_create_harvest_threshold_validation():
#     """Test validation of harvest thresholds in pool creation."""
#     # Test invalid high/low threshold relationship
#     with pytest.raises(ValidationError) as exc_info:
#         PoolCreate(
#             name="test_pool",
#             description="Test pool",
#             raidType=RaidTypeEnum.RAID5,
#             sizeTotal=1000000,
#             isHarvestEnabled=True,
#             poolSpaceHarvestHighThreshold=70.0,
#             poolSpaceHarvestLowThreshold=80.0,  # Low threshold higher than high threshold
#             alertThreshold=50,
#             type="dynamic"
#         )
#     assert "Low threshold must be less than high threshold" in str(exc_info.value)

#     # Test missing high threshold
#     with pytest.raises(ValidationError) as exc_info:
#         PoolCreate(
#             name="test_pool",
#             description="Test pool",
#             raidType=RaidTypeEnum.RAID5,
#             sizeTotal=1000000,
#             isHarvestEnabled=True,  # Enabled but no high threshold
#             poolSpaceHarvestLowThreshold=60.0,
#             alertThreshold=50,
#             type="dynamic"
#         )
#     assert "Pool space harvest high threshold must be set when harvesting is enabled" in str(exc_info.value)d


def test_harvest_state_enum():
    """Test HarvestStateEnum values."""
    assert HarvestStateEnum.IDLE.value == "IDLE"
    assert HarvestStateEnum.HARVESTING.value == "HARVESTING"
    assert HarvestStateEnum.PAUSED.value == "PAUSED"
    assert HarvestStateEnum.ERROR.value == "ERROR"

    # Test that the enum can be used in Pool schema
    pool_fastvp = PoolFASTVP(
        status=FastVPStatusEnum.IDLE,
        relocationRate=FastVPRelocationRateEnum.MEDIUM,
        isScheduleEnabled=False,
        relocationDurationEstimate=None,
        sizeMovingDown=0,
        sizeMovingUp=0,
        sizeMovingWithin=0,
        percentComplete=0,
        type="None",
        dataRelocated=0,
        lastStartTime=None,
        lastEndTime=None,
    )

    pool = Pool(
        id="test_id",
        name="test_pool",
        description="Test pool",
        raidType=RaidTypeEnum.RAID5,
        sizeTotal=1000000,
        sizeFree=1000000,
        sizeUsed=0,
        sizePreallocated=0,
        sizeSubscribed=1000000,
        alertThreshold=50,
        creationTime="2025-01-03T12:00:00Z",
        isHarvestEnabled=False,
        isSnapHarvestEnabled=False,
        harvestState=HarvestStateEnum.IDLE,
        poolSpaceHarvestHighThreshold=None,
        poolSpaceHarvestLowThreshold=None,
        snapSpaceHarvestHighThreshold=None,
        snapSpaceHarvestLowThreshold=None,
        dataReductionSizeSaved=0,
        dataReductionPercent=0,
        dataReductionRatio=1.0,
        flashPercentage=0,
        hasDataReductionEnabledLuns=False,
        hasDataReductionEnabledFs=False,
        isFASTCacheEnabled=False,
        isEmpty=True,
        poolFastVP=pool_fastvp,
        tiers=[],
        metadataSizeSubscribed=0,
        snapSizeSubscribed=0,
        nonBaseSizeSubscribed=0,
        metadataSizeUsed=0,
        snapSizeUsed=0,
        nonBaseSizeUsed=0,
        type="dynamic",
        isAllFlash=False,
    )
    assert pool.harvestState == HarvestStateEnum.IDLE


def test_pool_auto_configuration_response():
    """Test PoolAutoConfigurationResponse schema."""
    config = PoolAutoConfigurationResponse(
        name="recommended_ssd_pool",
        description="Test configuration",
        storageConfiguration={"raidType": "RAID5", "diskGroup": "dg_ssd", "diskCount": 5, "stripeWidth": 5},
        maxSizeLimit=10995116277760,
        maxDiskNumberLimit=16,
        isFastCacheEnabled=False,
        isDiskTechnologyMixed=False,
        isRPMMixed=False,
    )

    assert config.name == "recommended_ssd_pool"
    assert config.storageConfiguration.raidType == "RAID5"
    assert config.storageConfiguration.diskCount == 5
    assert config.maxDiskNumberLimit == 16
    assert config.poolSpaceHarvestHighThreshold == 85.0  # Default value
    assert config.poolSpaceHarvestLowThreshold == 75.0  # Default value


def test_recommend_auto_configuration(test_client, auth_headers):
    """Test pool auto-configuration endpoint."""
    headers, _ = auth_headers  # Unpack the tuple
    # Should work when no pools exist
    response = test_client.post("/api/types/pool/action/recommendAutoConfiguration", headers=headers)
    assert response.status_code == 200

    configs = response.json()
    assert isinstance(configs, list)
    assert len(configs) > 0

    # Verify structure of returned configurations
    for config in configs:
        assert "name" in config
        assert "storageConfiguration" in config
        assert "raidType" in config["storageConfiguration"]
        assert "diskCount" in config["storageConfiguration"]
        assert "stripeWidth" in config["storageConfiguration"]

    # Create a pool
    sample_pool_data = {"name": "test_pool", "raidType": "RAID5", "sizeTotal": 1000000}
    create_response = test_client.post("/api/types/pool/instances", json=sample_pool_data, headers=headers)
    assert create_response.status_code == 201

    # Should fail when pools exist
    response = test_client.post("/api/types/pool/action/recommendAutoConfiguration", headers=headers)
    assert response.status_code == 400
    assert "Auto configuration is only available when no pools exist" in response.json()["detail"]


def test_pool_create_with_harvest_settings(test_client, auth_headers):
    """Test pool creation with harvest settings."""
    headers, _ = auth_headers  # Unpack the tuple

    # Test creating pool with harvest enabled but no thresholds
    invalid_pool_data = {
        "name": "test_pool_harvest",
        "description": "Test pool with harvest",
        "raidType": "RAID5",
        "sizeTotal": 1000000,
        "isHarvestEnabled": True,  # Missing thresholds
        "alertThreshold": 50,
        "type": "dynamic",
    }
    response = test_client.post("/api/types/pool/instances", json=invalid_pool_data, headers=headers)
    assert response.status_code == 422
    assert "Pool space harvest high threshold must be set when harvesting is enabled" in response.json()["detail"]

    # Test creating pool with valid harvest settings
    valid_pool_data = {
        "name": "test_pool_harvest",
        "description": "Test pool with harvest",
        "raidType": "RAID5",
        "sizeTotal": 1000000,
        "isHarvestEnabled": True,
        "poolSpaceHarvestHighThreshold": 80.0,
        "poolSpaceHarvestLowThreshold": 70.0,
        "alertThreshold": 50,
        "type": "dynamic",
    }
    response = test_client.post("/api/types/pool/instances", json=valid_pool_data, headers=headers)
    assert response.status_code == 201
    created_pool = response.json()
    assert created_pool["isHarvestEnabled"] is True
    assert created_pool["poolSpaceHarvestHighThreshold"] == 80.0
    assert created_pool["poolSpaceHarvestLowThreshold"] == 70.0


def test_pool_update_harvest_settings(test_client, auth_headers):
    """Test updating pool harvest settings."""
    headers, _ = auth_headers  # Unpack the tuple
    # Create a pool first
    pool_data = {
        "name": "test_pool_update",
        "description": "Test pool for update testing",
        "raidType": "RAID5",
        "sizeTotal": 1000000,
        "isHarvestEnabled": False,  # Explicitly set to False
        "alertThreshold": 50,
        "type": "dynamic",
    }
    create_response = test_client.post("/api/types/pool/instances", json=pool_data, headers=headers)
    assert create_response.status_code == 201
    pool_id = create_response.json()["id"]

    # Update with invalid harvest settings
    invalid_update = {"isHarvestEnabled": True}  # Missing thresholds
    response = test_client.patch(f"/api/instances/pool/{pool_id}", json=invalid_update, headers=headers)
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert "harvest high threshold must be set" in error_detail

    # Update with valid harvest settings
    valid_update = {
        "isHarvestEnabled": True,
        "poolSpaceHarvestHighThreshold": 85.0,
        "poolSpaceHarvestLowThreshold": 75.0,
    }
    response = test_client.patch(f"/api/instances/pool/{pool_id}", json=valid_update, headers=headers)
    assert response.status_code == 200
    updated_pool = response.json()
    assert updated_pool["isHarvestEnabled"] is True
    assert updated_pool["poolSpaceHarvestHighThreshold"] == 85.0
    assert updated_pool["poolSpaceHarvestLowThreshold"] == 75.0
