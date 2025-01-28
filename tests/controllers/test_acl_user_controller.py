import pytest
from fastapi import HTTPException, Request

from dell_unisphere_mock_api.controllers.acl_user_controller import ACLUserController
from dell_unisphere_mock_api.models.acl_user import ACLUserCreate, ACLUserUpdate


@pytest.fixture
def acl_user_controller():
    return ACLUserController()


@pytest.fixture
def mock_request():
    return Request({"type": "http", "method": "GET", "headers": [], "path": "/"})


@pytest.fixture
def sample_acl_user_data():
    return {
        "user_name": "testuser",
        "domain_name": "test.local",
        "sid": "S-1-5-21-123456789-0123456789-012345678-1234",
        "is_domain_user": True,
        "is_local_user": False,
    }


def test_create_acl_user(acl_user_controller, mock_request, sample_acl_user_data):
    user_data = ACLUserCreate(**sample_acl_user_data)
    response = acl_user_controller.create_user(mock_request, user_data)
    assert response.entries[0].content.user_name == sample_acl_user_data["user_name"]
    assert response.entries[0].content.domain_name == sample_acl_user_data["domain_name"]
    assert response.entries[0].content.sid == sample_acl_user_data["sid"]
    assert response.entries[0].content.id is not None


def test_get_acl_user(acl_user_controller, mock_request, sample_acl_user_data):
    # First create a user
    user_data = ACLUserCreate(**sample_acl_user_data)
    created = acl_user_controller.create_user(mock_request, user_data)
    user_id = created.entries[0].content.id

    # Then get it
    response = acl_user_controller.get_user(mock_request, user_id)
    assert response.entries[0].content.user_name == sample_acl_user_data["user_name"]
    assert response.entries[0].content.id == user_id


def test_get_nonexistent_user(acl_user_controller, mock_request):
    with pytest.raises(HTTPException) as exc_info:
        acl_user_controller.get_user(mock_request, "nonexistent-id")
    assert exc_info.value.status_code == 404


def test_list_acl_users(acl_user_controller, mock_request, sample_acl_user_data):
    # Create a user first
    user_data = ACLUserCreate(**sample_acl_user_data)
    acl_user_controller.create_user(mock_request, user_data)

    # List all users
    response = acl_user_controller.list_users(mock_request)
    assert len(response.entries) == 1
    assert response.entries[0].content.user_name == sample_acl_user_data["user_name"]


def test_update_acl_user(acl_user_controller, mock_request, sample_acl_user_data):
    # First create a user
    user_data = ACLUserCreate(**sample_acl_user_data)
    created = acl_user_controller.create_user(mock_request, user_data)
    user_id = created.entries[0].content.id

    # Update it
    update_data = ACLUserUpdate(user_name="updated_user")
    response = acl_user_controller.update_user(mock_request, user_id, update_data)
    assert response.entries[0].content.user_name == "updated_user"
    assert response.entries[0].content.domain_name == sample_acl_user_data["domain_name"]


def test_update_nonexistent_user(acl_user_controller, mock_request):
    update_data = ACLUserUpdate(user_name="updated_user")
    with pytest.raises(HTTPException) as exc_info:
        acl_user_controller.update_user(mock_request, "nonexistent-id", update_data)
    assert exc_info.value.status_code == 404


def test_delete_acl_user(acl_user_controller, mock_request, sample_acl_user_data):
    # First create a user
    user_data = ACLUserCreate(**sample_acl_user_data)
    created = acl_user_controller.create_user(mock_request, user_data)
    user_id = created.entries[0].content.id

    # Delete it
    response = acl_user_controller.delete_user(mock_request, user_id)
    assert len(response.entries) == 0

    # Verify it's gone
    with pytest.raises(HTTPException) as exc_info:
        acl_user_controller.get_user(mock_request, user_id)
    assert exc_info.value.status_code == 404


def test_delete_nonexistent_user(acl_user_controller, mock_request):
    with pytest.raises(HTTPException) as exc_info:
        acl_user_controller.delete_user(mock_request, "nonexistent-id")
    assert exc_info.value.status_code == 404


def test_lookup_sid_by_domain_user(acl_user_controller, mock_request, sample_acl_user_data):
    # First create a user
    user_data = ACLUserCreate(**sample_acl_user_data)
    acl_user_controller.create_user(mock_request, user_data)

    # Look up the user
    response = acl_user_controller.lookup_sid_by_domain_user(
        mock_request, sample_acl_user_data["domain_name"], sample_acl_user_data["user_name"]
    )
    assert response.entries[0].content.user_name == sample_acl_user_data["user_name"]
    assert response.entries[0].content.domain_name == sample_acl_user_data["domain_name"]
    assert response.entries[0].content.sid == sample_acl_user_data["sid"]


def test_lookup_nonexistent_domain_user(acl_user_controller, mock_request):
    with pytest.raises(HTTPException) as exc_info:
        acl_user_controller.lookup_sid_by_domain_user(mock_request, "nonexistent.domain", "nonexistent_user")
    assert exc_info.value.status_code == 404
