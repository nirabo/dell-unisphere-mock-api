from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from dell_unisphere_mock_api.controllers.pool_controller import PoolController
from dell_unisphere_mock_api.schemas.pool import (
    HarvestStateEnum,
    Pool,
    PoolAutoConfigurationResponse,
    PoolCreate,
    PoolUpdate,
    RaidTypeEnum,
)


@pytest.fixture
def mock_request():
    class MockRequest:
        def __init__(self):
            self.base_url = "http://testserver"
            self.path = "/api/types/pool/instances"
            self.url = type("URL", (), {"path": "/api/types/pool/instances"})()

    return MockRequest()


@pytest.fixture
def pool_controller():
    return PoolController()


@pytest.fixture
def sample_pool_create():
    return PoolCreate(
        name="test_pool",
        description="Test pool",
        raidType=RaidTypeEnum.RAID5,
        sizeTotal=10995116277760,  # 10TB
        isHarvestEnabled=True,
        poolSpaceHarvestHighThreshold=80,
        poolSpaceHarvestLowThreshold=60,
        isSnapHarvestEnabled=True,
        snapSpaceHarvestHighThreshold=80,
        snapSpaceHarvestLowThreshold=60,
        alertThreshold=70,
        isAllFlashPool=True,
    )


def test_create_pool(pool_controller, sample_pool_create, mock_request):
    """Test creating a new pool."""
    response = pool_controller.create_pool(sample_pool_create, mock_request)
    assert response.base == "http://testserver/api/types/pool/instances"
    assert len(response.entries) == 1

    pool = response.entries[0].content
    assert pool.name == "test_pool"
    assert pool.description == "Test pool"
    assert pool.sizeTotal == 10995116277760
    assert pool.isHarvestEnabled is True
    assert pool.poolSpaceHarvestHighThreshold == 80
    assert pool.poolSpaceHarvestLowThreshold == 60
    assert pool.isSnapHarvestEnabled is True
    assert pool.snapSpaceHarvestHighThreshold == 80
    assert pool.snapSpaceHarvestLowThreshold == 60
    assert pool.alertThreshold == 70
    assert pool.isAllFlash is True
    assert pool.harvestState == HarvestStateEnum.IDLE
    assert pool.isEmpty is True
    assert pool.raidType == RaidTypeEnum.RAID5

    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{pool.id}"


def test_create_pool_duplicate_name(pool_controller, sample_pool_create, mock_request):
    """Test creating a pool with a duplicate name."""
    pool_controller.create_pool(sample_pool_create, mock_request)
    with pytest.raises(HTTPException) as exc:
        pool_controller.create_pool(sample_pool_create, mock_request)
    assert exc.value.status_code == 422
    assert exc.value.detail == "Pool with name 'test_pool' already exists"


def test_get_pool(pool_controller, sample_pool_create, mock_request):
    """Test getting a pool by ID."""
    created = pool_controller.create_pool(sample_pool_create, mock_request)
    pool_id = created.entries[0].content.id

    response = pool_controller.get_pool(pool_id, mock_request)
    assert response.base == "http://testserver/api/types/pool/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == pool_id
    assert response.entries[0].content.name == "test_pool"
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{pool_id}"


def test_get_pool_not_found(pool_controller, mock_request):
    """Test getting a non-existent pool."""
    with pytest.raises(HTTPException) as exc:
        pool_controller.get_pool("nonexistent", mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Pool with ID 'nonexistent' not found"


def test_get_pool_by_name(pool_controller, sample_pool_create, mock_request):
    """Test getting a pool by name."""
    created = pool_controller.create_pool(sample_pool_create, mock_request)
    pool_id = created.entries[0].content.id

    response = pool_controller.get_pool_by_name("test_pool", mock_request)
    assert response.base == "http://testserver/api/types/pool/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == pool_id
    assert response.entries[0].content.name == "test_pool"
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{pool_id}"


def test_get_pool_by_name_not_found(pool_controller, mock_request):
    """Test getting a non-existent pool by name."""
    with pytest.raises(HTTPException) as exc:
        pool_controller.get_pool_by_name("nonexistent", mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Pool with name 'nonexistent' not found"


def test_list_pools(pool_controller, sample_pool_create, mock_request):
    """Test listing all pools."""
    created = pool_controller.create_pool(sample_pool_create, mock_request)
    pool_id = created.entries[0].content.id

    response = pool_controller.list_pools(mock_request)
    assert response.base == "http://testserver/api/types/pool/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == pool_id
    assert response.entries[0].content.name == "test_pool"
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{pool_id}"


def test_update_pool(pool_controller, sample_pool_create, mock_request):
    """Test updating a pool."""
    created = pool_controller.create_pool(sample_pool_create, mock_request)
    pool_id = created.entries[0].content.id

    update_data = PoolUpdate(
        description="Updated description",
        alertThreshold=75,
    )
    response = pool_controller.update_pool(pool_id, update_data, mock_request)
    assert response.base == "http://testserver/api/types/pool/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.description == "Updated description"
    assert response.entries[0].content.alertThreshold == 75
    # Original values should remain unchanged
    assert response.entries[0].content.name == "test_pool"
    assert response.entries[0].content.sizeTotal == 10995116277760


def test_update_pool_not_found(pool_controller, mock_request):
    """Test updating a non-existent pool."""
    update_data = PoolUpdate(description="Updated description")
    with pytest.raises(HTTPException) as exc:
        pool_controller.update_pool("nonexistent", update_data, mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Pool with ID 'nonexistent' not found"


def test_delete_pool(pool_controller, sample_pool_create, mock_request):
    """Test deleting a pool."""
    created = pool_controller.create_pool(sample_pool_create, mock_request)
    pool_id = created.entries[0].content.id

    response = pool_controller.delete_pool(pool_id, mock_request)
    assert response.base == "http://testserver/api/types/pool/instances"
    assert len(response.entries) == 0

    with pytest.raises(HTTPException) as exc:
        pool_controller.get_pool(pool_id, mock_request)
    assert exc.value.status_code == 404


def test_delete_pool_not_found(pool_controller, mock_request):
    """Test deleting a non-existent pool."""
    with pytest.raises(HTTPException) as exc:
        pool_controller.delete_pool("nonexistent", mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Pool with ID 'nonexistent' not found"


def test_delete_pool_by_name(pool_controller, sample_pool_create, mock_request):
    """Test deleting a pool by name."""
    pool_controller.create_pool(sample_pool_create, mock_request)
    response = pool_controller.delete_pool_by_name("test_pool", mock_request)
    assert response.base == "http://testserver/api/types/pool/instances"
    assert len(response.entries) == 0

    with pytest.raises(HTTPException) as exc:
        pool_controller.get_pool_by_name("test_pool", mock_request)
    assert exc.value.status_code == 404


def test_delete_pool_by_name_not_found(pool_controller, mock_request):
    """Test deleting a non-existent pool by name."""
    with pytest.raises(HTTPException) as exc:
        pool_controller.delete_pool_by_name("nonexistent", mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Pool with name 'nonexistent' not found"


def test_recommend_auto_configuration(pool_controller, mock_request):
    """Test getting pool auto configuration recommendations."""
    response = pool_controller.recommend_auto_configuration(mock_request)
    assert response.base == "http://testserver/api/types/pool/instances"
    assert len(response.entries) == 1

    config = response.entries[0].content
    assert config.name == "Recommended Pool Configuration"
    assert config.description == "Auto-generated pool configuration based on available drives"
    assert config.maxSizeLimit == 109951162777600  # 100TB
    assert config.maxDiskNumberLimit == 180

    # Check storage configuration
    assert config.storageConfiguration.raidType == RaidTypeEnum.RAID5
    assert config.storageConfiguration.stripeWidth == 5
    assert config.storageConfiguration.diskCount == 5
    assert config.storageConfiguration.diskGroup == "dg_ssd"

    # Check default values
    assert config.isFastCacheEnabled is False
    assert config.isFASTVpScheduleEnabled is False
    assert config.isDiskTechnologyMixed is False
    assert config.isMaxSizeLimitExceeded is False
    assert config.isMaxDiskNumberLimitExceeded is False
    assert config.isRPMMixed is False

    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == "/auto_config"
