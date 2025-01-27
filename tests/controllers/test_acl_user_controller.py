from unittest.mock import Mock

import pytest
from fastapi import HTTPException, Request

from dell_unisphere_mock_api.controllers.acl_user_controller import ACLUserController
from dell_unisphere_mock_api.models.acl_user import ACLUserCreate, ACLUserUpdate


@pytest.fixture
def acl_user_controller():
    return ACLUserController()


@pytest.fixture
def mock_request():
    request = Mock(spec=Request)
    request.base_url = "http://test"
    return request


@pytest.fixture
def sample_acl_user_data():
    return {
        "user_name": "test_user",
        "domain_name": "test.local",
        "sid": "S-1-5-21-123456789-0123456789-012345678-1234",
        "is_domain_user": True,
        "is_local_user": False,
    }


@pytest.mark.asyncio
async def test_create_acl_user(acl_user_controller, mock_request, sample_acl_user_data):
    user_data = ACLUserCreate(**sample_acl_user_data)
    response = await acl_user_controller.create_user(mock_request, user_data)
    response_dict = response.model_dump()

    assert response_dict["base"] == "http://test/api/types/aclUser/instances"
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["user_name"] == sample_acl_user_data["user_name"]
    assert content["domain_name"] == sample_acl_user_data["domain_name"]
    assert content["sid"] == sample_acl_user_data["sid"]


@pytest.mark.asyncio
async def test_get_acl_user(acl_user_controller, mock_request, sample_acl_user_data):
    # First create a user
    user_data = ACLUserCreate(**sample_acl_user_data)
    created = await acl_user_controller.create_user(mock_request, user_data)
    created_dict = created.model_dump()
    user_id = created_dict["entries"][0]["content"]["id"]

    # Then get it
    response = await acl_user_controller.get_user(mock_request, user_id)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["user_name"] == sample_acl_user_data["user_name"]
    assert content["domain_name"] == sample_acl_user_data["domain_name"]


@pytest.mark.asyncio
async def test_list_acl_users(acl_user_controller, mock_request, sample_acl_user_data):
    # Create a user first
    user_data = ACLUserCreate(**sample_acl_user_data)
    created_response = await acl_user_controller.create_user(mock_request, user_data)
    created_dict = created_response.model_dump()
    created_id = created_dict["entries"][0]["content"]["id"]
    created_name = created_dict["entries"][0]["content"]["user_name"]

    # List all users
    response = await acl_user_controller.list_users(mock_request)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) > 0
    content = response_dict["entries"][0]["content"]
    assert content["id"] == created_id
    assert content["user_name"] == created_name


@pytest.mark.asyncio
async def test_update_acl_user(acl_user_controller, mock_request, sample_acl_user_data):
    # First create a user
    user_data = ACLUserCreate(**sample_acl_user_data)
    created = await acl_user_controller.create_user(mock_request, user_data)
    created_dict = created.model_dump()
    user_id = created_dict["entries"][0]["content"]["id"]

    # Update it
    update_data = ACLUserUpdate(domain_name="updated.local")
    response = await acl_user_controller.update_user(mock_request, user_id, update_data)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["domain_name"] == "updated.local"


@pytest.mark.asyncio
async def test_delete_acl_user(acl_user_controller, mock_request, sample_acl_user_data):
    # First create a user
    user_data = ACLUserCreate(**sample_acl_user_data)
    created = await acl_user_controller.create_user(mock_request, user_data)
    created_dict = created.model_dump()
    user_id = created_dict["entries"][0]["content"]["id"]

    # Delete it
    response = await acl_user_controller.delete_user(mock_request, user_id)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 0

    # Verify it's deleted
    with pytest.raises(HTTPException) as exc_info:
        await acl_user_controller.get_user(mock_request, user_id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_lookup_sid_by_domain_user(acl_user_controller, mock_request, sample_acl_user_data):
    # First create a user
    user_data = ACLUserCreate(**sample_acl_user_data)
    await acl_user_controller.create_user(mock_request, user_data)

    # Look up by domain and username
    response = await acl_user_controller.lookup_sid_by_domain_user(
        mock_request, sample_acl_user_data["domain_name"], sample_acl_user_data["user_name"]
    )
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["sid"] == sample_acl_user_data["sid"]
    assert content["user_name"] == sample_acl_user_data["user_name"]
    assert content["domain_name"] == sample_acl_user_data["domain_name"]


@pytest.mark.asyncio
async def test_lookup_sid_by_domain_user_not_found(acl_user_controller, mock_request):
    with pytest.raises(HTTPException) as exc_info:
        await acl_user_controller.lookup_sid_by_domain_user(mock_request, "nonexistent.local", "nonexistent")
    assert exc_info.value.status_code == 404
