from unittest.mock import Mock

import pytest
from fastapi import HTTPException, Request

from dell_unisphere_mock_api.controllers.tenant_controller import TenantController
from dell_unisphere_mock_api.models.tenant import TenantCreate, TenantUpdate


@pytest.fixture
def tenant_controller():
    return TenantController()


@pytest.fixture
def mock_request():
    request = Mock(spec=Request)
    request.base_url = "http://test"
    return request


@pytest.fixture
def sample_tenant_data():
    return {
        "name": "test_tenant",
        "description": "Test tenant",
        "vlans": [100, 200],
        "networks": ["192.168.1.0/24", "10.0.0.0/24"],
        "is_enabled": True,
    }


@pytest.mark.asyncio
async def test_create_tenant(tenant_controller, mock_request, sample_tenant_data):
    tenant_data = TenantCreate(**sample_tenant_data)
    response = await tenant_controller.create_tenant(mock_request, tenant_data)
    response_dict = response.model_dump()

    assert response_dict["base"] == "http://test/api/types/tenant/instances"
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["name"] == sample_tenant_data["name"]
    assert content["description"] == sample_tenant_data["description"]
    assert content["vlans"] == sample_tenant_data["vlans"]
    assert content["networks"] == sample_tenant_data["networks"]


@pytest.mark.asyncio
async def test_get_tenant(tenant_controller, mock_request, sample_tenant_data):
    # First create a tenant
    tenant_data = TenantCreate(**sample_tenant_data)
    created = await tenant_controller.create_tenant(mock_request, tenant_data)
    created_dict = created.model_dump()
    tenant_id = created_dict["entries"][0]["content"]["id"]

    # Then get it
    response = await tenant_controller.get_tenant(mock_request, tenant_id)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["name"] == sample_tenant_data["name"]
    assert content["description"] == sample_tenant_data["description"]


@pytest.mark.asyncio
async def test_get_tenant_by_name(tenant_controller, mock_request, sample_tenant_data):
    # First create a tenant
    tenant_data = TenantCreate(**sample_tenant_data)
    await tenant_controller.create_tenant(mock_request, tenant_data)

    # Then get it by name
    response = await tenant_controller.get_tenant_by_name(mock_request, sample_tenant_data["name"])
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["name"] == sample_tenant_data["name"]
    assert content["description"] == sample_tenant_data["description"]


@pytest.mark.asyncio
async def test_list_tenants(tenant_controller, mock_request, sample_tenant_data):
    # Create a tenant first
    tenant_data = TenantCreate(**sample_tenant_data)
    created_response = await tenant_controller.create_tenant(mock_request, tenant_data)
    created_dict = created_response.model_dump()
    created_id = created_dict["entries"][0]["content"]["id"]
    created_name = created_dict["entries"][0]["content"]["name"]

    # List all tenants
    response = await tenant_controller.list_tenants(mock_request)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) > 0
    content = response_dict["entries"][0]["content"]
    assert content["id"] == created_id
    assert content["name"] == created_name


@pytest.mark.asyncio
async def test_update_tenant(tenant_controller, mock_request, sample_tenant_data):
    # First create a tenant
    tenant_data = TenantCreate(**sample_tenant_data)
    created = await tenant_controller.create_tenant(mock_request, tenant_data)
    created_dict = created.model_dump()
    tenant_id = created_dict["entries"][0]["content"]["id"]

    # Update it
    update_data = TenantUpdate(description="Updated description", vlans=[300, 400])
    response = await tenant_controller.update_tenant(mock_request, tenant_id, update_data)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 1
    content = response_dict["entries"][0]["content"]
    assert content["description"] == "Updated description"
    assert content["vlans"] == [300, 400]


@pytest.mark.asyncio
async def test_update_tenant_name(tenant_controller, mock_request, sample_tenant_data):
    # First create a tenant
    tenant_data = TenantCreate(**sample_tenant_data)
    created = await tenant_controller.create_tenant(mock_request, tenant_data)
    created_dict = created.model_dump()
    tenant_id = created_dict["entries"][0]["content"]["id"]

    # Update its name
    new_name = "updated_tenant"
    update_data = TenantUpdate(name=new_name)
    response = await tenant_controller.update_tenant(mock_request, tenant_id, update_data)
    response_dict = response.model_dump()
    content = response_dict["entries"][0]["content"]
    assert content["name"] == new_name

    # Verify we can get it by the new name
    response = await tenant_controller.get_tenant_by_name(mock_request, new_name)
    response_dict = response.model_dump()
    content = response_dict["entries"][0]["content"]
    assert content["name"] == new_name


@pytest.mark.asyncio
async def test_delete_tenant(tenant_controller, mock_request, sample_tenant_data):
    # First create a tenant
    tenant_data = TenantCreate(**sample_tenant_data)
    created = await tenant_controller.create_tenant(mock_request, tenant_data)
    created_dict = created.model_dump()
    tenant_id = created_dict["entries"][0]["content"]["id"]

    # Delete it
    response = await tenant_controller.delete_tenant(mock_request, tenant_id)
    response_dict = response.model_dump()
    assert len(response_dict["entries"]) == 0

    # Verify it's deleted
    with pytest.raises(HTTPException) as exc_info:
        await tenant_controller.get_tenant(mock_request, tenant_id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_tenant(tenant_controller, mock_request):
    with pytest.raises(HTTPException) as exc_info:
        await tenant_controller.get_tenant(mock_request, "nonexistent-id")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_tenant_by_name(tenant_controller, mock_request):
    with pytest.raises(HTTPException) as exc_info:
        await tenant_controller.get_tenant_by_name(mock_request, "nonexistent-name")
    assert exc_info.value.status_code == 404
