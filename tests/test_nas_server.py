import pytest


class TestNasServer:
    def setup_method(self):
        """Setup method that runs before each test."""
        self.last_created_nas = None

    @pytest.fixture
    def sample_nas_server_data(self):
        return {
            "name": "test-nas",
            "description": "Test NAS Server",
            "homeSP": "SP_A",
            "pool": "pool_1",
            "isReplicationDestination": False,
            "defaultUnixUser": "root",
            "defaultWindowsUser": "Administrator",
            "isMultiProtocolEnabled": True,
            "dns_config": {
                "domain": "example.com",
                "addresses": ["192.168.1.1", "192.168.1.2"],
                "search_domains": ["example.com", "test.com"],
            },
            "network_interfaces": [
                {
                    "id": "if_1",
                    "name": "eth0",
                    "ip_address": "192.168.1.10",
                    "netmask": "255.255.255.0",
                    "gateway": "192.168.1.1",
                    "interface_type": "Production",
                    "vlan_id": 100,
                }
            ],
            "user_mapping": {
                "unix_enabled": True,
                "windows_enabled": True,
                "ldap_enabled": True,
                "ldap_server": "ldap.example.com",
                "ldap_base_dn": "dc=example,dc=com",
                "kerberos_enabled": True,
                "kerberos_realm": "EXAMPLE.COM",
            },
            "authentication_type": "Kerberos",
        }

    def test_create_nas_server(self, test_client, auth_headers, sample_nas_server_data):
        headers, _ = auth_headers
        response = test_client.post("/api/types/nasServer/instances", json=sample_nas_server_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_nas_server_data["name"]
        assert "id" in data
        assert data["health"] == "OK"
        assert "NFSv3" in data["protocols"]
        assert "CIFS" in data["protocols"]
        self.last_created_nas = data

    def test_create_nas_server_unauthorized(self, test_client):
        # No auth headers = unauthorized
        response = test_client.post("/api/types/nasServer/instances", json={})
        assert response.status_code == 401

    def test_get_nas_server_by_id(self, test_client, auth_headers, sample_nas_server_data):
        headers, _ = auth_headers
        # First create a NAS server
        self.test_create_nas_server(test_client, auth_headers, sample_nas_server_data)
        assert self.last_created_nas is not None

        # Then get it by ID
        response = test_client.get(f"/api/instances/nasServer/{self.last_created_nas['id']}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.last_created_nas["id"]
        assert data["name"] == sample_nas_server_data["name"]

    def test_get_nas_server_by_name(self, test_client, auth_headers, sample_nas_server_data):
        headers, _ = auth_headers
        # First create a NAS server
        self.test_create_nas_server(test_client, auth_headers, sample_nas_server_data)
        assert self.last_created_nas is not None

        # Then get it by name
        response = test_client.get(
            f"/api/types/nasServer/instances/name:{sample_nas_server_data['name']}", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_nas_server_data["name"]

    def test_generate_user_mappings_report(self, test_client, auth_headers, sample_nas_server_data):
        headers, _ = auth_headers
        # First create a NAS server
        self.test_create_nas_server(test_client, auth_headers, sample_nas_server_data)
        assert self.last_created_nas is not None

        # Generate user mappings report
        response = test_client.post(
            f"/api/instances/nasServer/{self.last_created_nas['id']}/action/generateUserMappingsReport", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nas_server_id"] == self.last_created_nas["id"]
        assert "mappings" in data
        assert "unix_users" in data["mappings"]
        assert "windows_users" in data["mappings"]

    def test_update_user_mappings(self, test_client, auth_headers, sample_nas_server_data):
        headers, _ = auth_headers
        # First create a NAS server
        self.test_create_nas_server(test_client, auth_headers, sample_nas_server_data)
        assert self.last_created_nas is not None

        # Update user mappings
        new_mapping = {
            "unix_enabled": True,
            "windows_enabled": True,
            "ldap_enabled": True,
            "ldap_server": "new-ldap.example.com",
            "ldap_base_dn": "dc=new,dc=example,dc=com",
            "kerberos_enabled": True,
            "kerberos_realm": "NEW.EXAMPLE.COM",
        }
        response = test_client.post(
            f"/api/instances/nasServer/{self.last_created_nas['id']}/action/updateUserMappings",
            json=new_mapping,
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_mapping"]["ldap_server"] == new_mapping["ldap_server"]

    def test_ping_from_nas(self, test_client, auth_headers, sample_nas_server_data):
        headers, _ = auth_headers
        # First create a NAS server
        self.test_create_nas_server(test_client, auth_headers, sample_nas_server_data)
        assert self.last_created_nas is not None

        # Perform ping
        ping_request = {"address": "192.168.1.1", "count": 4, "timeout": 5, "size": 64}
        response = test_client.post(
            f"/api/instances/nasServer/{self.last_created_nas['id']}/action/ping", json=ping_request, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["address"] == ping_request["address"]
        assert data["packets_transmitted"] == ping_request["count"]
        assert "results" in data
        assert len(data["results"]) == ping_request["count"]

    def test_traceroute_from_nas(self, test_client, auth_headers, sample_nas_server_data):
        headers, _ = auth_headers
        # First create a NAS server
        self.test_create_nas_server(test_client, auth_headers, sample_nas_server_data)
        assert self.last_created_nas is not None

        # Perform traceroute
        traceroute_request = {"address": "192.168.1.1", "timeout": 5, "max_hops": 10}
        response = test_client.post(
            f"/api/instances/nasServer/{self.last_created_nas['id']}/action/traceroute",
            json=traceroute_request,
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["destination"] == traceroute_request["address"]
        assert "hops" in data
        assert len(data["hops"]) <= traceroute_request["max_hops"]

    def test_refresh_configuration(self, test_client, auth_headers, sample_nas_server_data):
        headers, _ = auth_headers
        # First create a NAS server
        self.test_create_nas_server(test_client, auth_headers, sample_nas_server_data)
        assert self.last_created_nas is not None

        # Refresh configuration
        response = test_client.post(
            f"/api/instances/nasServer/{self.last_created_nas['id']}/action/refreshConfiguration", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["configuration_status"] == "OK"

    # TODO: Fix FastAPI routing conflict for name-based deletion
    # def test_delete_nas_server_by_name(self, test_client, auth_headers, sample_nas_server_data):
    #     headers, _ = auth_headers
    #     # First create a NAS server
    #     self.test_create_nas_server(test_client, auth_headers, sample_nas_server_data)
    #     assert self.last_created_nas is not None
    #
    #     # Delete by name
    #     response = test_client.delete(
    #         f"/api/types/nasServer/instances/name:{sample_nas_server_data['name']}",
    #         headers=headers
    #     )
    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["message"] == "NAS server deleted successfully"
    #
    #     # Verify it's deleted
    #     response = test_client.get(
    #         f"/api/types/nasServer/instances/name:{sample_nas_server_data['name']}",
    #         headers=headers
    #     )
    #     assert response.status_code == 404
