import base64
from typing import Dict

import pytest
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.main import app
from dell_unisphere_mock_api.models.disk import DiskModel
from dell_unisphere_mock_api.models.disk_group import DiskGroupModel
from dell_unisphere_mock_api.models.job import JobModel
from dell_unisphere_mock_api.models.lun import LUNModel
from dell_unisphere_mock_api.models.pool import PoolModel
from dell_unisphere_mock_api.models.pool_unit import PoolUnitModel


@pytest.fixture(autouse=True)
def clear_data():
    """Clear all data before each test."""
    pool_model = PoolModel()
    lun_model = LUNModel()
    disk_model = DiskModel()
    disk_group_model = DiskGroupModel()
    pool_unit_model = PoolUnitModel()

    # Clear all data
    pool_model.pools.clear()
    lun_model.luns.clear()
    if hasattr(disk_model, "disks"):
        disk_model.disks.clear()
    if hasattr(disk_group_model, "disk_groups"):
        disk_group_model.disk_groups.clear()
    if hasattr(pool_unit_model, "pool_units"):
        pool_unit_model.pool_units.clear()

    # Clear job data
    job_model = JobModel()
    if hasattr(job_model, "jobs"):
        job_model.jobs.clear()
    yield


@pytest.fixture
def test_client():
    """Create a test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers(test_client):
    """Create headers with authentication and CSRF token for test requests."""
    # Create Basic Auth header with correct password
    credentials = base64.b64encode(b"admin:Password123!").decode("utf-8")
    headers = {
        "Authorization": f"Basic {credentials}",
        "X-EMC-REST-CLIENT": "true",  # Make sure this matches case exactly
        "EMC-CSRF-TOKEN": "test-csrf-token",
    }
    return headers, {}  # Return headers and empty cookies dict
