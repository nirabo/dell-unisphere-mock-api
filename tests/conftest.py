import base64

import pytest
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.controllers.cifs_server_controller import CIFSServerController
from dell_unisphere_mock_api.controllers.nfs_share_controller import NFSShareController
from dell_unisphere_mock_api.controllers.quota_controller import QuotaController
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
    cifs_server_controller = CIFSServerController()
    nfs_share_controller = NFSShareController()
    quota_controller = QuotaController()

    # Clear all data
    pool_model.pools.clear()
    lun_model.luns.clear()
    if hasattr(disk_model, "disks"):
        disk_model.disks.clear()
    if hasattr(disk_group_model, "disk_groups"):
        disk_group_model.disk_groups.clear()
    if hasattr(pool_unit_model, "pool_units"):
        pool_unit_model.pool_units.clear()
    if hasattr(cifs_server_controller, "cifs_servers"):
        cifs_server_controller.cifs_servers.clear()
    if hasattr(nfs_share_controller, "nfs_shares"):
        nfs_share_controller.nfs_shares.clear()
    if hasattr(quota_controller, "quota_configs"):
        quota_controller.quota_configs.clear()
    if hasattr(quota_controller, "tree_quotas"):
        quota_controller.tree_quotas.clear()
    if hasattr(quota_controller, "user_quotas"):
        quota_controller.user_quotas.clear()

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
    """Create headers with authentication for test requests.

    This follows the Dell Unity API behavior:
    1. Uses HTTP Basic auth
    2. Requires X-EMC-REST-CLIENT header
    3. For GET requests, returns EMC-CSRF-TOKEN in response header
    4. For POST/PATCH/DELETE requests, requires EMC-CSRF-TOKEN header

    Returns:
        tuple: (headers_with_csrf, headers_without_csrf)
        - headers_with_csrf: Headers for POST/PATCH/DELETE requests
        - headers_without_csrf: Headers for GET requests
    """
    # Create Basic Auth header with correct password
    credentials = base64.b64encode(b"admin:Password123!").decode("utf-8")

    # Base headers used for all requests
    base_headers = {
        "Authorization": f"Basic {credentials}",
        "X-EMC-REST-CLIENT": "true",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Make a GET request to get CSRF token
    response = test_client.get("/api/types/user/instances", headers=base_headers)
    csrf_token = response.headers.get("EMC-CSRF-TOKEN")

    # Create headers with CSRF token for mutating requests
    headers_with_csrf = base_headers.copy()
    headers_with_csrf["EMC-CSRF-TOKEN"] = csrf_token

    return headers_with_csrf, base_headers
