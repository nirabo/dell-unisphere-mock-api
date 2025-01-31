from unittest.mock import Mock

import pytest
from fastapi import HTTPException, Request

from dell_unisphere_mock_api.controllers.cifs_server_controller import CIFSServerController
from dell_unisphere_mock_api.models.cifs_server import CIFSServerCreate, CIFSServerUpdate


@pytest.fixture
def cifs_server_controller():
    return CIFSServerController()


@pytest.fixture
def mock_request():
    request = Mock(spec=Request)
    request.base_url = "http://test"

    # Mock the URL object with path property
    mock_url = Mock()
    mock_url.path = "/api/types/cifsServer/instances"
    request.url = mock_url

    return request


@pytest.fixture
def sample_cifs_server_data():
    return {
        "name": "test_cifs_server",
        "description": "Test CIFS server",
        "nas_server_id": "nas_1",
        "domain_name": "test.local",
        "netbios_name": "TESTCIFS",
        "workgroup": "WORKGROUP",
        "is_standalone": True,
    }


@pytest.mark.asyncio
async def test_create_cifs_server(cifs_server_controller, mock_request, sample_cifs_server_data):
    cifs_server_data = CIFSServerCreate(**sample_cifs_server_data)
    response = await cifs_server_controller.create_cifs_server(mock_request, cifs_server_data)
    response_dict = response.model_dump()

    assert response_dict["base"] == "http://test/api/types/cifsServer/instances"
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["name"] == sample_cifs_server_data["name"]
    assert content["description"] == sample_cifs_server_data["description"]
    assert content["nas_server_id"] == sample_cifs_server_data["nas_server_id"]


@pytest.mark.asyncio
async def test_get_cifs_server(cifs_server_controller, mock_request, sample_cifs_server_data):
    # First create a CIFS server
    cifs_server_data = CIFSServerCreate(**sample_cifs_server_data)
    created = await cifs_server_controller.create_cifs_server(mock_request, cifs_server_data)
    created_dict = created.model_dump()
    cifs_server_id = created_dict["entries"][0]["content"]["id"]

    # Then get it
    response = await cifs_server_controller.get_cifs_server(mock_request, cifs_server_id)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["name"] == sample_cifs_server_data["name"]
    assert content["description"] == sample_cifs_server_data["description"]
    assert content["nas_server_id"] == sample_cifs_server_data["nas_server_id"]


@pytest.mark.asyncio
async def test_list_cifs_servers(cifs_server_controller, mock_request, sample_cifs_server_data):
    # Create a CIFS server first
    cifs_server_data = CIFSServerCreate(**sample_cifs_server_data)
    created_response = await cifs_server_controller.create_cifs_server(mock_request, cifs_server_data)
    created_dict = created_response.model_dump()
    created_id = created_dict["entries"][0]["content"]["id"]
    created_name = created_dict["entries"][0]["content"]["name"]

    # List all CIFS servers
    response = await cifs_server_controller.list_cifs_servers(mock_request)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) > 0
    content = response_dict["entries"][0]["content"]
    assert content["id"] == created_id
    assert content["name"] == created_name
    assert content["nas_server_id"] == sample_cifs_server_data["nas_server_id"]


@pytest.mark.asyncio
async def test_update_cifs_server(cifs_server_controller, mock_request, sample_cifs_server_data):
    # First create a CIFS server
    cifs_server_data = CIFSServerCreate(**sample_cifs_server_data)
    created = await cifs_server_controller.create_cifs_server(mock_request, cifs_server_data)
    created_dict = created.model_dump()
    cifs_server_id = created_dict["entries"][0]["content"]["id"]

    # Update it
    update_data = CIFSServerUpdate(
        description="Updated description", domain_name="updated.domain", workgroup="NEWGROUP"
    )
    response = await cifs_server_controller.update_cifs_server(mock_request, cifs_server_id, update_data)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["description"] == "Updated description"
    assert content["domain_name"] == "updated.domain"
    assert content["workgroup"] == "NEWGROUP"
    assert content["name"] == sample_cifs_server_data["name"]  # Name should be unchanged
    assert content["nas_server_id"] == sample_cifs_server_data["nas_server_id"]


@pytest.mark.asyncio
async def test_delete_cifs_server(cifs_server_controller, mock_request, sample_cifs_server_data):
    # First create a CIFS server
    cifs_server_data = CIFSServerCreate(**sample_cifs_server_data)
    created = await cifs_server_controller.create_cifs_server(mock_request, cifs_server_data)
    created_dict = created.model_dump()
    cifs_server_id = created_dict["entries"][0]["content"]["id"]

    # Delete it
    response = await cifs_server_controller.delete_cifs_server(mock_request, cifs_server_id)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 0

    # Verify it's deleted
    with pytest.raises(HTTPException) as exc_info:
        await cifs_server_controller.get_cifs_server(mock_request, cifs_server_id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_cifs_server(cifs_server_controller, mock_request):
    with pytest.raises(HTTPException) as exc_info:
        await cifs_server_controller.get_cifs_server(mock_request, "nonexistent-id")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_nonexistent_cifs_server(cifs_server_controller, mock_request):
    update_data = CIFSServerUpdate(name="updated_server")
    with pytest.raises(HTTPException) as exc_info:
        await cifs_server_controller.update_cifs_server(mock_request, "nonexistent-id", update_data)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_cifs_server(cifs_server_controller, mock_request):
    with pytest.raises(HTTPException) as exc_info:
        await cifs_server_controller.delete_cifs_server(mock_request, "nonexistent-id")
    assert exc_info.value.status_code == 404
