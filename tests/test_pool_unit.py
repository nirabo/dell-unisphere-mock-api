import pytest
from fastapi import HTTPException, Request
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


@pytest.fixture
def mock_request():
    """Fixture for mock request."""
    return Request({"type": "http", "method": "GET", "url": "http://test"})


@pytest.fixture
def pool_controller(mock_request):
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


def test_recommend_auto_configuration_no_pools(pool_controller, mock_request):
    """Test auto configuration recommendations when no pools exist."""
    recommendations = pool_controller.recommend_auto_configuration(mock_request)

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    # Check SSD configuration
    ssd_config = next(r for r in recommendations if "flash" in r.name.lower())
    assert ssd_config.storageConfiguration.raidType == RaidTypeEnum.RAID5
    assert ssd_config.storageConfiguration.diskCount == 5  # 4+1 RAID5
    assert not ssd_config.isFastCacheEnabled  # Not needed for all-flash

    # Check SAS configuration
    sas_config = next(r for r in recommendations if "sas" in r.name.lower())
    assert sas_config.storageConfiguration.raidType == RaidTypeEnum.RAID6
    assert sas_config.storageConfiguration.diskCount == 8  # 6+2 RAID6
    assert sas_config.isFastCacheEnabled  # Should be enabled for HDD


def test_create_pool_with_harvest_validation(pool_controller, mock_request):
    """Test validation of harvest settings in pool creation."""
    # Test creating pool with invalid harvest settings (high threshold < low threshold)
    pool_data = {
        "name": "test_pool_invalid_harvest",
        "description": "Test pool with invalid harvest settings",
        "raidType": RaidTypeEnum.RAID5,
        "sizeTotal": 1000000,
        "alertThreshold": 50,
        "isHarvestEnabled": True,
        "poolSpaceHarvestHighThreshold": 75.0,  # Invalid: high < low
        "poolSpaceHarvestLowThreshold": 85.0,
        "isSnapHarvestEnabled": False,
        "type": "dynamic",
    }

    with pytest.raises(HTTPException) as exc_info:
        pool_controller.create_pool(PoolCreate(**pool_data), mock_request)
    assert exc_info.value.status_code == 422
    assert "Low threshold must be less than high threshold" in exc_info.value.detail


def test_update_pool_with_harvest_validation(pool_controller, mock_request):
    """Test pool update with harvest settings validation."""
    # First create a pool
    pool_data = {
        "name": "test_pool_harvest_update",
        "description": "Test pool for harvest settings update",
        "raidType": RaidTypeEnum.RAID5,
        "sizeTotal": 1000000,
        "alertThreshold": 50,
        "isHarvestEnabled": False,
        "isSnapHarvestEnabled": False,
        "type": "dynamic",
    }
    pool = pool_controller.create_pool(PoolCreate(**pool_data), mock_request)

    # Test updating pool with invalid harvest settings (missing thresholds)
    update_data = {
        "isHarvestEnabled": True,  # Enable harvesting without setting thresholds
    }

    with pytest.raises(HTTPException) as exc_info:
        pool_controller.update_pool(pool.id, PoolUpdate(**update_data), mock_request)
    assert exc_info.value.status_code == 422
    assert "Pool space harvest high threshold must be set when harvesting is enabled" in exc_info.value.detail
