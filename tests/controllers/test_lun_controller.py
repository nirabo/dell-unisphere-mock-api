from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from dell_unisphere_mock_api.controllers.lun_controller import LUNController
from dell_unisphere_mock_api.core.response_models import ApiResponse, Entry
from dell_unisphere_mock_api.schemas.lun import LUN, LUNCreate, LUNUpdate
from dell_unisphere_mock_api.schemas.pool import Pool, RaidTypeEnum


@pytest.fixture
def mock_request():
    class MockRequest:
        def __init__(self):
            self.base_url = "http://testserver"
            self.path = "/api/types/lun/instances"
            self.url = type("URL", (), {"path": "/api/types/lun/instances"})()

    return MockRequest()


@pytest.fixture
def sample_pool():
    """Create a sample pool for testing."""
    return Pool(
        id="test_pool_id",
        name="test_pool",
        description="Test pool",
        raidType=RaidTypeEnum.RAID5,
        sizeTotal=10995116277760,  # 10TB
        sizeFree=10995116277760,  # 10TB
        sizeUsed=0,
        sizePreallocated=0,
        dataReductionSizeSaved=0,
        dataReductionPercent=0,
        dataReductionRatio=1.0,
        flashPercentage=100,
        sizeSubscribed=10995116277760,
        alertThreshold=70,
        hasDataReductionEnabledLuns=False,
        hasDataReductionEnabledFs=False,
        isFASTCacheEnabled=False,
        creationTime=datetime.now(timezone.utc),
        isEmpty=True,
        poolFastVP=None,
        tiers=[],
        isHarvestEnabled=True,
        harvestState="IDLE",
        isSnapHarvestEnabled=True,
        poolSpaceHarvestHighThreshold=80.0,
        poolSpaceHarvestLowThreshold=60.0,
        snapSpaceHarvestHighThreshold=80.0,
        snapSpaceHarvestLowThreshold=60.0,
        metadataSizeSubscribed=0,
        snapSizeSubscribed=0,
        nonBaseSizeSubscribed=0,
        metadataSizeUsed=0,
        snapSizeUsed=0,
        nonBaseSizeUsed=0,
        rebalanceProgress=None,
        type="dynamic",
        isAllFlash=True,
    )


@pytest.fixture
def sample_lun_create(sample_pool):
    """Create a sample LUN create request for testing."""
    return LUNCreate(
        name="test_lun",
        description="Test LUN",
        pool_id=sample_pool.id,
        size=1099511627776,  # 1TB
        isThinEnabled=True,
        isDataReductionEnabled=False,
        type="thick",
    )


@pytest.fixture
def mock_pool_controller(sample_pool, mock_request):
    """Create a mock pool controller."""
    with patch("dell_unisphere_mock_api.controllers.pool_controller.PoolController") as mock:
        mock_instance = mock.return_value
        mock_instance.get_pool.return_value = ApiResponse(
            base="http://testserver/api/types/pool/instances",
            updated=datetime.now(timezone.utc).isoformat(),
            links=[{"rel": "self", "href": "/api/types/pool/instances"}],
            entries=[
                Entry(
                    base="http://testserver/api/types/pool/instances",
                    updated=datetime.now(timezone.utc).isoformat(),
                    content=sample_pool,
                    links=[{"rel": "self", "href": f"/{sample_pool.id}"}],
                )
            ],
        )
        yield mock_instance


@pytest.fixture
def lun_controller(mock_pool_controller):
    controller = LUNController()
    controller.pool_controller = mock_pool_controller
    return controller


def test_create_lun(lun_controller, sample_lun_create, mock_request):
    """Test creating a new LUN."""
    response = lun_controller.create_lun(sample_lun_create, mock_request)
    assert response.base == "http://testserver/api/types/lun/instances"
    assert len(response.entries) == 1

    lun = response.entries[0].content
    assert lun.name == "test_lun"
    assert lun.description == "Test LUN"
    assert lun.pool_id == "test_pool_id"
    assert lun.size == 1099511627776
    assert lun.isThinEnabled is True
    assert lun.isDataReductionEnabled is False

    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{lun.id}"


def test_create_lun_duplicate_name(lun_controller, sample_lun_create, mock_request):
    """Test creating a LUN with a duplicate name."""
    lun_controller.create_lun(sample_lun_create, mock_request)
    with pytest.raises(HTTPException) as exc:
        lun_controller.create_lun(sample_lun_create, mock_request)
    assert exc.value.status_code == 409
    assert exc.value.detail == "LUN with this name already exists"


def test_get_lun(lun_controller, sample_lun_create, mock_request):
    """Test getting a LUN by ID."""
    created = lun_controller.create_lun(sample_lun_create, mock_request)
    lun_id = created.entries[0].content.id

    response = lun_controller.get_lun(lun_id, mock_request)
    assert response.base == "http://testserver/api/types/lun/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == lun_id
    assert response.entries[0].content.name == "test_lun"
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{lun_id}"


def test_get_lun_not_found(lun_controller, mock_request):
    """Test getting a non-existent LUN."""
    with pytest.raises(HTTPException) as exc:
        lun_controller.get_lun("nonexistent", mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "LUN with ID 'nonexistent' not found"


def test_get_lun_by_name(lun_controller, sample_lun_create, mock_request):
    """Test getting a LUN by name."""
    created = lun_controller.create_lun(sample_lun_create, mock_request)
    lun_id = created.entries[0].content.id

    response = lun_controller.get_lun_by_name("test_lun", mock_request)
    assert response.base == "http://testserver/api/types/lun/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == lun_id
    assert response.entries[0].content.name == "test_lun"
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{lun_id}"


def test_get_lun_by_name_not_found(lun_controller, mock_request):
    """Test getting a non-existent LUN by name."""
    with pytest.raises(HTTPException) as exc:
        lun_controller.get_lun_by_name("nonexistent", mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "LUN with name 'nonexistent' not found"


def test_list_luns(lun_controller, sample_lun_create, mock_request):
    """Test listing all LUNs."""
    created = lun_controller.create_lun(sample_lun_create, mock_request)
    lun_id = created.entries[0].content.id

    response = lun_controller.list_luns(mock_request)
    assert response.base == "http://testserver/api/types/lun/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == lun_id
    assert response.entries[0].content.name == "test_lun"
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{lun_id}"


def test_get_luns_by_pool(lun_controller, sample_lun_create, mock_request):
    """Test getting LUNs by pool ID."""
    created = lun_controller.create_lun(sample_lun_create, mock_request)
    lun_id = created.entries[0].content.id

    response = lun_controller.get_luns_by_pool("test_pool_id", mock_request)
    assert response.base == "http://testserver/api/types/lun/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.id == lun_id
    assert response.entries[0].content.name == "test_lun"
    assert response.entries[0].links[0].rel == "self"
    assert response.entries[0].links[0].href == f"/{lun_id}"


def test_update_lun(lun_controller, sample_lun_create, mock_request):
    """Test updating a LUN."""
    created = lun_controller.create_lun(sample_lun_create, mock_request)
    lun_id = created.entries[0].content.id

    update_data = LUNUpdate(
        description="Updated description",
        isThinEnabled=False,
        isCompressionEnabled=True,
    )
    response = lun_controller.update_lun(lun_id, update_data, mock_request)
    assert response.base == "http://testserver/api/types/lun/instances"
    assert len(response.entries) == 1
    assert response.entries[0].content.description == "Updated description"
    assert response.entries[0].content.isThinEnabled is False
    assert response.entries[0].content.isCompressionEnabled is True
    # Original values should remain unchanged
    assert response.entries[0].content.name == "test_lun"
    assert response.entries[0].content.size == 1099511627776


def test_update_lun_not_found(lun_controller, mock_request):
    """Test updating a non-existent LUN."""
    update_data = LUNUpdate(description="Updated description")
    with pytest.raises(HTTPException) as exc:
        lun_controller.update_lun("nonexistent", update_data, mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "LUN with ID 'nonexistent' not found"


def test_update_lun_duplicate_name(lun_controller, sample_lun_create, mock_request):
    """Test updating a LUN with a duplicate name."""
    # Create first LUN
    lun_controller.create_lun(sample_lun_create, mock_request)

    # Create second LUN with different name
    second_lun = sample_lun_create.model_copy()
    second_lun.name = "test_lun_2"
    created = lun_controller.create_lun(second_lun, mock_request)
    second_lun_id = created.entries[0].content.id

    # Try to update second LUN with first LUN's name
    update_data = LUNUpdate(name="test_lun")
    with pytest.raises(HTTPException) as exc:
        lun_controller.update_lun(second_lun_id, update_data, mock_request)
    assert exc.value.status_code == 409
    assert exc.value.detail == "LUN with this name already exists"


def test_delete_lun(lun_controller, sample_lun_create, mock_request):
    """Test deleting a LUN."""
    created = lun_controller.create_lun(sample_lun_create, mock_request)
    lun_id = created.entries[0].content.id

    response = lun_controller.delete_lun(lun_id, mock_request)
    assert response.base == "http://testserver/api/types/lun/instances"
    assert len(response.entries) == 0

    with pytest.raises(HTTPException) as exc:
        lun_controller.get_lun(lun_id, mock_request)
    assert exc.value.status_code == 404


def test_delete_lun_not_found(lun_controller, mock_request):
    """Test deleting a non-existent LUN."""
    with pytest.raises(HTTPException) as exc:
        lun_controller.delete_lun("nonexistent", mock_request)
    assert exc.value.status_code == 404
    assert exc.value.detail == "LUN with ID 'nonexistent' not found"
