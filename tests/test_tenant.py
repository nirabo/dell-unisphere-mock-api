from fastapi.testclient import TestClient

from dell_unisphere_mock_api.controllers.tenant_controller import TenantController
from dell_unisphere_mock_api.models.tenant import TenantCreate, TenantUpdate


def test_tenant_controller_create():
    """Test creating a tenant."""
    controller = TenantController()
    tenant_data = TenantCreate(
        name="TestTenant",
        vlans=[1, 100, 200],
    )

    tenant = controller.create_tenant(tenant_data)
    assert tenant.name == "TestTenant"
    assert tenant.vlans == [1, 100, 200]
    assert tenant.hosts == []


def test_tenant_controller_get():
    """Test retrieving a tenant."""
    controller = TenantController()
    tenant_data = TenantCreate(
        name="TestTenant",
        vlans=[1, 100, 200],
    )

    created_tenant = controller.create_tenant(tenant_data)
    retrieved_tenant = controller.get_tenant(created_tenant.id)

    assert retrieved_tenant is not None
    assert retrieved_tenant.id == created_tenant.id
    assert retrieved_tenant.name == "TestTenant"
    assert retrieved_tenant.vlans == [1, 100, 200]


def test_tenant_controller_update():
    """Test updating a tenant."""
    controller = TenantController()
    tenant_data = TenantCreate(
        name="TestTenant",
        vlans=[1, 100, 200],
    )

    created_tenant = controller.create_tenant(tenant_data)
    update_data = TenantUpdate(name="UpdatedTenant", vlans=[1, 300, 400])
    updated_tenant = controller.update_tenant(created_tenant.id, update_data)

    assert updated_tenant is not None
    assert updated_tenant.name == "UpdatedTenant"
    assert updated_tenant.vlans == [1, 300, 400]


def test_tenant_controller_get_by_name():
    """Test retrieving a tenant by name."""
    controller = TenantController()
    tenant_data = TenantCreate(
        name="TestTenant",
        vlans=[1, 100, 200],
    )

    created_tenant = controller.create_tenant(tenant_data)
    retrieved_tenant = controller.get_tenant_by_name("TestTenant")

    assert retrieved_tenant is not None
    assert retrieved_tenant.id == created_tenant.id
    assert retrieved_tenant.name == "TestTenant"
    assert retrieved_tenant.vlans == [1, 100, 200]


def test_tenant_api_endpoints(test_client: TestClient, auth_headers):
    """Test tenant API endpoints."""
    headers, _ = auth_headers

    # Create
    response = test_client.post(
        "/api/types/tenant/instances",
        json={
            "name": "TestTenant",
            "vlans": [1, 100, 200],
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    tenant_id = data["entries"][0]["content"]["id"]
    assert data["entries"][0]["content"]["name"] == "TestTenant"

    # Get by ID
    response = test_client.get(f"/api/types/tenant/instances/{tenant_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["entries"][0]["content"]["name"] == "TestTenant"

    # Get by name
    response = test_client.get("/api/types/tenant/instances/name:TestTenant", headers=headers)
    assert response.status_code == 200
    assert response.json()["entries"][0]["content"]["name"] == "TestTenant"

    # Modify by ID
    response = test_client.post(
        f"/api/types/tenant/instances/{tenant_id}/action/modify",
        json={"name": "UpdatedTenant", "vlans": [1, 300, 400]},
        headers=headers,
    )
    assert response.status_code == 204

    # Verify modification
    response = test_client.get(f"/api/types/tenant/instances/{tenant_id}", headers=headers)
    assert response.status_code == 200
    content = response.json()["entries"][0]["content"]
    assert content["name"] == "UpdatedTenant"
    assert content["vlans"] == [1, 300, 400]

    # Delete
    response = test_client.delete(f"/api/types/tenant/instances/{tenant_id}", headers=headers)
    assert response.status_code == 200

    # Verify deletion
    response = test_client.get(f"/api/types/tenant/instances/{tenant_id}", headers=headers)
    assert response.status_code == 404
