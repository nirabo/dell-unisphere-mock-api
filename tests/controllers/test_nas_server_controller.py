from unittest.mock import Mock

import pytest
from fastapi import HTTPException, Request

from dell_unisphere_mock_api.controllers.nas_server_controller import NasServerController
from dell_unisphere_mock_api.schemas.nas_server import NasServerCreate, NasServerUpdate


@pytest.fixture
def nas_server_controller():
    return NasServerController()


@pytest.fixture
def mock_request():
    request = Mock(spec=Request)
    request.base_url = "http://test"
    return request


@pytest.fixture
def sample_nas_server_data():
    return {
        "name": "test_nas_server",
        "description": "Test NAS server",
        "homeSP": "spa",
        "pool": "pool_1",
        "currentUnixDirectory": "NONE",
        "isMultiProtocolEnabled": False,
        "isWindowsToUnixUsernameMappingEnabled": False,
        "defaultUnixUser": None,
        "defaultWindowsUser": None,
        "fileInterfaces": [],
    }


@pytest.mark.asyncio
async def test_create_nas_server(nas_server_controller, mock_request, sample_nas_server_data):
    nas_server_data = NasServerCreate(**sample_nas_server_data)
    response = await nas_server_controller.create_nas_server(mock_request, nas_server_data)
    response_dict = response.model_dump()

    assert response_dict["base"] == "http://test/api/types/nasServer/instances"
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["name"] == sample_nas_server_data["name"]
    assert content["description"] == sample_nas_server_data["description"]


@pytest.mark.asyncio
async def test_get_nas_server(nas_server_controller, mock_request, sample_nas_server_data):
    # First create a NAS server
    nas_server_data = NasServerCreate(**sample_nas_server_data)
    created = await nas_server_controller.create_nas_server(mock_request, nas_server_data)
    created_dict = created.model_dump()
    nas_server_id = created_dict["entries"][0]["content"]["id"]

    # Then get it
    response = await nas_server_controller.get_nas_server(mock_request, nas_server_id)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["name"] == sample_nas_server_data["name"]
    assert content["description"] == sample_nas_server_data["description"]


@pytest.mark.asyncio
async def test_list_nas_servers(nas_server_controller, mock_request, sample_nas_server_data):
    # Create a NAS server first
    nas_server_data = NasServerCreate(**sample_nas_server_data)
    created_response = await nas_server_controller.create_nas_server(mock_request, nas_server_data)
    created_dict = created_response.model_dump()
    created_id = created_dict["entries"][0]["content"]["id"]
    created_name = created_dict["entries"][0]["content"]["name"]

    # List all NAS servers
    response = await nas_server_controller.list_nas_servers(mock_request)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) > 0
    content = response_dict["entries"][0]["content"]
    assert content["id"] == created_id
    assert content["name"] == created_name


@pytest.mark.asyncio
async def test_update_nas_server(nas_server_controller, mock_request, sample_nas_server_data):
    # First create a NAS server
    nas_server_data = NasServerCreate(**sample_nas_server_data)
    created = await nas_server_controller.create_nas_server(mock_request, nas_server_data)
    created_dict = created.model_dump()
    nas_server_id = created_dict["entries"][0]["content"]["id"]

    # Update it
    update_data = NasServerUpdate(description="Updated description")
    response = await nas_server_controller.update_nas_server(mock_request, nas_server_id, update_data)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_nas_server(nas_server_controller, mock_request, sample_nas_server_data):
    # First create a NAS server
    nas_server_data = NasServerCreate(**sample_nas_server_data)
    created = await nas_server_controller.create_nas_server(mock_request, nas_server_data)
    created_dict = created.model_dump()
    nas_server_id = created_dict["entries"][0]["content"]["id"]

    # Delete it
    response = await nas_server_controller.delete_nas_server(mock_request, nas_server_id)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 0

    # Verify it's deleted
    with pytest.raises(HTTPException) as exc_info:
        await nas_server_controller.get_nas_server(mock_request, nas_server_id)
    assert exc_info.value.status_code == 404
