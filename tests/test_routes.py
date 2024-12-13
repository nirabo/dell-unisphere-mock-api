import pytest
from fastapi.testclient import TestClient
from dell_unisphere_mock_api.main import app

class TestStorageResourceRoutes:
    @pytest.fixture
    def sample_resource_data(self):
        return {
            "name": "test_resource",
            "description": "Test storage resource",
            "type": "LUN",
            "pool": "pool_1",
            "isThinEnabled": True,
            "isCompressionEnabled": False,
            "isAdvancedDedupEnabled": False,
            "sizeTotal": 1024 * 1024 * 1024 * 100  # 100GB
        }

    def test_create_storage_resource(self, test_client, auth_headers, sample_resource_data):
        response = test_client.post(
            "/api/types/storageResource/instances",
            json=sample_resource_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_resource_data["name"]
        assert data["type"] == sample_resource_data["type"]
        assert "id" in data
        return data

    def test_get_storage_resource(self, test_client, auth_headers, sample_resource_data):
        # First create a resource
        resource = self.test_create_storage_resource(test_client, auth_headers, sample_resource_data)
        
        # Then get it
        response = test_client.get(
            f"/api/types/storageResource/instances/{resource['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resource["id"]

    def test_list_storage_resources(self, test_client, auth_headers, sample_resource_data):
        # Create a resource first
        self.test_create_storage_resource(test_client, auth_headers, sample_resource_data)
        
        # List all resources
        response = test_client.get(
            "/api/types/storageResource/instances",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert isinstance(data, list)

    def test_update_storage_resource(self, test_client, auth_headers, sample_resource_data):
        # First create a resource
        resource = self.test_create_storage_resource(test_client, auth_headers, sample_resource_data)
        
        # Update it
        update_data = {
            "description": "Updated description",
            "isCompressionEnabled": True
        }
        response = test_client.patch(
            f"/api/types/storageResource/instances/{resource['id']}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
        assert data["isCompressionEnabled"] == update_data["isCompressionEnabled"]

    def test_delete_storage_resource(self, test_client, auth_headers, sample_resource_data):
        # First create a resource
        resource = self.test_create_storage_resource(test_client, auth_headers, sample_resource_data)
        
        # Delete it
        response = test_client.delete(
            f"/api/types/storageResource/instances/{resource['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify it's gone
        response = test_client.get(
            f"/api/types/storageResource/instances/{resource['id']}",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_host_access_management(self, test_client, auth_headers, sample_resource_data):
        # First create a resource
        resource = self.test_create_storage_resource(test_client, auth_headers, sample_resource_data)
        
        # Modify host access
        host_access = {
            "host": "host1",
            "accessType": "Production"
        }
        response = test_client.post(
            f"/api/types/storageResource/instances/{resource['id']}/action/modifyHostAccess",
            json=host_access,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "hostAccess" in data

    def test_unauthorized_access(self, test_client, sample_resource_data):
        # Try to create without auth
        response = test_client.post(
            "/api/types/storageResource/instances",
            json=sample_resource_data
        )
        assert response.status_code == 401

class TestFilesystemRoutes:
    @pytest.fixture
    def sample_filesystem_data(self):
        return {
            "name": "test_filesystem",
            "description": "Test filesystem",
            "nasServer": "nas_1",
            "size": 1024 * 1024 * 1024 * 100,  # 100GB
            "protocol": "NFS"
        }

    def test_create_filesystem(self, test_client, auth_headers, sample_filesystem_data):
        response = test_client.post(
            "/api/types/filesystem/instances",
            json=sample_filesystem_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_filesystem_data["name"]
        assert "id" in data
        return data

    def test_get_filesystem(self, test_client, auth_headers, sample_filesystem_data):
        # First create a filesystem
        filesystem = self.test_create_filesystem(test_client, auth_headers, sample_filesystem_data)
        
        # Then get it
        response = test_client.get(
            f"/api/instances/filesystem/{filesystem['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == filesystem["id"]

class TestNasServerRoutes:
    @pytest.fixture
    def sample_nas_data(self):
        return {
            "name": "test_nas",
            "description": "Test NAS server",
            "pool": "pool_1",
            "currentUnixDirectoryService": "None",
            "isMultiprotocolEnabled": False,
            "currentPreferredIPv4Interface": None
        }

    def test_create_nas_server(self, test_client, auth_headers, sample_nas_data):
        response = test_client.post(
            "/api/types/nasServer/instances",
            json=sample_nas_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_nas_data["name"]
        assert "id" in data
        return data

    def test_get_nas_server(self, test_client, auth_headers, sample_nas_data):
        # First create a NAS server
        nas_server = self.test_create_nas_server(test_client, auth_headers, sample_nas_data)
        
        # Then get it
        response = test_client.get(
            f"/api/instances/nasServer/{nas_server['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == nas_server["id"]
