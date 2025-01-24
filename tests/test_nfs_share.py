"""Tests for NFS Share functionality."""

import pytest
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.controllers.nfs_share_controller import NFSShareController
from dell_unisphere_mock_api.models.nfs_share import NFSShareCreate, NFSShareUpdate


def test_nfs_share_controller_create():
    """Test creating an NFS share."""
    controller = NFSShareController()
    share_data = NFSShareCreate(
        name="TestShare", filesystem_id="fs_1", path="/exports/test", description="Test NFS share"
    )

    share = controller.create_nfs_share(share_data)
    assert share.name == "TestShare"
    assert share.filesystem_id == "fs_1"
    assert share.path == "/exports/test"
    assert share.description == "Test NFS share"
    assert share.state == "READY"


def test_nfs_share_controller_get():
    """Test retrieving an NFS share."""
    controller = NFSShareController()
    share_data = NFSShareCreate(name="TestShare", filesystem_id="fs_1", path="/exports/test")

    created_share = controller.create_nfs_share(share_data)
    retrieved_share = controller.get_nfs_share(created_share.id)

    assert retrieved_share is not None
    assert retrieved_share.id == created_share.id
    assert retrieved_share.name == "TestShare"


def test_nfs_share_controller_update():
    """Test updating an NFS share."""
    controller = NFSShareController()
    share_data = NFSShareCreate(name="TestShare", filesystem_id="fs_1", path="/exports/test")

    created_share = controller.create_nfs_share(share_data)
    update_data = NFSShareUpdate(description="Updated description", is_read_only=True)
    updated_share = controller.update_nfs_share(created_share.id, update_data)

    assert updated_share is not None
    assert updated_share.description == "Updated description"
    assert updated_share.is_read_only is True


def test_nfs_share_controller_delete():
    """Test deleting an NFS share."""
    controller = NFSShareController()
    share_data = NFSShareCreate(name="TestShare", filesystem_id="fs_1", path="/exports/test")

    created_share = controller.create_nfs_share(share_data)
    assert controller.delete_nfs_share(created_share.id) is True
    assert controller.get_nfs_share(created_share.id) is None


def test_nfs_share_api_endpoints(test_client: TestClient, auth_headers):
    """Test NFS share API endpoints."""
    headers, _ = auth_headers

    # Create
    response = test_client.post(
        "/api/types/nfsShare/instances",
        json={
            "name": "TestShare",
            "filesystem_id": "fs_1",
            "path": "/shared/projects",
            "default_access": "READ_ONLY",
            "root_squash_enabled": True,
            "anonymous_uid": 65534,
            "anonymous_gid": 65534,
            "is_read_only": True,
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    share_id = data["entries"][0]["content"]["id"]

    # Get
    response = test_client.get(f"/api/types/nfsShare/instances/{share_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["entries"][0]["content"]["name"] == "TestShare"

    # Update
    response = test_client.patch(
        f"/api/types/nfsShare/instances/{share_id}",
        json={"description": "Updated description", "default_access": "READ_WRITE"},
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()["entries"][0]["content"]
    assert content["description"] == "Updated description"
    assert content["default_access"] == "READ_WRITE"

    # Delete
    response = test_client.delete(f"/api/types/nfsShare/instances/{share_id}", headers=headers)
    assert response.status_code == 200

    # Verify deletion
    response = test_client.get(f"/api/types/nfsShare/instances/{share_id}", headers=headers)
    assert response.status_code == 404
