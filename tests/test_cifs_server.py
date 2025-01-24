"""Tests for CIFS Server functionality."""

import pytest
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.controllers.cifs_server_controller import CIFSServerController
from dell_unisphere_mock_api.models.cifs_server import CIFSServerCreate, CIFSServerUpdate


def test_cifs_server_controller_create():
    """Test creating a CIFS server."""
    controller = CIFSServerController()
    server_data = CIFSServerCreate(
        name="TestServer",
        nas_server_id="nas_1",
        netbios_name="TESTSERVER",
        domain_name="WORKGROUP",
        workgroup="WORKGROUP",
    )

    server = controller.create_cifs_server(server_data)
    assert server.name == "TestServer"
    assert server.nas_server_id == "nas_1"
    assert server.netbios_name == "TESTSERVER"
    assert server.domain_name == "WORKGROUP"
    assert server.workgroup == "WORKGROUP"
    assert server.state == "READY"


def test_cifs_server_controller_get():
    """Test retrieving a CIFS server."""
    controller = CIFSServerController()
    server_data = CIFSServerCreate(
        name="TestServer",
        nas_server_id="nas_1",
        netbios_name="TESTSERVER",
        domain_name="WORKGROUP",
        workgroup="WORKGROUP",
    )

    created_server = controller.create_cifs_server(server_data)
    retrieved_server = controller.get_cifs_server(created_server.id)

    assert retrieved_server is not None
    assert retrieved_server.id == created_server.id
    assert retrieved_server.name == "TestServer"


def test_cifs_server_controller_update():
    """Test updating a CIFS server."""
    controller = CIFSServerController()
    server_data = CIFSServerCreate(
        name="TestServer",
        nas_server_id="nas_1",
        netbios_name="TESTSERVER",
        domain_name="WORKGROUP",
        workgroup="WORKGROUP",
    )

    created_server = controller.create_cifs_server(server_data)
    update_data = CIFSServerUpdate(description="Updated description", workgroup="NEWWORKGROUP")
    updated_server = controller.update_cifs_server(created_server.id, update_data)

    assert updated_server is not None
    assert updated_server.description == "Updated description"
    assert updated_server.workgroup == "NEWWORKGROUP"


def test_cifs_server_controller_delete():
    """Test deleting a CIFS server."""
    controller = CIFSServerController()
    server_data = CIFSServerCreate(
        name="TestServer",
        nas_server_id="nas_1",
        netbios_name="TESTSERVER",
        domain_name="WORKGROUP",
        workgroup="WORKGROUP",
    )

    created_server = controller.create_cifs_server(server_data)
    assert controller.delete_cifs_server(created_server.id) is True
    assert controller.get_cifs_server(created_server.id) is None


def test_cifs_server_api_endpoints(test_client: TestClient, auth_headers):
    """Test CIFS server API endpoints."""
    headers, _ = auth_headers

    # Create
    response = test_client.post(
        "/api/types/cifsServer/instances",
        json={
            "name": "TestServer",
            "nas_server_id": "nas_1",
            "netbios_name": "TESTSERVER",
            "domain_name": "WORKGROUP",
            "workgroup": "WORKGROUP",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    server_id = data["entries"][0]["content"]["id"]

    # Get
    response = test_client.get(f"/api/types/cifsServer/instances/{server_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["entries"][0]["content"]["name"] == "TestServer"

    # Update
    response = test_client.patch(
        f"/api/types/cifsServer/instances/{server_id}",
        json={"description": "Updated description", "workgroup": "NEWWORKGROUP"},
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()["entries"][0]["content"]
    assert content["description"] == "Updated description"
    assert content["workgroup"] == "NEWWORKGROUP"

    # Delete
    response = test_client.delete(f"/api/types/cifsServer/instances/{server_id}", headers=headers)
    assert response.status_code == 200

    # Verify deletion
    response = test_client.get(f"/api/types/cifsServer/instances/{server_id}", headers=headers)
    assert response.status_code == 404
