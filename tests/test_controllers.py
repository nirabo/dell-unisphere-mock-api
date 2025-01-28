import pytest
from fastapi import HTTPException

from dell_unisphere_mock_api.controllers.filesystem_controller import FilesystemController
from dell_unisphere_mock_api.controllers.nas_server_controller import NasServerController
from dell_unisphere_mock_api.controllers.storage_resource_controller import StorageResourceController
from dell_unisphere_mock_api.schemas.filesystem import FilesystemCreate
from dell_unisphere_mock_api.schemas.nas_server import NasServerCreate
from dell_unisphere_mock_api.schemas.storage_resource import StorageResourceCreate, StorageResourceUpdate


class TestStorageResourceController:
    @pytest.fixture
    def controller(self):
        return StorageResourceController()

    @pytest.fixture
    def mock_request(self):
        class MockRequest:
            def __init__(self):
                self.base_url = "http://testserver"
                self.path = "/test"
                self.url = type("URL", (), {"path": "/test"})()

        return MockRequest()

    @pytest.fixture
    def sample_resource_data(self):
        return StorageResourceCreate(
            name="test_resource",
            description="Test storage resource",
            type="LUN",
            pool="pool_1",
            isThinEnabled=True,
            isCompressionEnabled=False,
            isAdvancedDedupEnabled=False,
            sizeTotal=1024 * 1024 * 1024 * 100,  # 100GB
        )

    @pytest.mark.asyncio
    async def test_create_storage_resource(self, controller, mock_request, sample_resource_data):
        response = await controller.create_storage_resource(mock_request, sample_resource_data)
        resource = response.entries[0].content
        assert resource.name == sample_resource_data.name
        assert resource.type == sample_resource_data.type
        assert resource.health == "OK"

    @pytest.mark.asyncio
    async def test_get_storage_resource(self, controller, mock_request, sample_resource_data):
        created_response = await controller.create_storage_resource(mock_request, sample_resource_data)
        created = created_response.entries[0].content
        retrieved_response = await controller.get_storage_resource(mock_request, created.id)
        retrieved = retrieved_response.entries[0].content
        assert retrieved == created

    @pytest.mark.asyncio
    async def test_list_storage_resources(self, controller, mock_request, sample_resource_data):
        await controller.create_storage_resource(mock_request, sample_resource_data)
        response = await controller.list_storage_resources(mock_request)
        assert len(response.entries) == 1
        assert response.entries[0].content.name == sample_resource_data.name

    @pytest.mark.asyncio
    async def test_update_storage_resource(self, controller, mock_request, sample_resource_data):
        created_response = await controller.create_storage_resource(mock_request, sample_resource_data)
        created = created_response.entries[0].content
        update_data = StorageResourceUpdate(description="Updated description", isCompressionEnabled=True)
        updated_response = await controller.update_storage_resource(mock_request, created.id, update_data)
        updated = updated_response.entries[0].content
        assert updated.description == update_data.description
        assert updated.isCompressionEnabled == update_data.isCompressionEnabled

    @pytest.mark.asyncio
    async def test_delete_storage_resource(self, controller, mock_request, sample_resource_data):
        created_response = await controller.create_storage_resource(mock_request, sample_resource_data)
        created = created_response.entries[0].content
        await controller.delete_storage_resource(mock_request, created.id)
        with pytest.raises(HTTPException) as exc_info:
            await controller.get_storage_resource(mock_request, created.id)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_host_access_management(self, controller, mock_request, sample_resource_data):
        created_response = await controller.create_storage_resource(mock_request, sample_resource_data)
        created = created_response.entries[0].content

        # Add host access
        updated_response = await controller.add_host_access(mock_request, created.id, "host1", "READ_WRITE")
        updated = updated_response.entries[0].content

        # Verify host access was added
        retrieved_response = await controller.get_storage_resource(mock_request, created.id)
        retrieved = retrieved_response.entries[0].content
        assert len(retrieved.hostAccess) == 1
        assert retrieved.hostAccess[0]["host"] == "host1"
        assert retrieved.hostAccess[0]["accessType"] == "READ_WRITE"

        # Remove host access
        removed_response = await controller.remove_host_access(mock_request, created.id, "host1")
        removed = removed_response.entries[0].content

        # Verify host access was removed
        retrieved_response = await controller.get_storage_resource(mock_request, created.id)
        retrieved = retrieved_response.entries[0].content
        assert len(retrieved.hostAccess) == 0


class TestFilesystemController:
    @pytest.fixture
    def controller(self):
        return FilesystemController()

    @pytest.fixture
    def mock_request(self):
        class MockRequest:
            def __init__(self):
                self.base_url = "http://testserver"
                self.path = "/test"
                self.url = type("URL", (), {"path": "/test"})()

        return MockRequest()

    @pytest.fixture
    def sample_filesystem_data(self):
        return FilesystemCreate(
            name="test_fs",
            description="Test filesystem",
            nasServer="nas1",
            pool="pool_1",
            size=1024 * 1024 * 1024 * 100,  # 100GB
            isThinEnabled=True,
            supportedProtocols=["NFS", "CIFS"],
            isCacheEnabled=True,
            isCompressionEnabled=False,
            isAdvancedDedupEnabled=False,
            isDataReductionEnabled=False,
        )

    @pytest.mark.asyncio
    async def test_create_filesystem(self, controller, mock_request, sample_filesystem_data):
        response = await controller.create_filesystem(request=mock_request, filesystem_data=sample_filesystem_data)
        fs = response.entries[0].content
        assert fs.name == sample_filesystem_data.name
        assert fs.size == sample_filesystem_data.size
        assert fs.health == "OK"

    @pytest.mark.asyncio
    async def test_get_filesystem(self, controller, mock_request, sample_filesystem_data):
        created_response = await controller.create_filesystem(
            request=mock_request, filesystem_data=sample_filesystem_data
        )
        created = created_response.entries[0].content
        retrieved_response = await controller.get_filesystem(request=mock_request, filesystem_id=created.id)
        retrieved = retrieved_response.entries[0].content
        assert retrieved == created


class TestNasServerController:
    @pytest.fixture
    def controller(self):
        return NasServerController()

    @pytest.fixture
    def mock_request(self):
        class MockRequest:
            def __init__(self):
                self.base_url = "http://testserver"
                self.path = "/test"
                self.url = type("URL", (), {"path": "/test"})()

        return MockRequest()

    @pytest.fixture
    def sample_nas_data(self):
        return NasServerCreate(
            name="test_nas",
            description="Test NAS server",
            homeSP="spa",
            pool="pool_1",
            isMultiProtocolEnabled=False,
            isReplicationDestination=False,
            defaultUnixUser="root",
            defaultWindowsUser="Administrator",
            currentUnixDirectory=None,
            dns_config=None,
            network_interfaces=[],
            user_mapping=None,
            authentication_type="None",
        )

    @pytest.mark.asyncio
    async def test_create_nas_server(self, controller, mock_request, sample_nas_data):
        response = await controller.create_nas_server(request=mock_request, nas_server_data=sample_nas_data)
        nas = response.entries[0].content
        assert nas.name == sample_nas_data.name
        assert nas.health == "OK"

    @pytest.mark.asyncio
    async def test_get_nas_server(self, controller, mock_request, sample_nas_data):
        created_response = await controller.create_nas_server(request=mock_request, nas_server_data=sample_nas_data)
        created = created_response.entries[0].content
        retrieved_response = await controller.get_nas_server(request=mock_request, nas_server_id=created.id)
        retrieved = retrieved_response.entries[0].content
        assert retrieved == created
