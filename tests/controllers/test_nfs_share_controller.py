"""Tests for NFS Share Controller."""

import pytest
from fastapi import HTTPException, Request

from dell_unisphere_mock_api.controllers.nfs_share_controller import NFSShareController
from dell_unisphere_mock_api.models.nfs_share import NFSShareCreate, NFSShareUpdate


@pytest.fixture
def nfs_share_controller():
    """Create a new NFS share controller for testing."""
    return NFSShareController()


@pytest.fixture
def mock_request(mocker):
    """Create a mock request object."""
    mock = mocker.Mock()
    mock.base_url = "http://testserver"
    mock.url = mocker.Mock()
    mock.url.path = "/api/types/nfsShare/instances"
    return mock


@pytest.fixture
def sample_nfs_share_data():
    """Create sample NFS share data for testing."""
    return {
        "name": "test_share",
        "filesystem_id": "fs_1",
        "path": "/exports/test",
        "description": "Test NFS share",
        "default_access": "READ_ONLY",
        "root_squash_enabled": True,
        "anonymous_uid": 65534,
        "anonymous_gid": 65534,
        "is_read_only": True,
        "min_security": "SYS",
        "no_access_hosts": [],
        "read_only_hosts": [],
        "read_write_hosts": [],
        "root_access_hosts": [],
    }


@pytest.mark.asyncio
async def test_create_nfs_share(nfs_share_controller, mock_request, sample_nfs_share_data):
    """Test creating an NFS share."""
    share_data = NFSShareCreate(**sample_nfs_share_data)
    response = nfs_share_controller.create_nfs_share(mock_request, share_data)
    response_dict = response.model_dump()

    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["name"] == sample_nfs_share_data["name"]
    assert content["filesystem_id"] == sample_nfs_share_data["filesystem_id"]
    assert content["path"] == sample_nfs_share_data["path"]
    assert content["description"] == sample_nfs_share_data["description"]
    assert content["state"] == "READY"


@pytest.mark.asyncio
async def test_get_nfs_share(nfs_share_controller, mock_request, sample_nfs_share_data):
    """Test retrieving an NFS share."""
    # Create a share first
    share_data = NFSShareCreate(**sample_nfs_share_data)
    created_response = nfs_share_controller.create_nfs_share(mock_request, share_data)
    created_dict = created_response.model_dump()
    created_id = created_dict["entries"][0]["content"]["id"]

    # Get the share
    response = nfs_share_controller.get_nfs_share(mock_request, created_id)
    response_dict = response.model_dump()

    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["id"] == created_id
    assert content["name"] == sample_nfs_share_data["name"]


@pytest.mark.asyncio
async def test_list_nfs_shares(nfs_share_controller, mock_request, sample_nfs_share_data):
    """Test listing NFS shares."""
    # Create a share first
    share_data = NFSShareCreate(**sample_nfs_share_data)
    created_response = nfs_share_controller.create_nfs_share(mock_request, share_data)
    created_dict = created_response.model_dump()
    created_id = created_dict["entries"][0]["content"]["id"]
    created_name = created_dict["entries"][0]["content"]["name"]

    # List all shares
    response = nfs_share_controller.list_nfs_shares(mock_request)
    response_dict = response.model_dump()

    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]  # Each entry has its own content
    assert content["id"] == created_id
    assert content["name"] == created_name


@pytest.mark.asyncio
async def test_update_nfs_share(nfs_share_controller, mock_request, sample_nfs_share_data):
    """Test updating an NFS share."""
    # Create a share first
    share_data = NFSShareCreate(**sample_nfs_share_data)
    created_response = nfs_share_controller.create_nfs_share(mock_request, share_data)
    created_dict = created_response.model_dump()
    created_id = created_dict["entries"][0]["content"]["id"]

    # Update the share
    update_data = NFSShareUpdate(description="Updated description", is_read_only=False)
    response = nfs_share_controller.update_nfs_share(mock_request, created_id, update_data)
    response_dict = response.model_dump()

    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["id"] == created_id
    assert content["description"] == "Updated description"
    assert content["is_read_only"] is False
    # Original fields should remain unchanged
    assert content["name"] == sample_nfs_share_data["name"]
    assert content["filesystem_id"] == sample_nfs_share_data["filesystem_id"]


@pytest.mark.asyncio
async def test_delete_nfs_share(nfs_share_controller, mock_request, sample_nfs_share_data):
    """Test deleting an NFS share."""
    # Create a share first
    share_data = NFSShareCreate(**sample_nfs_share_data)
    created_response = nfs_share_controller.create_nfs_share(mock_request, share_data)
    created_dict = created_response.model_dump()
    created_id = created_dict["entries"][0]["content"]["id"]

    # Delete the share
    response = nfs_share_controller.delete_nfs_share(mock_request, created_id)
    assert response is True

    # Verify it's deleted by trying to get it
    with pytest.raises(HTTPException) as exc_info:
        nfs_share_controller.get_nfs_share(mock_request, created_id)
    assert exc_info.value.status_code == 404
