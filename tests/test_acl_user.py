from fastapi.testclient import TestClient

from dell_unisphere_mock_api.controllers.acl_user_controller import ACLUserController
from dell_unisphere_mock_api.models.acl_user import ACLUserCreate, ACLUserUpdate


def test_acl_user_controller_create():
    """Test creating an ACL user."""
    controller = ACLUserController()
    user_data = ACLUserCreate(
        sid="S-1-5-21-1234567890-1234567890-1234567890-1234",
        domain_name="WORKGROUP",
        user_name="testuser",
    )

    user = controller.create_user(user_data)
    assert user.sid == "S-1-5-21-1234567890-1234567890-1234567890-1234"
    assert user.domain_name == "WORKGROUP"
    assert user.user_name == "testuser"


def test_acl_user_controller_get():
    """Test retrieving an ACL user."""
    controller = ACLUserController()
    user_data = ACLUserCreate(
        sid="S-1-5-21-1234567890-1234567890-1234567890-1234",
        domain_name="WORKGROUP",
        user_name="testuser",
    )

    created_user = controller.create_user(user_data)
    retrieved_user = controller.get_user(created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.sid == "S-1-5-21-1234567890-1234567890-1234567890-1234"
    assert retrieved_user.domain_name == "WORKGROUP"
    assert retrieved_user.user_name == "testuser"


def test_acl_user_controller_update():
    """Test updating an ACL user."""
    controller = ACLUserController()
    user_data = ACLUserCreate(
        sid="S-1-5-21-1234567890-1234567890-1234567890-1234",
        domain_name="WORKGROUP",
        user_name="testuser",
    )

    created_user = controller.create_user(user_data)
    update_data = ACLUserUpdate(user_name="updateduser")
    updated_user = controller.update_user(created_user.id, update_data)

    assert updated_user is not None
    assert updated_user.user_name == "updateduser"
    assert updated_user.sid == "S-1-5-21-1234567890-1234567890-1234567890-1234"
    assert updated_user.domain_name == "WORKGROUP"


def test_acl_user_controller_lookup_sid():
    """Test looking up a user's SID by domain name and username."""
    controller = ACLUserController()
    user_data = ACLUserCreate(
        sid="S-1-5-21-1234567890-1234567890-1234567890-1234",
        domain_name="WORKGROUP",
        user_name="testuser",
    )

    controller.create_user(user_data)
    result = controller.lookup_sid_by_domain_user("WORKGROUP", "testuser")

    assert result is not None
    sid, user = result
    assert sid == "S-1-5-21-1234567890-1234567890-1234567890-1234"
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
