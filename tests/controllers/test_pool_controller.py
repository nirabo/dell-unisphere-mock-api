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
    )


def test_create_pool(pool_controller, sample_pool_create, mock_request):
    """Test creating a pool."""
    response = pool_controller.create_pool(sample_pool_create, mock_request)
    assert len(response.entries) == 1
    pool = response.entries[0].content
    assert isinstance(pool, Pool)
    assert pool.name == sample_pool_create.name
    assert pool.description == sample_pool_create.description
    assert pool.raidType == sample_pool_create.raidType
    assert pool.sizeTotal == sample_pool_create.sizeTotal
    assert pool.isHarvestEnabled == sample_pool_create.isHarvestEnabled
    assert pool.harvestState == HarvestStateEnum.IDLE


def test_create_pool_duplicate_name(pool_controller, sample_pool_create, mock_request):
    """Test creating a pool with a duplicate name."""
    pool_controller.create_pool(sample_pool_create, mock_request)
    with pytest.raises(HTTPException) as exc_info:
        pool_controller.create_pool(sample_pool_create, mock_request)
    assert exc_info.value.status_code == 409


def test_get_pool(pool_controller, sample_pool_create, mock_request):
    """Test getting a pool by ID."""
    created_response = pool_controller.create_pool(sample_pool_create, mock_request)
    created_pool = created_response.entries[0].content
    response = pool_controller.get_pool(created_pool.id, mock_request)
    assert len(response.entries) == 1
    pool = response.entries[0].content
    assert isinstance(pool, Pool)
    assert pool.id == created_pool.id
    assert pool.name == created_pool.name


def test_get_pool_not_found(pool_controller, mock_request):
    """Test getting a non-existent pool."""
    with pytest.raises(HTTPException) as exc_info:
        pool_controller.get_pool("non_existent_id", mock_request)
    assert exc_info.value.status_code == 404


def test_get_pool_by_name(pool_controller, sample_pool_create, mock_request):
    """Test getting a pool by name."""
    created_response = pool_controller.create_pool(sample_pool_create, mock_request)
    created_pool = created_response.entries[0].content
    response = pool_controller.get_pool_by_name(created_pool.name, mock_request)
    assert len(response.entries) == 1
    pool = response.entries[0].content
    assert isinstance(pool, Pool)
    assert pool.id == created_pool.id
    assert pool.name == created_pool.name


def test_get_pool_by_name_not_found(pool_controller, mock_request):
    """Test getting a non-existent pool by name."""
    with pytest.raises(HTTPException) as exc_info:
        pool_controller.get_pool_by_name("non_existent_name", mock_request)
    assert exc_info.value.status_code == 404


def test_list_pools(pool_controller, sample_pool_create, mock_request):
    """Test listing all pools."""
    # Create a pool first
    created_response = pool_controller.create_pool(sample_pool_create, mock_request)
    created_pool = created_response.entries[0].content

    # List pools
    response = pool_controller.list_pools(mock_request)
    assert len(response.entries) >= 1
    found = False
    for entry in response.entries:
        pool = entry.content
        if pool.id == created_pool.id:
            found = True
            assert pool.name == created_pool.name
            break
    assert found


def test_update_pool(pool_controller, sample_pool_create, mock_request):
    """Test updating a pool."""
    # Create a pool first
    created_response = pool_controller.create_pool(sample_pool_create, mock_request)
    created_pool = created_response.entries[0].content

    # Update the pool
    pool_update = PoolUpdate(name="updated_pool", description="Updated description")
    response = pool_controller.update_pool(created_pool.id, pool_update, mock_request)
    assert len(response.entries) == 1
    updated_pool = response.entries[0].content
    assert updated_pool.id == created_pool.id
    assert updated_pool.name == "updated_pool"
    assert updated_pool.description == "Updated description"


def test_update_pool_not_found(pool_controller, mock_request):
    """Test updating a non-existent pool."""
    pool_update = PoolUpdate(name="updated_pool")
    with pytest.raises(HTTPException) as exc_info:
        pool_controller.update_pool("non_existent_id", pool_update, mock_request)
    assert exc_info.value.status_code == 404


def test_delete_pool(pool_controller, sample_pool_create, mock_request):
    """Test deleting a pool."""
    created_response = pool_controller.create_pool(sample_pool_create, mock_request)
    created_pool = created_response.entries[0].content
    pool_controller.delete_pool(created_pool.id, mock_request)
    with pytest.raises(HTTPException) as exc_info:
        pool_controller.get_pool(created_pool.id, mock_request)
    assert exc_info.value.status_code == 404


def test_delete_pool_not_found(pool_controller, mock_request):
    """Test deleting a non-existent pool."""
    with pytest.raises(HTTPException) as exc_info:
        pool_controller.delete_pool("non_existent_id", mock_request)
    assert exc_info.value.status_code == 404


def test_delete_pool_by_name(pool_controller, sample_pool_create, mock_request):
    """Test deleting a pool by name."""
    created_response = pool_controller.create_pool(sample_pool_create, mock_request)
    created_pool = created_response.entries[0].content
    pool_controller.delete_pool_by_name(created_pool.name, mock_request)
    with pytest.raises(HTTPException) as exc_info:
        pool_controller.get_pool_by_name(created_pool.name, mock_request)
    assert exc_info.value.status_code == 404


def test_delete_pool_by_name_not_found(pool_controller, mock_request):
    """Test deleting a non-existent pool by name."""
    with pytest.raises(HTTPException) as exc_info:
        pool_controller.delete_pool_by_name("non_existent_name", mock_request)
    assert exc_info.value.status_code == 404


def test_recommend_auto_configuration(pool_controller, mock_request):
    """Test getting pool auto configuration recommendations."""
    response = pool_controller.recommend_auto_configuration(mock_request)
    assert len(response.entries) > 0
    for entry in response.entries:
        recommendation = entry.content
        assert isinstance(recommendation, PoolAutoConfigurationResponse)
        assert recommendation.name
        assert recommendation.description
        assert recommendation.storageConfiguration
        assert 50 <= recommendation.alertThreshold <= 84
        assert 0 <= recommendation.poolSpaceHarvestHighThreshold <= 100
        assert 0 <= recommendation.poolSpaceHarvestLowThreshold <= 100
        assert recommendation.poolSpaceHarvestLowThreshold < recommendation.poolSpaceHarvestHighThreshold
