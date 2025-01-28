"""Tests for NFS Share functionality."""

import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.controllers.nfs_share_controller import NFSShareController
from dell_unisphere_mock_api.models.nfs_share import NFSShareCreate, NFSShareUpdate


class MockRequest:
    """Mock Request object for testing."""

    def __init__(self):
        self.base_url = "http://testserver"
        self.url = type("MockURL", (), {"path": "/api/types/nfsShare/instances"})()


def test_nfs_share_controller_create():
    """Test creating an NFS share."""
    controller = NFSShareController()
    request = MockRequest()
    share_data = NFSShareCreate(
        name="TestShare",
        filesystem_id="fs_1",
        path="/exports/test",
        description="Test NFS share",
        default_access="NO_ACCESS",
        root_squash_enabled=True,
        anonymous_uid=65534,
        anonymous_gid=65534,
        is_read_only=False,
        min_security="SYS",
        no_access_hosts=[],
        read_only_hosts=[],
        read_write_hosts=[],
        root_access_hosts=[],
    )

    response = controller.create_nfs_share(request, share_data)
    assert response.entries[0].content.name == "TestShare"


def test_nfs_share_controller_get():
    """Test retrieving an NFS share."""
    controller = NFSShareController()
    request = MockRequest()
    share_data = NFSShareCreate(
        name="TestShare",
        filesystem_id="fs_1",
        path="/exports/test",
        description="Test NFS share",
        default_access="NO_ACCESS",
        root_squash_enabled=True,
        anonymous_uid=65534,
        anonymous_gid=65534,
        is_read_only=False,
        min_security="SYS",
        no_access_hosts=[],
        read_only_hosts=[],
        read_write_hosts=[],
        root_access_hosts=[],
    )

    created_share = controller.create_nfs_share(request, share_data)
    share_id = created_share.entries[0].content.id
    retrieved_share = controller.get_nfs_share(request, share_id)
    assert retrieved_share.entries[0].content.name == "TestShare"


def test_nfs_share_controller_update():
    """Test updating an NFS share."""
    controller = NFSShareController()
    request = MockRequest()
    share_data = NFSShareCreate(
        name="TestShare",
        filesystem_id="fs_1",
        path="/exports/test",
        description="Test NFS share",
        default_access="NO_ACCESS",
        root_squash_enabled=True,
        anonymous_uid=65534,
        anonymous_gid=65534,
        is_read_only=False,
        min_security="SYS",
        no_access_hosts=[],
        read_only_hosts=[],
        read_write_hosts=[],
        root_access_hosts=[],
    )

    created_share = controller.create_nfs_share(request, share_data)
    share_id = created_share.entries[0].content.id
    update_data = NFSShareUpdate(description="Updated description", is_read_only=True)
    updated_share = controller.update_nfs_share(request, share_id, update_data)
    assert updated_share.entries[0].content.description == "Updated description"
    assert updated_share.entries[0].content.is_read_only is True


def test_nfs_share_controller_delete():
    """Test deleting an NFS share."""
    controller = NFSShareController()
    request = MockRequest()
    share_data = NFSShareCreate(
        name="TestShare",
        filesystem_id="fs_1",
        path="/exports/test",
        description="Test NFS share",
        default_access="NO_ACCESS",
        root_squash_enabled=True,
        anonymous_uid=65534,
        anonymous_gid=65534,
        is_read_only=False,
        min_security="SYS",
        no_access_hosts=[],
        read_only_hosts=[],
        read_write_hosts=[],
        root_access_hosts=[],
    )

    created_share = controller.create_nfs_share(request, share_data)
    share_id = created_share.entries[0].content.id
    assert controller.delete_nfs_share(request, share_id) is True


def test_nfs_share_api_endpoints(test_client: TestClient, auth_headers):
    """Test NFS share API endpoints."""
    headers_with_csrf, headers_without_csrf = auth_headers

    # Create
    response = test_client.post(
        "/api/types/nfsShare/instances",
        json={
            "name": "TestShare",
            "filesystem_id": "fs_1",
            "path": "/exports/test",
            "description": "Test NFS share",
            "default_access": "NO_ACCESS",
            "root_squash_enabled": True,
            "anonymous_uid": 65534,
            "anonymous_gid": 65534,
            "is_read_only": False,
            "min_security": "SYS",
            "no_access_hosts": [],
            "read_only_hosts": [],
            "read_write_hosts": [],
            "root_access_hosts": [],
        },
        headers=headers_with_csrf,
    )
    assert response.status_code == 200
    data = response.json()
    share_id = data["entries"][0]["content"]["id"]

    # Get
    response = test_client.get(f"/api/types/nfsShare/instances/{share_id}", headers=headers_without_csrf)
    assert response.status_code == 200
    data = response.json()
    assert data["entries"][0]["content"]["name"] == "TestShare"

    # Update
    response = test_client.put(
        f"/api/types/nfsShare/instances/{share_id}",
        json={"description": "Updated description", "is_read_only": True},
        headers=headers_with_csrf,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["entries"][0]["content"]["description"] == "Updated description"
    assert data["entries"][0]["content"]["is_read_only"] is True

    # Delete
    response = test_client.delete(f"/api/types/nfsShare/instances/{share_id}", headers=headers_with_csrf)
    assert response.status_code == 200
