import base64

import pytest
from fastapi.testclient import TestClient

from dell_unisphere_mock_api.main import app


class TestTutorial52:
    def setup_method(self):
        self.client = TestClient(app)
        # Create Basic Auth header
        credentials = base64.b64encode(b"admin:Password123!").decode("utf-8")
        auth_header = f"Basic {credentials}"

        # Login to get the cookie and CSRF token
        response = self.client.post(
            "/api/auth",
            headers={"X-EMC-REST-CLIENT": "true", "Authorization": auth_header},
        )
        assert response.status_code == 200
        self.csrf_token = response.headers.get("EMC-CSRF-TOKEN")
        self.cookies = response.cookies
        self.auth_header = auth_header

    def test_get_pools_basic(self):
        """Test the basic pool query from the tutorial"""
        response = self.client.get(
            "/api/types/pool/instances",
            params={"compact": "True", "fields": "id,name"},
            headers={
                "X-EMC-REST-CLIENT": "true",
                "EMC-CSRF-TOKEN": self.csrf_token,
                "Authorization": self.auth_header,
            },
            cookies=self.cookies,
        )
        assert response.status_code == 200
        data = response.json()
        assert "@base" in data
        assert "entries" in data
        # Verify the structure matches tutorial example
        for entry in data["entries"]:
            assert "content" in entry
            assert "id" in entry["content"]
            assert "name" in entry["content"]

    def test_get_pools_with_pagination(self):
        """Test pool query with pagination parameters"""
        response = self.client.get(
            "/api/types/pool/instances",
            params={"page": 1, "per_page": 2, "fields": "id,name"},
            headers={
                "X-EMC-REST-CLIENT": "true",
                "EMC-CSRF-TOKEN": self.csrf_token,
                "Authorization": self.auth_header,
            },
            cookies=self.cookies,
        )
        assert response.status_code == 200
        data = response.json()
        assert "@base" in data
        assert "entries" in data
        # Verify pagination info
        assert len(data["entries"]) <= 2  # Should respect per_page parameter

    def test_get_pools_with_sorting(self):
        """Test pool query with sorting"""
        response = self.client.get(
            "/api/types/pool/instances",
            params={"orderby": "name desc", "fields": "id,name"},
            headers={
                "X-EMC-REST-CLIENT": "true",
                "EMC-CSRF-TOKEN": self.csrf_token,
                "Authorization": self.auth_header,
            },
            cookies=self.cookies,
        )
        assert response.status_code == 200
        data = response.json()
        # Verify sorting - names should be in descending order
        names = [entry["content"]["name"] for entry in data["entries"]]
        assert names == sorted(names, reverse=True)

    def test_async_request(self):
        """Test making an asynchronous request"""
        # Create a pool in async mode
        pool_data = {"name": "async_test_pool", "type": 1, "sizeTotal": 1000000000}
        response = self.client.post(
            "/api/types/pool/instances?timeout=0",
            json=pool_data,
            headers={
                "X-EMC-REST-CLIENT": "true",
                "EMC-CSRF-TOKEN": self.csrf_token,
                "Authorization": self.auth_header,
            },
            cookies=self.cookies,
        )
        assert response.status_code == 202
        job_id = response.json()["id"]

        # Check job status
        response = self.client.get(
            f"/api/instances/job/{job_id}",
            headers={
                "X-EMC-REST-CLIENT": "true",
                "EMC-CSRF-TOKEN": self.csrf_token,
                "Authorization": self.auth_header,
            },
            cookies=self.cookies,
        )
        assert response.status_code == 200
        assert "state" in response.json()

    def test_aggregated_request(self):
        """Test making an aggregated request"""
        # Create aggregated job data
        job_data = {
            "description": "Test aggregated job",
            "tasks": [
                {
                    "name": "CreatePool",
                    "object": "pool",
                    "action": "create",
                    "parametersIn": {"name": "aggregated_pool", "type": 1, "sizeTotal": 1000000000},
                },
                {
                    "name": "CreateLUN",
                    "object": "storageResource",
                    "action": "createLun",
                    "parametersIn": {"name": "aggregated_lun", "size": 500000000, "pool": {"id": "@CreatePool.id"}},
                },
            ],
        }

        # Submit aggregated job
        response = self.client.post(
            "/api/types/job/instances?timeout=0",
            json=job_data,
            headers={
                "X-EMC-REST-CLIENT": "true",
                "EMC-CSRF-TOKEN": self.csrf_token,
                "Authorization": self.auth_header,
            },
            cookies=self.cookies,
        )
        assert response.status_code == 202
        job_id = response.json()["id"]

        # Check job status
        response = self.client.get(
            f"/api/instances/job/{job_id}",
            headers={
                "X-EMC-REST-CLIENT": "true",
                "EMC-CSRF-TOKEN": self.csrf_token,
                "Authorization": self.auth_header,
            },
            cookies=self.cookies,
        )
        assert response.status_code == 200
        assert "state" in response.json()
