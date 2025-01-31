"""Tests for CIFS Server functionality."""

from typing import Dict, Optional

import pytest
from fastapi.testclient import TestClient
from starlette.datastructures import URL

from dell_unisphere_mock_api.controllers.cifs_server_controller import CIFSServerController
from dell_unisphere_mock_api.models.cifs_server import CIFSServer, CIFSServerCreate, CIFSServerUpdate


class MockRequest:
    """Mock request for testing."""

    def __init__(self):
        self.base_url = URL("http://testserver")
        self.url = URL("/api/types/cifsServer/instances")
        self.method = "GET"
        self.headers = {"Content-Type": "application/json"}
        self.query_params: Dict[str, str] = {}
        self.path_params: Dict[str, str] = {}
        self.cookies: Dict[str, str] = {}
        self.client = None
        self.state = {}


@pytest.fixture
def mock_request():
    """Create a mock request for testing."""
    return MockRequest()


@pytest.mark.asyncio
async def test_cifs_server_controller_create(mock_request):
    """Test creating a CIFS server."""
    controller = CIFSServerController()
    server_data = CIFSServerCreate(
        name="TestServer",
        nas_server_id="nas_1",
        netbios_name="TESTSERVER",
        domain_name="WORKGROUP",
        workgroup="WORKGROUP",
    )

    response = await controller.create_cifs_server(mock_request, server_data)
    content = response.entries[0].content
    assert content.name == "TestServer"
    assert content.nas_server_id == "nas_1"
    assert content.netbios_name == "TESTSERVER"


@pytest.mark.asyncio
async def test_cifs_server_controller_get(mock_request):
    """Test retrieving a CIFS server."""
    controller = CIFSServerController()
    server_data = CIFSServerCreate(
        name="TestServer",
        nas_server_id="nas_1",
        netbios_name="TESTSERVER",
        domain_name="WORKGROUP",
        workgroup="WORKGROUP",
    )

    created_response = await controller.create_cifs_server(mock_request, server_data)
    created_server = created_response.entries[0].content
    retrieved_response = await controller.get_cifs_server(mock_request, created_server.id)
    retrieved_server = retrieved_response.entries[0].content

    assert retrieved_server.name == "TestServer"
    assert retrieved_server.nas_server_id == "nas_1"
    assert retrieved_server.netbios_name == "TESTSERVER"


@pytest.mark.asyncio
async def test_cifs_server_controller_update(mock_request):
    """Test updating a CIFS server."""
    controller = CIFSServerController()
    server_data = CIFSServerCreate(
        name="TestServer",
        nas_server_id="nas_1",
        netbios_name="TESTSERVER",
        domain_name="WORKGROUP",
        workgroup="WORKGROUP",
    )

    created_response = await controller.create_cifs_server(mock_request, server_data)
    created_server = created_response.entries[0].content

    update_data = CIFSServerUpdate(name="UpdatedServer")
    updated_response = await controller.update_cifs_server(mock_request, created_server.id, update_data)
    updated_server = updated_response.entries[0].content

    assert updated_server.name == "UpdatedServer"
    assert updated_server.nas_server_id == "nas_1"
    assert updated_server.netbios_name == "TESTSERVER"


def test_cifs_server_api_endpoints(test_client: TestClient, auth_headers):
    """Test CIFS server API endpoints."""
    headers, _ = auth_headers

    # First make a GET request to get the CSRF token
    response = test_client.get("/api/types/cifsServer/instances", headers=headers)
    assert response.status_code == 200
    csrf_token = response.headers.get("EMC-CSRF-TOKEN")
    assert csrf_token is not None

    # Add CSRF token to headers for mutating requests
    headers_with_csrf = {**headers, "EMC-CSRF-TOKEN": csrf_token}

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
        headers=headers_with_csrf,
    )
    assert response.status_code == 200
    data = response.json()
    assert "entries" in data
    assert len(data["entries"]) == 1
    server_id = data["entries"][0]["content"]["id"]

    # Get
    response = test_client.get(f"/api/types/cifsServer/instances/{server_id}", headers=headers)
    assert response.status_code == 200
    content = response.json()["entries"][0]["content"]
    assert content["name"] == "TestServer"

    # Update
    response = test_client.patch(
        f"/api/types/cifsServer/instances/{server_id}",
        json={"name": "UpdatedServer"},
        headers=headers_with_csrf,
    )
    assert response.status_code == 200
    content = response.json()["entries"][0]["content"]
    assert content["name"] == "UpdatedServer"

    # Delete
    response = test_client.delete(f"/api/types/cifsServer/instances/{server_id}", headers=headers_with_csrf)
    assert response.status_code == 200

    # Verify deletion
    response = test_client.get(f"/api/types/cifsServer/instances/{server_id}", headers=headers)
    assert response.status_code == 404
