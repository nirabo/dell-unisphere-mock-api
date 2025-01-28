import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.controllers.acl_user_controller import ACLUserController
from dell_unisphere_mock_api.models.acl_user import ACLUserCreate, ACLUserUpdate


@pytest.fixture
def mock_request():
    """Create a mock request object."""
    scope = {
        "type": "http",
        "headers": [],
        "method": "GET",
        "scheme": "http",
        "server": ("testserver", 80),
        "path": "/api/types/aclUser/instances",
    }
    return Request(scope=scope)


def test_acl_user_controller_create(mock_request):
    """Test creating an ACL user."""
    controller = ACLUserController()
    user_data = ACLUserCreate(
        sid="S-1-5-21-1234567890-1234567890-1234567890-1234",
        domain_name="WORKGROUP",
        user_name="testuser",
    )

    response = controller.create_user(mock_request, user_data)
    content = response.entries[0].content
    assert content.sid == "S-1-5-21-1234567890-1234567890-1234567890-1234"
    assert content.domain_name == "WORKGROUP"
    assert content.user_name == "testuser"


def test_acl_user_controller_get(mock_request):
    """Test retrieving an ACL user."""
    controller = ACLUserController()
    user_data = ACLUserCreate(
        sid="S-1-5-21-1234567890-1234567890-1234567890-1234",
        domain_name="WORKGROUP",
        user_name="testuser",
    )

    created_response = controller.create_user(mock_request, user_data)
    created_user = created_response.entries[0].content
    retrieved_response = controller.get_user(mock_request, created_user.id)
    retrieved_user = retrieved_response.entries[0].content

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.sid == "S-1-5-21-1234567890-1234567890-1234567890-1234"
    assert retrieved_user.domain_name == "WORKGROUP"
    assert retrieved_user.user_name == "testuser"


def test_acl_user_controller_update(mock_request):
    """Test updating an ACL user."""
    controller = ACLUserController()
    user_data = ACLUserCreate(
        sid="S-1-5-21-1234567890-1234567890-1234567890-1234",
        domain_name="WORKGROUP",
        user_name="testuser",
    )

    created_response = controller.create_user(mock_request, user_data)
    created_user = created_response.entries[0].content
    update_data = ACLUserUpdate(user_name="updateduser")
    updated_response = controller.update_user(mock_request, created_user.id, update_data)
    updated_user = updated_response.entries[0].content

    assert updated_user is not None
    assert updated_user.user_name == "updateduser"
    assert updated_user.sid == "S-1-5-21-1234567890-1234567890-1234567890-1234"
    assert updated_user.domain_name == "WORKGROUP"


def test_acl_user_controller_lookup_sid(mock_request):
    """Test looking up a user's SID by domain name and username."""
    controller = ACLUserController()
    user_data = ACLUserCreate(
        sid="S-1-5-21-1234567890-1234567890-1234567890-1234",
        domain_name="WORKGROUP",
        user_name="testuser",
    )

    controller.create_user(mock_request, user_data)
    result = controller.lookup_sid_by_domain_user(mock_request, "WORKGROUP", "testuser")
    user = result.entries[0].content

    assert result is not None
    assert user.sid == "S-1-5-21-1234567890-1234567890-1234567890-1234"
    assert user.domain_name == "WORKGROUP"
    assert user.user_name == "testuser"


def test_acl_user_api_endpoints(test_client: TestClient, auth_headers):
    """Test ACL user API endpoints."""
    headers, _ = auth_headers

    # Create
    response = test_client.post(
        "/api/types/aclUser/instances",
        json={
            "sid": "S-1-5-21-1234567890-1234567890-1234567890-1234",
            "domain_name": "WORKGROUP",
            "user_name": "testuser",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    user_id = data["entries"][0]["content"]["id"]
    assert data["entries"][0]["content"]["user_name"] == "testuser"

    # Get
    response = test_client.get(f"/api/types/aclUser/instances/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["entries"][0]["content"]["user_name"] == "testuser"

    # Update
    response = test_client.patch(
        f"/api/types/aclUser/instances/{user_id}",
        json={"user_name": "updateduser"},
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()["entries"][0]["content"]
    assert content["user_name"] == "updateduser"

    # Lookup SID
    response = test_client.get(
        "/api/types/aclUser/action/lookupSIDByDomainUser",
        params={"domain_name": "WORKGROUP", "user_name": "updateduser"},
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()["entries"][0]["content"]
    assert content["sid"] == "S-1-5-21-1234567890-1234567890-1234567890-1234"
