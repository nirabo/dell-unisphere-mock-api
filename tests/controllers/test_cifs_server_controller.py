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
    return request


@pytest.fixture
def sample_cifs_server_data():
    return {
        "name": "test_cifs_server",
        "description": "Test CIFS server",
        "nas_server_id": "nas_1",
        "domain": "test.local",
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


@pytest.mark.asyncio
async def test_update_cifs_server(cifs_server_controller, mock_request, sample_cifs_server_data):
    # First create a CIFS server
    cifs_server_data = CIFSServerCreate(**sample_cifs_server_data)
    created = await cifs_server_controller.create_cifs_server(mock_request, cifs_server_data)
    created_dict = created.model_dump()
    cifs_server_id = created_dict["entries"][0]["content"]["id"]

    # Update it
    update_data = CIFSServerUpdate(description="Updated description")
    response = await cifs_server_controller.update_cifs_server(mock_request, cifs_server_id, update_data)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["description"] == "Updated description"


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
