import pytest
from fastapi import HTTPException

from dell_unisphere_mock_api.controllers.storage_resource_controller import StorageResourceController
from dell_unisphere_mock_api.schemas.storage_resource import StorageResourceCreate, StorageResourceUpdate


@pytest.fixture
def storage_resource_controller():
    return StorageResourceController()


@pytest.fixture
def mock_request(mocker):
    mock = mocker.Mock()
    mock.base_url = "http://testserver"
    mock.url = mocker.Mock()
    mock.url.path = "/api/types/storageResource/instances"
    return mock


@pytest.fixture
def sample_resource_data():
    return {
        "name": "test_resource",
        "description": "Test storage resource",
        "type": "LUN",
        "pool": "pool_1",
        "size": 1024 * 1024 * 1024,  # 1GB
        "isThinEnabled": True,
        "isCompressionEnabled": True,
        "isAdvancedDedupEnabled": True,
        "tieringPolicy": "Autotier",
        "hostAccess": [],
        "snapCount": 0,
        "tierUsage": {},
    }


@pytest.mark.asyncio
async def test_create_storage_resource(storage_resource_controller, mock_request, sample_resource_data):
    # Create resource
    resource_data = StorageResourceCreate(**sample_resource_data)
    response = await storage_resource_controller.create_storage_resource(mock_request, resource_data)

    # Verify response format
    assert len(response.entries) == 1
    entry = response.entries[0]

    # Verify content
    content = entry.content
    assert content.name == sample_resource_data["name"]
    assert content.description == sample_resource_data["description"]
    assert content.type == sample_resource_data["type"]
    assert content.pool == sample_resource_data["pool"]
    assert content.isCompressionEnabled == sample_resource_data["isCompressionEnabled"]
    assert content.isAdvancedDedupEnabled == sample_resource_data["isAdvancedDedupEnabled"]

    # Verify links
    assert entry.links
    assert any(link.rel == "self" for link in entry.links)


@pytest.mark.asyncio
async def test_get_storage_resource(storage_resource_controller, mock_request, sample_resource_data):
    # First create a resource
    resource_data = StorageResourceCreate(**sample_resource_data)
    created = await storage_resource_controller.create_storage_resource(mock_request, resource_data)
    resource_id = created.entries[0].content.id

    # Get the resource
    response = await storage_resource_controller.get_storage_resource(mock_request, resource_id)

    # Verify response format
    assert len(response.entries) == 1
    entry = response.entries[0]

    # Verify content
    content = entry.content
    assert content.id == resource_id
    assert content.name == sample_resource_data["name"]

    # Verify links
    assert entry.links
    assert any(link.rel == "self" for link in entry.links)


@pytest.mark.asyncio
async def test_list_storage_resources(storage_resource_controller, mock_request, sample_resource_data):
    # Create multiple resources
    resource_data1 = StorageResourceCreate(**sample_resource_data)
    resource_data2 = StorageResourceCreate(**{**sample_resource_data, "name": "test_resource_2"})

    await storage_resource_controller.create_storage_resource(mock_request, resource_data1)
    await storage_resource_controller.create_storage_resource(mock_request, resource_data2)

    # List resources
    response = await storage_resource_controller.list_storage_resources(mock_request)

    # Verify response format
    assert len(response.entries) == 2

    # Verify each entry has correct format and links
    for entry in response.entries:
        assert entry.content
        assert entry.links
        assert any(link.rel == "self" for link in entry.links)


@pytest.mark.asyncio
async def test_update_storage_resource(storage_resource_controller, mock_request, sample_resource_data):
    # First create a resource
    resource_data = StorageResourceCreate(**sample_resource_data)
    created = await storage_resource_controller.create_storage_resource(mock_request, resource_data)
    resource_id = created.entries[0].content.id

    # Update the resource
    update_data = StorageResourceUpdate(name="updated_name", description="Updated description")
    response = await storage_resource_controller.update_storage_resource(mock_request, resource_id, update_data)

    # Verify response format
    assert len(response.entries) == 1
    entry = response.entries[0]

    # Verify content was updated
    content = entry.content
    assert content.id == resource_id
    assert content.name == "updated_name"
    assert content.description == "Updated description"

    # Verify links
    assert entry.links
    assert any(link.rel == "self" for link in entry.links)


@pytest.mark.asyncio
async def test_delete_storage_resource(storage_resource_controller, mock_request, sample_resource_data):
    # First create a resource
    resource_data = StorageResourceCreate(**sample_resource_data)
    created = await storage_resource_controller.create_storage_resource(mock_request, resource_data)
    resource_id = created.entries[0].content.id

    # Delete should not raise any exceptions
    await storage_resource_controller.delete_storage_resource(mock_request, resource_id)

    # Verify resource is deleted
    with pytest.raises(HTTPException) as exc_info:
        await storage_resource_controller.get_storage_resource(mock_request, resource_id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_host_access_operations(storage_resource_controller, mock_request, sample_resource_data):
    # First create a resource
    resource_data = StorageResourceCreate(**sample_resource_data)
    created = await storage_resource_controller.create_storage_resource(mock_request, resource_data)
    resource_id = created.entries[0].content.id

    # Add host access
    response = await storage_resource_controller.add_host_access(mock_request, resource_id, "host_1", "READ_WRITE")
    content = response.entries[0].content
    assert "host_1" in [access["host"] for access in content.hostAccess]

    # Update host access
    response = await storage_resource_controller.update_host_access(mock_request, resource_id, "host_1", "READ_ONLY")
    content = response.entries[0].content
    assert any(access["host"] == "host_1" and access["accessType"] == "READ_ONLY" for access in content.hostAccess)

    # Remove host access
    response = await storage_resource_controller.remove_host_access(mock_request, resource_id, "host_1")
    content = response.entries[0].content
    assert "host_1" not in [access["host"] for access in content.hostAccess]


@pytest.mark.asyncio
async def test_update_usage_stats(storage_resource_controller, mock_request, sample_resource_data):
    # First create a resource
    resource_data = StorageResourceCreate(**sample_resource_data)
    created = await storage_resource_controller.create_storage_resource(mock_request, resource_data)
    resource_id = created.entries[0].content.id

    # Update usage stats
    size_used = 512 * 1024 * 1024  # 512MB
    tier_usage = {"PERFORMANCE": 256 * 1024 * 1024, "CAPACITY": 256 * 1024 * 1024}

    response = await storage_resource_controller.update_usage_stats(mock_request, resource_id, size_used, tier_usage)

    # Verify response format
    assert len(response.entries) == 1
    content = response.entries[0].content

    # Verify stats were updated
    assert content.sizeUsed == size_used
    assert content.perTierSizeUsed == tier_usage
